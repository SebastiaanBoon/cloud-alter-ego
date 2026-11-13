"""PreToolUse hook: makes a session on the largest model hand execution work to a cheaper agent.

The rule "execution work goes to a subagent on a smaller model" is in preferences.md, but a session
on the largest model tends to do every step itself. This hook counts the direct Read, Bash and
PowerShell calls per session. After 12 in a row it blocks, until an Agent with a model other than
the largest has been started. Calls made inside a subagent never count.

Grep and Glob are not counted: their output is small and an agent for a single search costs more
than it saves. A subagent for two or three calls costs tens of thousands of tokens by itself, and
every result wakes the main session, which then reads its whole context again. Delegating pays off
for a block of work with a clear end result, not for single steps.

Set CLOUD_ALTER_EGO_MAX_DIRECT to change the limit, or remove the hook from settings.json to turn
it off. Exit 0 = allow, exit 2 = block; the message goes back to the agent via stderr.
"""
import json
import os
import re
import sys
from pathlib import Path

try:
    MAX_DIRECT = int(os.environ.get("CLOUD_ALTER_EGO_MAX_DIRECT", "12"))
except ValueError:
    MAX_DIRECT = 12
DIRECT_TOOLS = {"Read", "Bash", "PowerShell"}
CHEAP = re.compile(r"sonnet|haiku", re.I)
# Journal lines always stay direct: they belong to every turn.
FREE = re.compile(r"tools[\\/]note\.py", re.I)
STATE_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "claude-delegation"


def session_model(transcript_path: str) -> str:
    """Model of the last assistant message in the transcript."""
    try:
        with open(transcript_path, "rb") as f:
            f.seek(0, os.SEEK_END)
            f.seek(max(0, f.tell() - 400_000))
            lines = f.read().decode("utf-8", "ignore").splitlines()
    except OSError:
        return ""
    for line in reversed(lines):
        if '"assistant"' not in line:
            continue
        try:
            item = json.loads(line)
        except ValueError:
            continue
        model = (item.get("message") or {}).get("model")
        if item.get("type") == "assistant" and model:
            return model
    return ""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    if payload.get("agent_id"):
        return 0
    if "opus" not in session_model(payload.get("transcript_path") or "").lower():
        return 0

    session = payload.get("session_id") or "unknown"
    tool = payload.get("tool_name") or ""
    tool_input = payload.get("tool_input") or {}
    state_file = STATE_DIR / f"{session}.json"
    try:
        count = json.loads(state_file.read_text()).get("direct", 0)
    except (OSError, ValueError):
        count = 0

    if tool == "Agent":
        # Without a model CLAUDE_CODE_SUBAGENT_MODEL from settings.json applies; a fork always inherits the big model.
        model = tool_input.get("model") or os.environ.get("CLAUDE_CODE_SUBAGENT_MODEL") or ""
        if tool_input.get("subagent_type") != "fork" and CHEAP.search(str(model)):
            count = 0
    elif tool in DIRECT_TOOLS:
        if FREE.search(str(tool_input.get("command") or "")):
            return 0
        if count >= MAX_DIRECT:
            print(
                f"BLOCKED: already {count} direct tool calls in this session without an agent.\n"
                "\n"
                "Execution work (fetching, reading, searching, checks, simple edits) goes through the Agent "
                'tool with model "sonnet" or "haiku". Pass the relevant working rules literally and give a '
                "concrete assignment with a clear end result. The big model only does judgment, analysis and "
                "the final text.\n"
                "\n"
                f"Start an Agent with model sonnet or haiku for this step. After that {MAX_DIRECT} direct "
                "calls are allowed again.",
                file=sys.stderr,
            )
            return 2
        count += 1
    else:
        return 0

    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps({"direct": count}))
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
