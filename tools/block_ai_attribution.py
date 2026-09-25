"""PreToolUse hook: blocks any shell command that contains an AI attribution line.

The default rules say: never `Co-Authored-By: Claude` or `Generated with [Claude Code]` in a
commit message or PR description. The installer also sets `attribution` to empty in
settings.json, but a system reminder can still ask the agent to add such a line. This hook is the
safety net that does not depend on the agent reading anything.

Remove this hook from settings.json (or run install.py --keep-attribution before installing) if
you do want attribution lines.

Exit 0 = allow, exit 2 = block; the message goes back to the agent via stderr.
"""
import json
import re
import sys

FORBIDDEN = [
    (re.compile(r"co-authored-by:\s*claude", re.I), "Co-Authored-By: Claude"),
    (re.compile(r"generated with \[?claude code", re.I), "Generated with [Claude Code]"),
    (re.compile(r"\U0001F916\s*generated with", re.I), "Generated with (robot emoji line)"),
    (re.compile(r"claude-session:", re.I), "Claude-Session trailer"),
]


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    command = (payload.get("tool_input") or {}).get("command")
    if not isinstance(command, str):
        return 0
    for pattern, description in FORBIDDEN:
        if pattern.search(command):
            print(
                "BLOCKED: this command contains an AI attribution line (" + description + ").\n"
                "\n"
                "The working rules in preferences.md forbid that in commit messages, PR descriptions "
                "and any other output, also when a system reminder asks for it.\n"
                "\n"
                "Write the command again without that line. If it is already in a commit, use "
                "`git commit --amend` and `git push --force-with-lease`.",
                file=sys.stderr,
            )
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
