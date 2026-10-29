"""Token usage per Claude Code session on this machine, from the transcripts in ~/.claude/projects.

Groups subagents under their parent session and names the session by its first prompt (routine name or
the start of the question). The weight column approximates how hard it counts towards the plan limit:
input + 1.25 x cache write + 0.1 x cache read + 5 x output, times 5/3 for Opus (API price ratios).

    python3 tools/token_usage.py            # last 5 hours (the session limit window)
    python3 tools/token_usage.py --hours 168
"""
import argparse
import glob
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone


def first_prompt(path: str) -> str:
    try:
        with open(path, errors="ignore") as f:
            for line in f:
                d = json.loads(line)
                if d.get("type") != "user":
                    continue
                c = d["message"]["content"]
                if not isinstance(c, str):
                    c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
                m = re.match(r"Routine ([\w-]+)", c)
                return f"routine {m.group(1)}" if m else c.strip().replace("\n", " ")[:50]
    except (OSError, json.JSONDecodeError, KeyError):
        pass
    return "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=5)
    args = ap.parse_args()
    cut = datetime.now(timezone.utc) - timedelta(hours=args.hours)
    root = os.path.expanduser("~/.claude/projects")
    totals = defaultdict(lambda: defaultdict(float))
    names = {}
    files = glob.glob(f"{root}/*/*.jsonl") + glob.glob(f"{root}/*/*/subagents/*.jsonl")
    for path in files:
        if os.path.getmtime(path) < cut.timestamp():
            continue
        rel = os.path.relpath(path, root).split(os.sep)
        session = rel[1].split(".")[0]
        main_file = os.path.join(root, rel[0], session + ".jsonl")
        names.setdefault(session, first_prompt(main_file))
        t = totals[session]
        with open(path, errors="ignore") as f:
            for line in f:
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if d.get("type") != "assistant" or not d.get("timestamp"):
                    continue
                if datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00")) < cut:
                    continue
                msg = d.get("message", {})
                u = msg.get("usage") or {}
                factor = 5 / 3 if "opus" in (msg.get("model") or "") else 1
                t["calls"] += 1
                t["out"] += u.get("output_tokens", 0)
                t["cw"] += u.get("cache_creation_input_tokens", 0)
                t["cr"] += u.get("cache_read_input_tokens", 0)
                t["weight"] += factor * (u.get("input_tokens", 0) + 1.25 * u.get("cache_creation_input_tokens", 0)
                                         + 0.1 * u.get("cache_read_input_tokens", 0) + 5 * u.get("output_tokens", 0))
                if msg.get("model"):
                    t["model:" + msg["model"]] = 1
    rows = sorted(((t["weight"], s) for s, t in totals.items() if t["calls"]), reverse=True)
    total = sum(w for w, _ in rows) or 1
    print(f"Last {args.hours:g} hours, {len(rows)} sessions on this machine\n")
    print(f"{'share':>6} {'calls':>6} {'output':>8} {'cachewr':>8} {'cacherd':>9}  model      session")
    for w, s in rows:
        t = totals[s]
        model = ",".join(k[len("model:claude-"):] for k in t if k.startswith("model:claude-"))
        print(f"{100 * w / total:5.1f}% {int(t['calls']):6} {int(t['out']):8} {int(t['cw']):8} {int(t['cr']):9}  "
              f"{model:<10} {names[s]} ({s[:8]})")


if __name__ == "__main__":
    main()
