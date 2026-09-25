"""
Writes a journal line after every question and every answer, without the agent having to
remember it, and pushes the journals right away.

Why: when logging depends on the model calling note.py itself, conversations get lost. And
sessions are only saved at SessionEnd, while Remote Control sessions hardly ever end. This makes
the logging independent of the model.

Calls:
  Claude Code, UserPromptSubmit and Stop hooks (JSON on stdin):
      python tools/auto_journal.py
  Codex, notify (JSON as the last argument). An existing notify program is chained first, so
  whatever you already had there keeps working:
      python tools/auto_journal.py --codex [original program and arguments...] <json>
  Background sync (the script starts this itself):
      python tools/auto_journal.py --sync

Never fails hard: every error is swallowed and written to .auto-journal/errors.log, so a session
never gets stuck on it.
"""
import contextlib
import datetime
import io
import json
import os
import re
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "tools"))
import note  # noqa: E402

STATE = os.path.join(BASE, ".auto-journal")
SYNC_STAMP = os.path.join(STATE, "last-sync")
LAST_LINE = os.path.join(STATE, "last-line")
LOCK = os.path.join(STATE, "sync.lock")
LOG = os.path.join(STATE, "errors.log")
SYNC_EVERY = 0  # right after every question and answer; the lock prevents parallel syncs
# Without this flag Windows opens a console window for every git and python call.
NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def clean(text, limit):
    text = re.sub(r"<[^>]+>.*?</[^>]+>", " ", text, flags=re.S)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace(chr(0x2014), ",").replace(chr(0x2013), ",")  # em and en dash
    return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."


