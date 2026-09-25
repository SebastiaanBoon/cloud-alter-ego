"""
SessionEnd hook: saves a Claude Code transcript in the folder of the active context.

Reads the hook payload (JSON) from stdin, finds the active context in .current-context, and
writes the raw .jsonl plus a readable .md to <clients|projects>/<slug>/sessions/. Then commits
everything that changed in the repo, pulls with rebase (other devices push too) and pushes.

Manual use: python tools/save_session.py <transcript_path> [context-slug]
"""
import datetime
import json
import os
import shutil
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "tools"))
import note  # noqa: E402

NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def read_payload():
    """The hook passes JSON on stdin; manually the transcript path can be argv[1]."""
    if len(sys.argv) > 1:
        payload = {"transcript_path": sys.argv[1]}
        if len(sys.argv) > 2:
            payload["context_override"] = sys.argv[2]
        return payload
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def active_context(payload):
    override = payload.get("context_override")
    if override and note.context_dir(override):
        return override
    return note.current_context()


def block_text(content):
    """Turn message.content (a string or a list of blocks) into readable text."""
    if isinstance(content, str):
        return content
    parts = []
    for blk in content or []:
        if not isinstance(blk, dict):
            continue
        t = blk.get("type")
        if t == "text":
            parts.append(blk.get("text", ""))
        elif t == "tool_use":
            parts.append("_[tool: " + blk.get("name", "tool") + "]_")
        elif t == "tool_result":
            parts.append("_[tool result]_")
    return "\n".join(p for p in parts if p)


def jsonl_to_md(transcript_path):
    lines_out = []
    title = None
    with open(transcript_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if obj.get("type") not in ("user", "assistant"):
                continue
            msg = obj.get("message") or {}
            role = msg.get("role")
            if role not in ("user", "assistant"):
                continue
            text = block_text(msg.get("content"))
            if not text.strip():
                continue
            who = "User" if role == "user" else "Claude"
            ts = (obj.get("timestamp") or "")[:19].replace("T", " ")
            if title is None and role == "user":
                title = text.strip().split("\n")[0][:80]
            lines_out.append("### " + who + " (" + ts + ")\n\n" + text.strip() + "\n")
    return "# Session: " + (title or "untitled") + "\n\n" + "\n".join(lines_out)


def git(*args, timeout=60):
    return subprocess.run(["git", "-C", BASE, *args], timeout=timeout, capture_output=True, text=True,
                          creationflags=NO_WINDOW)


def main():
    payload = read_payload()
    tp = payload.get("transcript_path")
    if not tp or not os.path.exists(tp):
        return
    slug = active_context(payload)
    session_id = payload.get("session_id") or os.path.splitext(os.path.basename(tp))[0]
    base_name = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S") + "-" + session_id[:8]

    dest_dir = os.path.join(note.context_dir(slug) or note.context_dir(note.FALLBACK), "sessions")
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copyfile(tp, os.path.join(dest_dir, base_name + ".jsonl"))
    try:
        with open(os.path.join(dest_dir, base_name + ".md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(jsonl_to_md(tp))
    except Exception:
        pass

    try:
        git("add", "-A", timeout=30)
        git("commit", "-q", "-m", "Session saved: " + slug + " (" + base_name + ")", timeout=30)
        branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        if not branch or branch == "HEAD" or not git("remote").stdout.strip():
            return
        # Other devices push too; without a pull the push fails silently and the repo drifts apart.
        git("pull", "-q", "--rebase", "--autostash", "origin", branch)
        git("push", "origin", branch)
    except Exception:
        pass


if __name__ == "__main__":
    main()
