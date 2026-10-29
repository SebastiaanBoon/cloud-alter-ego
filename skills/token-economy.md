# Working economically with tokens

Use this when you set up routines, subagents and long sessions, and when the user asks where the
session limit went. The goal is the same result for as little of the plan limit as possible.

## Measure

- `python3 tools/token_usage.py` shows the last 5 hours (the window of the session limit), or
  `--hours 168` for a week. Per session its share, with subagents under their session and routines by
  name. It only counts the machine it runs on: run it on every machine. Chats on claude.ai are not in it.
- Rough weights: output 5x, cache write 1.25x, cache read 0.1x of input, the largest model 5/3 of the
  middle one.

## What costs the most

1. A routine with one subagent per item. Every subagent reads the runbook and the context again.
2. Resuming a long session: each turn after a pause of more than an hour, or after a restart, reads the
   whole context again as a cache write. A session with 500k of context can cost a fifth of the limit
   for one turn.
3. Big but simple work spread over many mid-size subagents, for example relabelling tens of thousands of
   records three times each.
4. Big dumps in the context: whole files, logs, web pages, JSON of an API.

## Rules

- Keep long-lived chats if the user works that way. Do not propose starting new sessions, the settings
  below absorb the cost.
- Settings, put on every device by `tools/session_start.py` (`ensure_hooks`, only when the key is
  missing, active from the next session start):
  - `autoCompactWindow: 200000`: a session compacts at 200k instead of at the model maximum.
  - `env.CLAUDE_CODE_IDLE_COMPACT_MIN_TOKENS: 100000`: a chat that stands still for about 54 minutes is
    summarised just before the cache expires, so the next message sends a summary instead of the whole
    history.
  - `env.CLAUDE_CODE_SUBAGENT_MODEL: haiku`: a subagent without a model runs on Haiku.
- Big but simple work (labelling, classifying, sorting, fetching, summarising): always Haiku, however
  much it is. The middle model for research and hard parts. At most 5 subagents at a time and every item
  once. No double or triple checking runs: check a sample yourself. If a script can do it, script first.
- Routines: as few subagents as possible. A subagent only when the work is really parallel or the main
  context would fill up. Several small items go in one subagent, one after the other.
- A job above roughly a million tokens: tell the user the size first, then start.
- Read precisely: `grep`, `sed -n`, `head`, a `--query` on az, `--jq` on gh. No whole files or unfiltered
  API answers in the context.
- Background commands with an `until` loop and a notification, not constant polling.
- Keep `preferences.md` under 9,000 characters: it is read at every session start, in every session.

## Check

Run `tools/token_usage.py` before and after a change to a routine and compare the share.

## Self-learning

A new big cost driver you measure goes in "What costs the most" with the measurement.
