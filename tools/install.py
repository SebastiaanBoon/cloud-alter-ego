"""
One-time installer: wires this repo into Claude Code (every account on this machine) and Codex.

What it does:
  1. Registers the hooks in every Claude Code config dir it finds (~/.claude, ~/.claude-<name>,
     CLAUDE_CONFIG_DIR). A backup of settings.json is written next to it first.
       SessionStart      -> tools/session_start.py   (inject rules, self-heal configs)
       UserPromptSubmit  -> tools/auto_journal.py    (log the question, push)
       Stop              -> tools/auto_journal.py    (log the answer, push)
       SessionEnd        -> tools/save_session.py    (save the transcript, commit, push)
       PreToolUse        -> tools/block_ai_attribution.py (no AI attribution in commits)
  2. Adds a short pointer block to the global CLAUDE.md of each config dir.
  3. Turns off Claude's commit and PR attribution lines (skip with --keep-attribution).
  4. If Codex is installed: logs every Codex turn via `notify` (an existing notify program keeps
     working, it is chained) and adds the same pointer block to ~/.codex/AGENTS.md
     (skip with --no-codex).

Usage:
    python tools/install.py
    python tools/install.py --keep-attribution --no-codex
    python tools/install.py --uninstall

Run it once per machine. After that, session_start.py keeps every Claude config in line by
itself, also for accounts you add later.
"""
import json
import os
import re
import shutil
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(BASE, "tools")
sys.path.insert(0, TOOLS)
import session_start as ss  # noqa: E402

AUTO_JOURNAL = os.path.join(TOOLS, "auto_journal.py")
AGENTS_BLOCK = """
{start}
## alter-ugg (shared memory, source of truth)

Your context, working rules, clients and projects live in the Git repo {base}.
Codex has no session-start hook, so do this yourself at the start of every session:
- Read {base}/preferences.md and follow it. Those rules always apply.
- For client or project work, read its README.md and the newest file in its journal/ folder.
- Set the context once it is known: {py} {note} --set <slug>
- Write 1 meaningful line per turn: {py} {note} "<what happened and what came out of it>"
Every turn is also logged automatically through `notify` in ~/.codex/config.toml.
{end}
"""


def say(msg):
    print("  " + msg)


def check_prerequisites():
    ok = True
    if sys.version_info < (3, 8):
        print("Python 3.8 or newer is needed.")
        ok = False
    if not shutil.which("git"):
        print("git is not on PATH. Install git first.")
        ok = False
    elif subprocess.run(["git", "-C", BASE, "rev-parse"], capture_output=True).returncode != 0:
        print("This folder is not a git repo. Clone your copy of the repo instead of downloading a zip.")
        ok = False
    return ok


def warn_if_public():
    """Your copy fills up with clients, conversations and journals. It must be private."""
    url = subprocess.run(["git", "-C", BASE, "remote", "get-url", "origin"], capture_output=True,
                         text=True).stdout.strip()
    if not url:
        say("No git remote yet. Add a PRIVATE remote, otherwise nothing syncs between devices.")
        return
    if "github.com" in url and shutil.which("gh"):
        r = subprocess.run(["gh", "repo", "view", url, "--json", "visibility", "-q", ".visibility"],
                           capture_output=True, text=True)
        if r.stdout.strip().upper() == "PUBLIC":
            print("\n  WARNING: " + url + " is PUBLIC. Your journals and transcripts will be pushed there.")
            print("  Make it private first:  gh repo edit --visibility private --accept-visibility-change-consequences\n")


def set_attribution_off(config_dir):
    path = os.path.join(config_dir, "settings.json")
    try:
        with open(path, encoding="utf-8") as f:
            settings = json.load(f)
    except OSError:
        settings = {}
    except ValueError:
        return False
    wanted = {"commit": "", "pr": ""}
    current = settings.get("attribution") or {}
    if all(current.get(k) == v for k, v in wanted.items()) and settings.get("includeCoAuthoredBy") is False:
        return False
    settings["attribution"] = {**current, **wanted}
    settings["includeCoAuthoredBy"] = False
    ss.write_json_atomic(path, settings)
    return True


# ---------- Codex ----------

def codex_dir():
    path = os.path.join(os.path.expanduser("~"), ".codex")
    if os.path.isdir(path) or shutil.which("codex"):
        os.makedirs(path, exist_ok=True)
        return path
    return None


def split_head(text):
    """Top-level keys live before the first [table] header."""
    m = re.search(r"^\s*\[", text, re.M)
    return (text[: m.start()], text[m.start():]) if m else (text, "")


def read_notify(text):
    head, _ = split_head(text)
    try:
        import tomllib
        value = tomllib.loads(head).get("notify")
        return value if isinstance(value, list) else None
    except ImportError:
        m = re.search(r"^notify\s*=\s*(\[.*?\])\s*$", head, re.M | re.S)
        if not m:
            return None
        try:
            return json.loads(m.group(1))
        except ValueError:
            raise RuntimeError("cannot parse the existing notify line without Python 3.11+")