def log_error(msg):
    try:
        os.makedirs(STATE, exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(datetime.datetime.now().isoformat() + " " + msg + "\n")
    except Exception:
        pass


def tail_lines(path, max_bytes=3_000_000):
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        f.seek(max(0, size - max_bytes))
        data = f.read().decode("utf-8", "ignore")
    lines = data.splitlines()
    return lines[1:] if size > max_bytes else lines


def texts(content, kind):
    if isinstance(content, str):
        return [content] if kind == "user" else []
    out = []
    for part in content or []:
        if isinstance(part, dict) and part.get("type") == "text":
            out.append(part.get("text", ""))
    return out


def from_claude(hook):
    path = hook.get("transcript_path")
    if not path or not os.path.exists(path):
        return None
    entries = []
    title = None
    for line in tail_lines(path):
        try:
            e = json.loads(line)
        except Exception:
            continue
        if e.get("type") == "custom-title":
            title = e.get("customTitle") or title
        entries.append(e)
    prompt_idx = None
    for i in range(len(entries) - 1, -1, -1):
        e = entries[i]
        if e.get("type") != "user" or e.get("isMeta"):
            continue
        if clean(" ".join(texts(e.get("message", {}).get("content"), "user")), 400):
            prompt_idx = i
            break
    if prompt_idx is None:
        return None
    prompt = " ".join(texts(entries[prompt_idx]["message"]["content"], "user"))
    answer = []
    for e in entries[prompt_idx + 1:]:
        if e.get("type") == "assistant":
            answer.extend(texts(e.get("message", {}).get("content"), "assistant"))
    who = "claude " + (title or hook.get("session_id", "")[:8])
    return who, prompt, answer[-1] if answer else ""


def session_name(hook):
    path = hook.get("transcript_path")
    if path and os.path.exists(path):
        for line in reversed(tail_lines(path, 1_000_000)):
            if '"custom-title"' in line:
                try:
                    return json.loads(line).get("customTitle")
                except Exception:
                    pass
    return hook.get("session_id", "")[:8]


def prompt_state(session_id):
    return os.path.join(STATE, "prompt-" + re.sub(r"[^A-Za-z0-9-]", "", session_id or "x") + ".txt")


def on_prompt(hook):
    """UserPromptSubmit: log the question right away, independent of the transcript."""
    prompt = hook.get("prompt") or ""
    if not clean(prompt, 180):
        return
    os.makedirs(STATE, exist_ok=True)
    with open(prompt_state(hook.get("session_id")), "w", encoding="utf-8") as f:
        f.write(prompt)
    write("claude " + (session_name(hook) or ""), prompt, "")
    maybe_start_sync()


def on_stop(hook):
    """Stop: log the answer, and warn when the transcript is not being written."""
    result = from_claude(hook)
    state = prompt_state(hook.get("session_id"))
    asked = ""
    if os.path.exists(state):
        with open(state, encoding="utf-8") as f:
            asked = f.read()
    if not result:
        return
    who, prompt, answer = result
    if asked and clean(asked, 180) != clean(prompt, 180):
        with contextlib.redirect_stdout(io.StringIO()):
            note.append(note.current_context(), "[auto " + who + "] WARNING: the transcript of this session is not "
                        "being written (the last question is missing). Probably two processes run on the same "
                        "session. See skills/remote-control-sessions.md.")
        return
    write(who, "(answer)", answer)
    maybe_start_sync()


def from_codex(payload):
    if payload.get("type") != "agent-turn-complete":
        return None
    inputs = payload.get("input-messages") or payload.get("input_messages") or []
    prompt = inputs[-1] if inputs else ""
    answer = payload.get("last-assistant-message") or payload.get("last_assistant_message") or ""
    thread = str(payload.get("thread-id") or payload.get("turn-id") or "")[:8]
    return "codex " + thread, prompt, answer


def write(who, prompt, answer):
    p = clean(prompt, 180)
    if not p:
        return
    a = clean(answer, 260)
    line = "[auto " + who.strip() + "] Q: " + p + (" | A: " + a if a else "")
    os.makedirs(STATE, exist_ok=True)
    if os.path.exists(LAST_LINE):
        with open(LAST_LINE, encoding="utf-8") as f:
            if f.read() == line:
                return
    with open(LAST_LINE, "w", encoding="utf-8") as f:
        f.write(line)
    with contextlib.redirect_stdout(io.StringIO()):
        note.append(note.current_context(), line)


def maybe_start_sync():
    last = os.path.getmtime(SYNC_STAMP) if os.path.exists(SYNC_STAMP) else 0
    if time.time() - last < SYNC_EVERY:
        return
    with open(SYNC_STAMP, "w") as f:
        f.write(str(time.time()))
    subprocess.Popen([sys.executable, os.path.abspath(__file__), "--sync"], cwd=BASE,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, creationflags=NO_WINDOW, close_fds=True)


def sync():
    os.makedirs(STATE, exist_ok=True)
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        if time.time() - os.path.getmtime(LOCK) < 600:
            return
        os.remove(LOCK)
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(fd)
    try:
        def git(*args):
            return subprocess.run(["git", "-C", BASE, *args], capture_output=True, text=True, timeout=120,
                                  creationflags=NO_WINDOW)
        for _ in range(3):
            # Only clients/ and projects/ are committed here; the rest goes with save_session.py.
            git("add", "--", "clients", "projects")
            if git("diff", "--cached", "--quiet").returncode != 0:
                git("commit", "-m", "Auto-journal " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
            if not git("remote").stdout.strip():
                return
            if not git("log", "@{u}..HEAD", "--oneline").stdout.strip():
                return
            r = git("pull", "--rebase", "--autostash")
            if r.returncode != 0:
                git("rebase", "--abort")
                log_error("pull failed: " + r.stderr[-400:])
                return
            r = git("push")
            if r.returncode != 0:
                log_error("push failed: " + r.stderr[-400:])
                return
    finally:
        os.remove(LOCK)


def main():
    args = sys.argv[1:]
    try:
        if args and args[0] == "--sync":
            sync()
            return
        if args and args[0] == "--codex":
            payload_raw = args[-1] if len(args) > 1 else "{}"
            chained = args[1:-1]
            if chained:
                try:
                    subprocess.Popen(chained + [payload_raw], stdin=subprocess.DEVNULL,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                     creationflags=NO_WINDOW)
                except Exception as e:
                    log_error("chaining the codex notify program failed: " + repr(e))
            result = from_codex(json.loads(payload_raw))
            if result:
                write(*result)
                maybe_start_sync()
            return
        hook = json.load(sys.stdin)
        if hook.get("hook_event_name") == "UserPromptSubmit":
            on_prompt(hook)
        else:
            on_stop(hook)
    except Exception as e:
        log_error(repr(e))


if __name__ == "__main__":
    main()
