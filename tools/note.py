"""
Writes one short line per turn to the journal of the active context (a client or a project).

Called by the agent during a session, so the memory grows without rereading or committing the
whole repo. auto_journal.py pushes the journals right away; save_session.py commits the rest at
the end of a session.

Usage:
    python tools/note.py "short line about what just happened"
    python tools/note.py --context acme "line for a specific client or project"
    python tools/note.py --set acme            (make acme the active context)
    python tools/note.py --show                (print the active context)
    python tools/note.py --list                (list all clients and projects)
    python tools/note.py --new-client acme     (create clients/acme from the template)
    python tools/note.py --new-project my-app  (create projects/my-app from the template)

A context is a folder in clients/ or projects/. "_unsorted" is the fallback for work that does
not belong to one.
"""
import datetime
import os
import re
import shutil
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKER = os.path.join(BASE, ".current-context")
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


def current_context():
    if os.path.exists(MARKER):
        with open(MARKER, encoding="utf-8") as f:
            slug = f.read().strip()
        if context_dir(slug):
            return slug
    return FALLBACK


def set_context(slug):
    if not context_dir(slug):
        print("unknown context: " + slug + ". Create it with --new-client or --new-project, see --list.")
        return 1
    with open(MARKER, "w", encoding="utf-8") as f:
        f.write(slug)
    print("active context: " + slug)
    return 0


def new_context(kind, slug):
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
    return set_context(slug)


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
        f.write("- " + now.strftime("%H:%M") + " " + text.strip() + "\n")
    print(path)
    return 0


def main():
    args = sys.argv[1:]
    if not args or args[0] == "--show":
        print(current_context())
        return 0
    if args[0] == "--list":
        for kind, name in all_contexts():
            print(kind + "/" + name)
        return 0
    if args[0] in ("--set", "--set-client", "--set-context"):
        if len(args) < 2:
            print("give a slug")
            return 1
        return set_context(args[1])
    if args[0] in ("--new-client", "--new-project"):
        if len(args) < 2:
            print("give a slug")
            return 1
        return new_context("clients" if args[0] == "--new-client" else "projects", args[1])
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
    return append(slug or current_context(), text)


if __name__ == "__main__":
    sys.exit(main())
