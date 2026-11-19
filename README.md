# cloud-alter-ego

> **Just want it in Claude chats, with nothing to install?** Use the Alter Ego connector: **https://cloudalterego.cafeboon.com**
>
> 1. In Claude, go to **Customize**, then **Connectors**, click **+ Add**, then **Add custom connector**.
> 2. Enter a name (for example Alter Ego) and paste `https://cloudalterego.cafeboon.com/mcp`, then click **Continue** and **Add**.
> 3. Sign in and choose where your memory lives: OneDrive, Google Drive, Dropbox, GitHub or Azure DevOps.
> 4. Switch the connector on in a chat (**+**, then **Connectors**). Setup per storage and troubleshooting:
>    [cloudalterego.cafeboon.com/docs.html](https://cloudalterego.cafeboon.com/docs.html).
>
> Team and Enterprise plans add the connector from Organization settings first. This repo, below, is the
> version for Claude Code and Codex on your own machines.

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
- **The Alter Ego connector**, a remote MCP server, is for chats in Claude, ChatGPT, Gemini and any AI chat with MCP, on the
  web or the phone, without installing anything. It logs every question by itself, so you do not have to put
  anything in your own account or settings, and you can have instructions saved for a client, project, task or tool.
  It keeps the memory in your own OneDrive, Google Drive, Dropbox, GitHub or Azure DevOps.

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

The core is six hooks and `note.py`, all plain Python with no dependencies, on Windows, macOS and Linux.
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
| `tools/session_start.py`, `auto_journal.py`, `save_session.py`, `block_ai_attribution.py`, `force_delegation.py` | The hooks: inject rules, log every turn, save the transcript, block AI attribution, push execution work to a cheaper agent |
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

## Concurrent writes

Two assistants can write to your memory at the same time, from this repo or through the connector. What
happens depends on the part that writes.

**This repo (hooks).** Every device has its own clone. `auto_journal.py` fetches, merges and pushes after
each turn. Journals (`**/journal/*.md`) use git's union merge, so lines from two sessions are both kept.
Any other file is a normal git merge: if two devices edit the same lines, git refuses the merge and the
sync reports it instead of overwriting anything. Git keeps the full history.

**The connector.** `remember` and `log` read the file, add to it and write it back (`update` in
`storage.py`). `write_file` replaces the whole file. Per user, storage and path the connector runs these
one at a time inside its process. On top of that, a write that carries the version it read is refused
when the file changed in between. The connector then reads again and retries, up to five times, and after
that it answers with an error and writes nothing.

| Storage | `remember` and `log` | `write_file` | History |
| --- | --- | --- | --- |
| GitHub | file `sha` is checked, retry on a conflict | same check, but it writes your text again after a retry, so the last write wins | one commit per write |
| Azure DevOps | the branch head is checked, retry on a conflict | same check, last write wins | one commit per write |
| OneDrive | `eTag` is checked, retry on a conflict | no check, last write wins | none from the connector |
| Dropbox | file `rev` is checked, retry on a conflict | no check, last write wins | none from the connector |
| Google Drive | no version check, only the lock inside the connector | no check, last write wins | none from the connector |

So two assistants that log or remember at the same moment both get their line saved on every storage,
as long as they go through the same connector. On Google Drive a change made outside the connector
between its read and its write, such as a manual edit, is overwritten. Two assistants that use
`write_file` on the same file at the same moment end with the text of the one that wrote last, on every
storage. The connector does not read, compare or restore older versions. OneDrive, Google Drive and
Dropbox keep file versions themselves, according to your own account and plan.

## Requirements

- Claude Code (any plan that supports hooks), optionally Codex.
- Python 3.8 or newer, git, and a private Git remote.
- Windows, macOS or Linux for the core. See Optional above for the parts tied to one system.

## License

MIT, see [LICENSE](LICENSE).
