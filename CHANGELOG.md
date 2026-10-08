# Changelog

All notable changes to this template are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

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

[0.3.0]: https://github.com/SebastiaanBoon/cloud-alter-ego/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/SebastiaanBoon/cloud-alter-ego/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/SebastiaanBoon/cloud-alter-ego/releases/tag/v0.1.0
