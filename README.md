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

| Path | What |
|---|---|
| [preferences.md](preferences.md) | Working rules injected at every session start. Sensible defaults for style, scope, code and facts; edit them |
| [preferences-background.md](preferences-background.md) | The reasoning behind every rule |
| [identity.md](identity.md) | Who you are: role, stack, how you work with agents (template) |
| [personal.md](personal.md) | Optional personal context (template) |
| [clients/](clients/README.md) | One folder per client: README with stack and incident history, `journal/`, `sessions/` |
| [projects/](projects/README.md) | One folder per own project, plus the infrastructure they share |
| [skills/](skills/README.md) | Runbooks: resume Remote Control sessions, read WhatsApp Web, lead outreach |
| [techniques/](techniques/README.md) | Reusable technical knowledge: Fabric, fabric-cicd, dbt, Databricks, Azure, Entra ID, Power BI, Git |
| [WORKFLOW.md](WORKFLOW.md) | How the hooks, contexts and syncing work |
| [tools/](tools/) | The scripts behind it all |

## Daily use

- Tell the agent what you are working on, or set it yourself: `python tools/note.py --set acme`.
  The agent reads that client's README and newest journal before it starts.
- The agent writes one meaningful journal line per turn. The automatic lines from the hooks are a
  safety net, the agent's line is the summary a future session needs.
- When a session teaches you something reusable, it goes into `techniques/`. A new working rule goes
  into `preferences.md`, with the story behind it in `preferences-background.md`.

## Privacy and safety

- Your copy must be **private**: transcripts and journals are pushed automatically. The installer
  warns when your remote is public.
- Never store secrets here. Resource names are fine, keys and passwords are not.
- `.current-context`, `.auto-journal/` and `tools/sessions.json` are local and gitignored.
- The hooks never fail hard: errors go to `.auto-journal/errors.log` and a session never gets stuck.

## Requirements

- Claude Code (any plan that supports hooks), optionally Codex.
- Python 3.8 or newer, git, and a private Git remote.
- Windows, macOS or Linux. `tools/start_agents.ps1` is Windows only.

## License

MIT, see [LICENSE](LICENSE).
