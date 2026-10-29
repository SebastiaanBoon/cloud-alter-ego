# cloud-alter-ego

**Your cloud alter ego for AI coding agents.** It remembers what you did yesterday, on which laptop,
with which account, and makes every agent follow your rules.

cloud-alter-ego is a Git repo that becomes the shared memory of every agent you work with: Claude
Code on any account and any device (including Remote Control from your phone) and Codex. Hooks inject
your working rules at the start of every session, log every question and answer into a journal per
client or project, save full transcripts at the end, and push it all, so every device and account
always works from the same brain.

```
you ask something ──> UserPromptSubmit hook ──> journal line ──> git push
agent answers     ──> Stop hook             ──> journal line ──> git push
new session       ──> SessionStart hook     ──> your rules + active client injected
session ends      ──> SessionEnd hook       ──> full transcript saved ──> git push
another device    ──> git pull on start     ──> same memory everywhere
```

## Repo or connector

There are two ways to get the same memory:

- **This repo** is for people who work with Claude Code or Codex on their own machines. Hooks log every turn,
  save transcripts and inject your rules without the agent having to remember anything.
- **The Alter Ego connector**, a remote MCP server, is for chats in Claude or ChatGPT, on the
  web or the phone, without installing anything. It keeps the memory in your own OneDrive, Google Drive,
  Dropbox, GitHub or Azure DevOps.

They work together: point the connector at the GitHub or Azure DevOps copy of this repo and it reads
`preferences.md`, `identity.md`, `clients/`, `projects/` and `skills/` as they are, and writes journal
lines in the same format.

## Get started

1. **Make your own private copy.** Click **Use this template** on GitHub and choose **Private**.
   Your copy will fill up with clients, conversations and journals. Never make it public.
2. **Clone it** anywhere on your machine.
3. **Install:** `python tools/install.py` (Python 3.8+ and git needed). It registers the hooks in
   every Claude Code config it finds, adds a pointer to your global `CLAUDE.md`, turns off AI
   attribution in commits and, when Codex is installed, hooks Codex in too. Settings files are backed
   up first. Undo with `python tools/install.py --uninstall`.
4. **Start a new Claude Code session.** Your rules are injected automatically from now on.
5. **Make it yours:** fill in `identity.md`, tune `preferences.md`, and add your work:

   ```
   python tools/note.py --new-client acme
   python tools/note.py --new-project my-app
   ```

   Tip: ask your agent to go through all your GitHub repos (`gh repo list`) and create a project
   folder for each, so nothing is missing from day one.
6. **Every other device or account:** clone the same private repo and run the installer there.

## What is in the box

The core is five hooks and `note.py`, all plain Python with no dependencies, on Windows, macOS and Linux.
Everything else is optional: take what fits your work.

### Core

| Path | What |
|---|---|
| [preferences.md](preferences.md) | Working rules injected at every session start. Sensible defaults for style, scope, code and facts; edit them |
| [preferences-background.md](preferences-background.md) | The reasoning behind every rule |
| [identity.md](identity.md) | Who you are: role, stack, how you work with agents (template) |
| [personal.md](personal.md) | Optional personal context (template) |
| [clients/](clients/README.md) | One folder per client: README with stack and incident history, `journal/`, `sessions/` |
| [projects/](projects/README.md) | One folder per own project, plus the infrastructure they share |
| [WORKFLOW.md](WORKFLOW.md) | How the hooks, contexts and syncing work |
| `tools/install.py` | Registers the hooks, undo with `--uninstall` |
| `tools/session_start.py`, `auto_journal.py`, `save_session.py`, `block_ai_attribution.py` | The hooks: inject rules, log every turn, save the transcript, block AI attribution |
| `tools/note.py` | Journal lines and contexts |
| `tools/redact.py` | Masks tokens, keys and passwords in every journal line and saved transcript before it is pushed |
| [tests/](tests/) | `python -m pytest -q tests` |
| [CHANGELOG.md](CHANGELOG.md) | What changed per release |

### Optional

| Path | What |
|---|---|
| [skills/](skills/README.md) | Runbooks. Core ones for how agents work for you, plus examples from real work (data platforms, client tickets, sales, investing) to keep, delete or copy |
| [techniques/](techniques/README.md) | Reusable technical knowledge: Fabric, fabric-cicd, dbt, Databricks, Azure, Entra ID, Microsoft 365 groups, Power BI, Git, client environments, agent sessions on a Linux server |
| `tools/run_routine.sh`, `run_routine.ps1` | Scheduled routines with a fixed session and usage-limit recovery |
| `tools/token_usage.py` | Token use per session |
| `tools/firefox_profile.py` | Signed-in browser access through a copy of a Firefox profile |
| `tools/*.ps1` | Windows only: start and watch Remote Control sessions, type into a session, start ChatGPT |
| `tools/server/` | Linux with systemd: agent sessions on a small server |

## Daily use

- Tell the agent what you are working on, or set it yourself: `python tools/note.py --set acme`.
  The context is per session, so parallel sessions each log to their own journal.
  The agent reads that client's README and newest journal before it starts.
- The agent writes one meaningful journal line per turn. The automatic lines from the hooks are a
  safety net, the agent's line is the summary a future session needs.
- When a session teaches you something reusable, it goes into `techniques/`. A new working rule goes
  into `preferences.md`, with the story behind it in `preferences-background.md`.

## Privacy and safety

- Your copy must be **private**: transcripts and journals are pushed automatically. The installer
  warns when your remote is public.
- Never store secrets here. Resource names are fine, keys and passwords are not. As a safety net
  `tools/redact.py` masks known token formats, private keys and `password=`-style values in journals and
  transcripts. It does not catch everything, so still keep secrets out of chats.
- `.current-context`, `.current-context.d/`, `.auto-journal/` and `tools/sessions.json` are local and gitignored.
- The hooks never fail hard: errors go to `.auto-journal/errors.log` and a session never gets stuck.
- Journals use a union merge (`.gitattributes`), so parallel sessions never block each other on a
  journal conflict.

## Requirements

- Claude Code (any plan that supports hooks), optionally Codex.
- Python 3.8 or newer, git, and a private Git remote.
- Windows, macOS or Linux for the core. See Optional above for the parts tied to one system.

## License

MIT, see [LICENSE](LICENSE).
