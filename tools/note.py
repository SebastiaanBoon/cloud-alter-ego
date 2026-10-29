"""
Writes one short line per turn to the journal of the active context (a client or a project).

Called by the agent during a session, so the memory grows without rereading or committing the
whole repo. auto_journal.py pushes the journals right away; save_session.py commits the rest at
the end of a session.

Usage:
    python tools/note.py "short line about what just happened"
    python tools/note.py --context acme "line for a specific client or project"
    python tools/note.py --set acme            (make acme the active context of this session)
    python tools/note.py --set acme --global   (make acme the device default)
    python tools/note.py --show                (print the active context and where it comes from)
    python tools/note.py --list                (list all clients and projects)
    python tools/note.py --new-client acme     (create clients/acme from the template)
    python tools/note.py --new-project my-app  (create projects/my-app from the template)

A context is a folder in clients/ or projects/. "_unsorted" is the fallback for work that does
not belong to one.

The context is per session. --set writes .current-context.d/<session id> when the session is
known: via --session <id>, or the environment variable AGENTCONTEXT_SESSION, CLAUDE_CODE_SESSION_ID
(Claude Code sets it in every shell call) or CODEX_SESSION_ID. Without a session, or with
--global, it writes .current-context, the device default for sessions that have no context of
their own yet. The hooks get session_id in their JSON and so read the context of their own
session, which keeps parallel sessions out of each other's journal.
"""
import datetime
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from redact import redact  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKER = os.path.join(BASE, ".current-context")
SESSION_DIR = MARKER + ".d"
SESSION_ENV = ("AGENTCONTEXT_SESSION", "CLAUDE_CODE_SESSION_ID", "CODEX_SESSION_ID")
KINDS = ("clients", "projects")
FALLBACK = "_unsorted"
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
INDEX_MARKER = "<!-- new rows are added above this line -->"


def context_dir(slug):
    """Folder of a context, or None when it does not exist."""
    if slug == FALLBACK:
        return os.path.join(BASE, "clients", FALLBACK)
    if not slug or not SLUG.match(slug):
        return None
    for kind in KINDS:
        path = os.path.join(BASE, kind, slug)
        if os.path.isdir(path):
            return path
    return None


def all_contexts():
    found = []
    for kind in KINDS:
        root = os.path.join(BASE, kind)
        if not os.path.isdir(root):
            continue
        for name in sorted(os.listdir(root)):
            if SLUG.match(name) and os.path.isdir(os.path.join(root, name)):
                found.append((kind, name))
    return found


def session_marker(session=None):
    """Marker file of a session (explicit id, else from the environment), or None."""
    if not session:
        for name in SESSION_ENV:
            if os.environ.get(name):
                session = os.environ[name]
                break
    key = re.sub(r"[^A-Za-z0-9_-]", "", str(session or ""))[:80]
    return os.path.join(SESSION_DIR, key) if key else None


def read_marker(path):
    if path and os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                slug = f.read().strip()
        except OSError:
            return None
        if context_dir(slug):
            return slug
    return None


def current_context(session=None, with_source=False):
    """Context of this session; without one the device default; else the fallback."""
    slug, source = read_marker(session_marker(session)), "session"
    if not slug:
        slug, source = read_marker(MARKER), "device default"
    if not slug:
        slug, source = FALLBACK, "no pointer"
    return (slug, source) if with_source else slug


def set_context(slug, session=None, device=False):
    if not context_dir(slug):
        print("unknown context: " + slug + ". Create it with --new-client or --new-project, see --list.")
        return 1
    path = None if device else session_marker(session)
    if path:
        os.makedirs(SESSION_DIR, exist_ok=True)
    with open(path or MARKER, "w", encoding="utf-8") as f:
        f.write(slug)
    if path:
        print("active context for session " + os.path.basename(path)[:8] + ": " + slug)
    else:
        print("active context (device default): " + slug)
    return 0


def new_context(kind, slug, session=None, device=False):
    if not SLUG.match(slug or ""):
        print("use a lowercase slug with letters, digits and dashes, for example acme or my-app")
        return 1
    if context_dir(slug):
        print(slug + " already exists")
        return 1
    template = os.path.join(BASE, kind, "_template")
    target = os.path.join(BASE, kind, slug)
    shutil.copytree(template, target)
    readme = os.path.join(target, "README.md")
    if os.path.exists(readme):
        with open(readme, encoding="utf-8") as f:
            text = f.read()
        with open(readme, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.replace("<NAME>", slug))
    index = os.path.join(BASE, kind, "README.md")
    if os.path.exists(index):
        with open(index, encoding="utf-8") as f:
            text = f.read()
        if INDEX_MARKER in text:
            row = "| [" + slug + "](" + slug + "/README.md) | | |\n"
            text = text.replace(INDEX_MARKER, row + INDEX_MARKER)
            with open(index, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
    print("created " + os.path.relpath(target, BASE) + ", fill in its README.md")
    return set_context(slug, session, device)


def append(slug, text):
    folder = context_dir(slug) or context_dir(FALLBACK)
    now = datetime.datetime.now()
    path = os.path.join(folder, "journal", now.strftime("%Y-%m") + ".md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    day = now.strftime("## %Y-%m-%d")
    existing = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            existing = f.read()
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        if not existing:
            f.write("# Journal " + slug + " " + now.strftime("%Y-%m") + "\n\n")
        if day not in existing:
            f.write("\n" + day + "\n\n")
        f.write("- " + now.strftime("%H:%M") + " " + redact(text.strip()) + "\n")
    print(path)
    return 0


def main():
    args = sys.argv[1:]
    session, device = None, False
    if "--session" in args:
        i = args.index("--session")
        session = args[i + 1] if i + 1 < len(args) else None
        args = args[:i] + args[i + 2:]
    if "--global" in args:
        device = True
        args.remove("--global")
    if not args or args[0] == "--show":
        slug, source = current_context(session, with_source=True)
        print(slug + " (" + source + ")")
        return 0
    if args[0] == "--list":
        for kind, name in all_contexts():
            print(kind + "/" + name)
        return 0
    if args[0] in ("--set", "--set-client", "--set-context"):
        if len(args) < 2:
            print("give a slug")
            return 1
        return set_context(args[1], session, device)
    if args[0] in ("--new-client", "--new-project"):
        if len(args) < 2:
            print("give a slug")
            return 1
        return new_context("clients" if args[0] == "--new-client" else "projects", args[1], session, device)
    slug = None
    if args[0] in ("--context", "--client"):
        if len(args) < 3:
            print("usage: --context <slug> <text>")
            return 1
        slug = args[1]
        args = args[2:]
        if not context_dir(slug):
            print("unknown context: " + slug)
            return 1
    text = " ".join(args)
    if not text.strip():
        return 1
    return append(slug or current_context(session), text)


if __name__ == "__main__":
    sys.exit(main())
