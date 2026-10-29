# Changelog

All notable changes to this template are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [0.5.0] - 2026-10-29

### Added

- Skills `when-it-fails` (the ladder to walk before writing "cannot"), `model-routing` (who does what,
  bulk work with the smallest model), `token-economy` (measure and reduce what sessions cost) and
  `signing-in` (the order to try before any login).
- `tools/token_usage.py` shows token use per session, subagent and routine for a time window.
- `tools/session_start.py` sets `autoCompactWindow` and the idle-compact and subagent-model environment
  variables when they are missing.
- Sync health: `tools/auto_journal.py` writes `.auto-journal/sync-status.json`, repairs a stuck rebase or
  merge, and prints a warning at the next prompt and at session start when the sync is stuck.
- Working rules with background: fix the cause, build with the environment, a ticket means only that,
  changing a client item makes you its owner, done means saved and synced, no draft while the
  investigation runs, one session per ticket, and offer a phone route when the user is away.

### Changed

- `tools/auto_journal.py` pulls with fetch and merge instead of rebase and autostash, and pushes to the
  named branch.
- `preferences.md` is shorter, so it stays under the 9,000 character limit.

### Fixed

- `tools/server/session-state`: a notification arriving during a turn now clears finished background
  tasks instead of being skipped.

## [0.4.0] - 2026-10-15

### Added

- The journal context is per session (`.current-context.d/<session id>`, `note.py --session`, and
  `--global` for the device default), so parallel sessions no longer write into each other's journal.
- `tools/watch_sessions.ps1` resumes dropped Remote Control sessions from `tools/sessions.json` on their
  own id, and `tools/type_into_session.ps1` types into a running session, for example `/rename`.
- A scheduled-routine runner (`tools/run_routine.sh`, `tools/run_routine.ps1`, `tools/routines/`) and
  the self-learning pattern: a routine reads `skills/learnings/<routine>.md` at start and appends its
  lessons after every run (`skills/routines.md`).
- A Linux server kit (`tools/server/`): a systemd unit per Remote Control session that continues after
  an outage, a `batch` wrapper that throttles heavy jobs, and a load guard, explained in
  `techniques/linux-server-sessions.md`.
- Skills `client-message-writing` and `devops-board-update`. Skills follow one structure: when to use,
  the steps, a check step and, for recurring work, a self-learning step.
- Working rules with background: the answer in the first sentence, do it yourself, what was switched
  off stays off, no sign-in popups, continue another agent's work, done only after the real result
  through the real route, report the real error, a broad search before "nothing found", check where
  something runs, split long tasks in parallel, and installer tests only with an isolated `HOME`.

### Changed

- `remote-control-sessions`: rename a running session with `/rename`, one process per session, how to
  prove Remote Control is active, and an offline checklist. `client-presentation` and
  `whatsapp-web-reading` start with when to use them and end with a check.

### Fixed

- A question sent during a running turn now counts as the prompt, and task notifications,
  cross-session messages and local command output are no longer logged as questions. This removes a
  false "transcript not written" warning.
- `save_session.py` keeps one copy per session and skips transcripts over 50 MB.

## [0.3.0] - 2026-10-08

### Added

- Working rules with background: client builds and deploys through the client's own CI with containers
  built in the pipeline, the Git Bash path conversion for az, visible agent work, no offers the user
  did not make, tone in documents the reader reads, updating existing client documents, and mail
  drafts through Graph as HTML.
- Technique `entra-id-and-oauth`: an MCP server behind Entra ID (client credentials for Claude, the
  AADSTS9010010 resource rule, access through Assignment required and app roles, a role for a group
  of key users, on-behalf-of).
- Technique `azure-app-service`: persistent data under `/home`, the Kudu VFS API, a quiet log stream,
  and syncing app data to git through the pipeline instead of a token in the app.
- Skill `client-presentation`: one message per slide, and only what is asked when updating a deck.
- Skill `whatsapp-web-reading`: pairing with a phone number, background tabs and reading poll votes.

## [0.2.0] - 2026-09-30

### Added

- `.gitattributes` with a union merge for journals (`**/journal/*.md`). Parallel sessions and devices
  append to the same journal; a pull with rebase now keeps both sides instead of stopping on a conflict.
- Skill `client-presentation`: co-branded slide decks for a client, reusing an existing format first,
  with slide copy rules and three checks when no visual render is available.
- Skill `context-doctor`: periodic check-up of the repo covering git state, unmerged branches, indexes,
  duplicate facts, local agent memory files and agent instruction files.
- Technique `microsoft-365-groups-and-guests`: device-code sign-in to a second tenant, inviting guests,
  finding dead addresses from bounces and automatic replies, and moving leavers to an archive group.
- Working rules with background: work in the user's own folder, keep solutions simple, "push" means
  all pending work, permission to run applies once, rebuild every field of an export, only real
  changes from tool exports, report done only after a full check, never use a pasted password, write
  messages in the user's voice, and move knowledge out of local agent memory files.
- Project template section for project-specific skills and tools.

### Fixed

- `save_session.py` aborts a failed `pull --rebase` instead of leaving the repo halfway through a
  rebase, which blocked every later hook. The local commit goes out with the next successful save.

## [0.1.0] - 2026-09-25

### Added

- First release: session hooks (auto journal, session save, session start), installer with uninstall,
  attribution block hook, Codex notify chaining, default working rules, skills and techniques.

[0.5.0]: https://github.com/SebastiaanBoon/cloud-alter-ego/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/SebastiaanBoon/cloud-alter-ego/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/SebastiaanBoon/cloud-alter-ego/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/SebastiaanBoon/cloud-alter-ego/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/SebastiaanBoon/cloud-alter-ego/releases/tag/v0.1.0