def replace_notify(text, items):
    head, rest = split_head(text)
    head = re.sub(r"^notify\s*=\s*\[.*?\]\s*\n?", "", head, count=1, flags=re.M | re.S)
    line = "notify = [" + ", ".join(json.dumps(i) for i in items) + "]\n" if items else ""
    return line + head + rest


def install_codex():
    cdir = codex_dir()
    if not cdir:
        say("Codex not found, skipped.")
        return
    cfg = os.path.join(cdir, "config.toml")
    text = open(cfg, encoding="utf-8").read() if os.path.exists(cfg) else ""
    existing = read_notify(text) or []
    if any(os.path.normcase(str(x)) == os.path.normcase(AUTO_JOURNAL) for x in existing):
        say("Codex notify already logs to this repo.")
    else:
        if os.path.exists(cfg):
            shutil.copy2(cfg, cfg + ".bak-alter-ugg")
        items = [sys.executable, AUTO_JOURNAL, "--codex"] + [str(x) for x in existing]
        with open(cfg, "w", encoding="utf-8", newline="\n") as f:
            f.write(replace_notify(text, items))
        say("Codex notify now logs every turn" + (" (your existing notify program is chained)." if existing else "."))
    agents = os.path.join(cdir, "AGENTS.md")
    current = open(agents, encoding="utf-8").read() if os.path.exists(agents) else ""
    if ss.BLOCK_START not in current:
        note_py = os.path.join(TOOLS, "note.py")
        with open(agents, "a", encoding="utf-8", newline="\n") as f:
            f.write(AGENTS_BLOCK.format(start=ss.BLOCK_START, end=ss.BLOCK_END, base=BASE,
                                        py=sys.executable, note=note_py))
        say("Pointer block added to " + agents)


def uninstall_codex():
    cdir = os.path.join(os.path.expanduser("~"), ".codex")
    cfg = os.path.join(cdir, "config.toml")
    if os.path.exists(cfg):
        text = open(cfg, encoding="utf-8").read()
        existing = read_notify(text) or []
        if any(os.path.normcase(str(x)) == os.path.normcase(AUTO_JOURNAL) for x in existing):
            idx = [os.path.normcase(str(x)) for x in existing].index(os.path.normcase(AUTO_JOURNAL))
            chained = existing[idx + 2:]  # drop python, auto_journal.py and --codex
            with open(cfg, "w", encoding="utf-8", newline="\n") as f:
                f.write(replace_notify(text, chained))
            say("Codex notify restored.")
    remove_block(os.path.join(cdir, "AGENTS.md"))


# ---------- uninstall helpers ----------

def remove_block(path):
    if not os.path.exists(path):
        return
    text = open(path, encoding="utf-8").read()
    new = re.sub(r"\n?" + re.escape(ss.BLOCK_START) + r".*?" + re.escape(ss.BLOCK_END) + r"\n?", "\n", text,
                 flags=re.S)
    if new != text:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
        say("Block removed from " + path)


def uninstall_claude(config_dir):
    path = os.path.join(config_dir, "settings.json")
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                settings = json.load(f)
        except ValueError:
            settings = None
        if settings:
            hooks = settings.get("hooks", {})
            changed = False
            for event in list(hooks):
                keep = [e for e in hooks[event] if os.path.normcase(TOOLS) not in os.path.normcase(json.dumps(e).replace("\\\\", "\\"))]
                if len(keep) != len(hooks[event]):
                    changed = True
                    hooks[event] = keep
                if not hooks[event]:
                    del hooks[event]
            if changed:
                ss.write_json_atomic(path, settings)
                say("Hooks removed from " + path)
    remove_block(os.path.join(config_dir, "CLAUDE.md"))


def main():
    args = set(sys.argv[1:])
    if not check_prerequisites():
        return 1
    if "--uninstall" in args:
        print("Removing alter-ugg from this machine:")
        for d in ss.claude_config_dirs():
            uninstall_claude(d)
        uninstall_codex()
        print("Done. Attribution settings were left as they are. Your repo is untouched.")
        return 0

    print("Installing alter-ugg from " + BASE)
    warn_if_public()
    changed = ss.ensure_setup(create_default=True)
    for d in ss.claude_config_dirs():
        say("Claude config: " + d)
    for c in changed:
        say("updated " + c)
    if "--keep-attribution" not in args:
        for d in ss.claude_config_dirs():
            if set_attribution_off(d):
                say("Commit and PR attribution turned off in " + os.path.join(d, "settings.json"))
    if "--no-codex" not in args:
        try:
            install_codex()
        except Exception as e:
            say("Codex setup skipped: " + str(e))
    print("""
Done. Next steps:
  1. Start a NEW Claude Code session (hooks are read at startup). The rules from preferences.md
     are injected automatically.
  2. Fill in identity.md, then adjust preferences.md to your own taste.
  3. Add your work:  python tools/note.py --new-client acme   or   --new-project my-app
  4. On another machine or account: clone the same private repo and run this installer there.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
