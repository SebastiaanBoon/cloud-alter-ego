# Client environments

Rules for work inside a client's environment: their data platform, their CI and their reports. They used to sit
in preferences.md; they live here so the rules injected into every session stay short for people who never touch
a client environment. preferences.md points here, so an agent reads this file before such work.

- Never start pipelines, notebooks or jobs in a client environment, also not in dev, unless literally
  asked to run. After a drop, report what has to be reloaded. No test files there.
- Before dropping a table: read how the load code creates it (a MERGE fails next run). In doubt, no drop.
- Changing an item in a client environment makes your account its owner (it stops when an elevated
  role expires): report the owner, get approval, then read back owner, status and next run.
- Clients: build and deploy through the client's own CI. Build containers in the pipeline. Git Bash
  turns `/home/data` in az arguments into a Windows path: set `MSYS_NO_PATHCONV=1`.
- Rebuilding an export or report: list every source field and build all of them; never quietly
  deliver less. A sync from a tool: only real changes, no formatting noise.
- Mail drafts through Microsoft Graph: HTML body, one `<p>` per paragraph.
