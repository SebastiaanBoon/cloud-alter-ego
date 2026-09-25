# How it works

alter-ugg has two layers. The cheap layer costs no model tokens and runs through hooks. The
meaningful layer is one short line per turn that the agent writes itself.

## The hooks

| Event | Script | What it does |
|---|---|---|
| SessionStart | `tools/session_start.py` | Pulls the repo, repairs every Claude config on the machine, injects where the repo is, the active context and the full `preferences.md` |
| UserPromptSubmit | `tools/auto_journal.py` | Writes the question, shortened, to the journal of the active context and pushes in the background |
| Stop | `tools/auto_journal.py` | Writes the answer, shortened, and pushes; warns when the transcript stops being written |
| SessionEnd | `tools/save_session.py` | Saves the raw transcript and a readable `.md` in the context's `sessions/`, commits everything, pulls with rebase and pushes |
| PreToolUse (Bash, PowerShell) | `tools/block_ai_attribution.py` | Blocks any command with an AI attribution line |

`tools/install.py` registers all of them once. After that, `session_start.py` keeps every Claude
Code config on the machine in line by itself (`~/.claude`, any `~/.claude-<name>` and
`CLAUDE_CONFIG_DIR`): same hooks, same pointer block in the global `CLAUDE.md`. An account that is not
set up yet repairs itself as soon as any account on the same machine starts a session. New hooks work
from the next session start.

## Codex

Codex has no session-start hook. `install.py` therefore:

- sets `notify` in `~/.codex/config.toml` to `auto_journal.py --codex`, chaining any notify program you
  already had (it still runs first), so every Codex turn lands in the journal;
- adds a pointer block to `~/.codex/AGENTS.md` telling Codex to read `preferences.md` and write
  journal lines.

## Contexts

A context is a folder in `clients/` or `projects/`. The active one lives in `.current-context` (local,
gitignored). Without one, everything lands in `clients/_unsorted/`.

```
python tools/note.py --new-client acme        # create from the template and make it active
python tools/note.py --new-project my-app
python tools/note.py --set acme               # switch
python tools/note.py --list
python tools/note.py "Pipeline failed on a missing config column, fixed by X"
```

Journal lines go to `<context>/journal/<year-month>.md`. `note.py` only writes; `auto_journal.py`
takes the line along in its next commit and push. The agent updates the context README only when
something structural changes (new stack facts, a solved incident, a new preference).

## Why this split

Saving a transcript is mechanical and can be done for free by a hook. Deciding what is worth
remembering from a conversation can only be done by the agent, and that costs tokens. Limiting that
to one line per turn lets the memory grow without every turn rereading and rewriting half the repo.

The injected preferences are the exception: they go in verbatim on every start, because agents skip
files they are only pointed to. That is also why `preferences.md` must stay short. Claude Code cuts
hook output above roughly 10,000 characters down to a 2 KB preview; `session_start.py` warns when the
injection gets too long.

## Multiple devices

The tools find the repo path from their own location, so the same clone works on any device without
changes. Never hardcode a path in the tools: saving would then only work on the machine where that
path exists. Clone your private repo on every device and run `python tools/install.py` once there.

## Save a session by hand

When the hook did not run:

```
python tools/save_session.py <path-to-transcript.jsonl> <context-slug>
```

Transcripts live in `~/.claude/projects/<project>/<session-id>.jsonl`.

## Limits

- The hooks save the conversation (your text, the agent's text, which tools ran). Files created or
  edited during a session stay where they are; they belong in their own project repo.
- Remote Control sessions rarely end, so SessionEnd rarely fires for them. That is exactly why the
  journal is written per turn by `auto_journal.py`.
