"""
SessionStart hook: tells every new Claude Code session where the cloud-alter-ego repo lives, which
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

# Token-saving settings for long-lived chats (skills/token-economy.md). Only set when missing, so a
# value you chose on a device stays. Source: code.claude.com/docs/en/settings-reference.
REQUIRED_SETTINGS = {"autoCompactWindow": 200000}
REQUIRED_ENV = {"CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS": "100000", "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"}

BLOCK_START = "<!-- cloud-alter-ego:start -->"
BLOCK_END = "<!-- cloud-alter-ego:end -->"
CLAUDE_MD_BLOCK = """
{start}
## cloud-alter-ego (shared memory, source of truth)

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
    """Fetch the newest context and tools first. The remote is the source of truth.
    Returns a warning when the sync has stalled (stuck rebase, not pushed, autostash)."""
    try:
        sys.path.insert(0, os.path.join(BASE, "tools"))
        import auto_journal
        error = auto_journal.repair() or auto_journal.pull()
        if error:
            auto_journal.set_status(error)
        return auto_journal.health()
    except Exception as e:
        return "WARNING the cloud-alter-ego sync could not be checked: " + repr(e)[:300]


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
        shutil.copy2(path, path + ".bak-cloud-alter-ego-" + time.strftime("%Y%m%d-%H%M%S"))
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
    for key, value in REQUIRED_SETTINGS.items():
        if key not in settings:
            settings[key] = value
            changed = True
    env = settings.setdefault("env", {})
    for key, value in REQUIRED_ENV.items():
        if key not in env:
            env[key] = value
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


def read_hook():
    try:
        if sys.stdin is None or sys.stdin.isatty():
            return {}
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def main():
    hook = read_hook()
    session = hook.get("session_id") or ""
    sync_warning = pull_latest()
    try:
        ensure_setup()
    except Exception:
        pass
    slug, source = note.current_context(session, with_source=True)
    if source == "session":
        target_line = "Context of this session (" + session[:8] + ", .current-context.d): " + slug + "."
    else:
        target_line = ("This session (" + (session[:8] or "id unknown") + ") has no context of its own yet; until you set it, "
                       "everything goes to the device default .current-context: " + slug + " (it may belong to another session).")
    note_cmd = PY_EXE + " " + os.path.join(BASE, "tools", "note.py")
    lines = [
        "cloud-alter-ego (your shared memory: context, working rules, clients and projects) lives in " + BASE + ".",
        target_line,
        "For client or project work, first read its README.md and the newest file in its journal/ folder.",
        "Set the context as soon as it is known: " + note_cmd + " --set <slug>, for this session only (note.py reads CLAUDE_CODE_SESSION_ID; without it add --session " + (session or "<session id>") + "). See --list, create with --new-client or --new-project.",
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
    if sync_warning:
        lines.insert(0, sync_warning)
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(lines),
        }
    }))


if __name__ == "__main__":
    main()
