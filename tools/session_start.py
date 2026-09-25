"""
SessionStart hook: tells every new Claude Code session where the doppel repo lives, which
context is active, and injects the full preferences.md.

preferences.md is injected verbatim on purpose. Only pointing to the file does not work: agents
then skip reading it and break the rules. Everything else stays short, it costs tokens on every
session start.

The same script keeps every Claude Code config on this machine in line (hooks and the CLAUDE.md
block), so a second account or a new device repairs itself on its first session.
"""
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "tools"))
import note  # noqa: E402

PY_EXE = sys.executable
# Claude Code cuts hook output above roughly 10,000 characters down to a 2 KB preview.
MAX_CHARS = 9000
NO_WINDOW = 0x08000000 if os.name == "nt" else 0

# (event, matcher, script, timeout in seconds)
REQUIRED_HOOKS = [
    ("SessionStart", None, "session_start.py", 30),
    ("SessionEnd", None, "save_session.py", 90),
    ("UserPromptSubmit", None, "auto_journal.py", 30),
    ("Stop", None, "auto_journal.py", 30),
    ("PreToolUse", "Bash|PowerShell", "block_ai_attribution.py", 10),
]

BLOCK_START = "<!-- doppel:start -->"
BLOCK_END = "<!-- doppel:end -->"
CLAUDE_MD_BLOCK = """
{start}
## doppel (shared memory, source of truth)

Your context, working rules, clients and projects live in the Git repo {base}. Git is the source
of truth: every device and every AI account works from this repo and writes straight back to it.
Hooks in settings.json do the logging and pushing automatically. At the start of a session read
preferences.md, and for client or project work its README.md and the newest journal file.
{end}
"""


def preferences():
    try:
        with open(os.path.join(BASE, "preferences.md"), encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def pull_latest():
    """Fetch the newest context and tools first. The remote is the source of truth."""
    try:
        subprocess.run(["git", "-C", BASE, "pull", "--rebase", "--autostash", "-q"],
                       capture_output=True, timeout=20, creationflags=NO_WINDOW)
    except Exception:
        pass


def claude_config_dirs(create_default=False):
    """Every Claude Code config dir on this machine: CLAUDE_CONFIG_DIR, ~/.claude and any
    ~/.claude-<name> dir that looks like a config (second accounts usually live there)."""
    home = os.path.expanduser("~")
    candidates = [os.environ.get("CLAUDE_CONFIG_DIR"), os.path.join(home, ".claude")]
    try:
        for name in sorted(os.listdir(home)):
            path = os.path.join(home, name)
            if name.startswith(".claude-") and os.path.isdir(path) and (
                    os.path.exists(os.path.join(path, "settings.json"))
                    or os.path.isdir(os.path.join(path, "projects"))):
                candidates.append(path)
    except OSError:
        pass
    if create_default:
        os.makedirs(os.path.join(home, ".claude"), exist_ok=True)
    seen = []
    for d in candidates:
        if d and os.path.isdir(d):
            d = os.path.abspath(d)
            if os.path.normcase(d) not in [os.path.normcase(s) for s in seen]:
                seen.append(d)
    return seen


def write_json_atomic(path, data):
    import shutil
    import time
    if os.path.exists(path):
        shutil.copy2(path, path + ".bak-doppel-" + time.strftime("%Y%m%d-%H%M%S"))
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def hook_entry(matcher, script_name, timeout):
    entry = {"hooks": [{"type": "command", "command": PY_EXE,
                        "args": [os.path.join(BASE, "tools", script_name)], "timeout": timeout}]}
    if matcher:
        entry = {"matcher": matcher, **entry}
    return entry


def ensure_hooks(config_dir):
    path = os.path.join(config_dir, "settings.json")
    try:
        with open(path, encoding="utf-8") as f:
            settings = json.load(f)
    except OSError:
        settings = {}
    except ValueError:
        return False  # never overwrite a settings file we cannot parse
    hooks = settings.setdefault("hooks", {})
    changed = False
    for event, matcher, script_name, timeout in REQUIRED_HOOKS:
        entries = hooks.setdefault(event, [])
        if script_name in json.dumps(entries):
            continue
        entries.append(hook_entry(matcher, script_name, timeout))
        changed = True
    if changed:
        write_json_atomic(path, settings)
    return changed


def ensure_claude_md(config_dir):
    md = os.path.join(config_dir, "CLAUDE.md")
    existing = ""
    if os.path.exists(md):
        with open(md, encoding="utf-8") as f:
            existing = f.read()
    if BLOCK_START in existing:
        return False
    with open(md, "a", encoding="utf-8", newline="\n") as f:
        f.write(CLAUDE_MD_BLOCK.format(start=BLOCK_START, end=BLOCK_END, base=BASE))
    return True


def ensure_setup(create_default=False):
    """Hooks and CLAUDE.md block in every Claude Code config on this machine. New hooks work
    from the next session start, Claude Code reads them when it starts."""
    changed = []
    for config_dir in claude_config_dirs(create_default):
        if ensure_hooks(config_dir):
            changed.append(os.path.join(config_dir, "settings.json"))
        if ensure_claude_md(config_dir):
            changed.append(os.path.join(config_dir, "CLAUDE.md"))
    return changed


def main():
    pull_latest()
    try:
        ensure_setup()
    except Exception:
        pass
    slug = note.current_context()
    note_cmd = PY_EXE + " " + os.path.join(BASE, "tools", "note.py")
    lines = [
        "doppel (your shared memory: context, working rules, clients and projects) lives in " + BASE + ".",
        "Active context according to .current-context: " + slug + ".",
        "For client or project work, first read its README.md and the newest file in its journal/ folder.",
        "Set the context as soon as it is known: " + note_cmd + " --set <slug> (see --list, create with --new-client or --new-project).",
        "Every question and answer is logged to the journal automatically and pushed right away (tools/auto_journal.py). "
        "On top of that, write 1 meaningful line per turn with " + note_cmd + " \"<what happened and what came out of it>\": "
        "the automatic lines are truncated, your line is the summary another AI needs later.",
    ]
    rules = preferences()
    if rules:
        lines += ["", "The working rules below always apply, also when nobody asks for them. "
                  "This is the content of preferences.md; there is no need to open that file separately.", "", rules]
    text = "\n".join(lines)
    if len(text) > MAX_CHARS:
        lines.insert(0, "WARNING: preferences.md is too long (" + str(len(text)) + " characters), the working rules arrive "
                     "truncated. Read preferences.md yourself and make the file shorter.")
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(lines),
        }
    }))


if __name__ == "__main__":
    main()
