# Linux server for agent sessions

Running Claude Remote Control sessions on a small VPS (for example 2 vCPU / 4 GB). Files are in
`tools/server/`; install with `sudo bash tools/server/install.sh <agent-user>` (idempotent). Scale the limits
to your machine.

## One systemd unit per session

- `claude-session@<name>.service` runs `run-session <name>`, configured by `/etc/claude-sessions/<name>.conf`
  (copy `tools/server/session.example.conf`: ID, NAME, CWD, optional MODEL).
- It always starts `claude --resume <original id> --remote-control <name>` inside its own tmux server
  (`tmux -L cs-<name>`), so every session has its own cgroup and memory limit. Without a transcript for that
  id it exits with code 3 and never creates a new session in its place.
- `Restart=always` with no start limit: a crash, OOM or reboot is temporary. The unit is enabled at boot.
- **Continue after an outage:** at every start `session-state` reads the transcript. If the session was
  halfway through a task (last message a tool call or result, an unanswered prompt, or a background command
  that is now gone), `run-session` types a continue prompt. Idle sessions get nothing.
- `claude-sessions.timer` runs `ensure-sessions` every 5 minutes to restart units that were stopped.
- Watch a session: `sudo -u <agent-user> tmux -L cs-<name> attach -t <name>`.

## Heavy jobs only through `batch`

- `batch <cmd>` runs in the foreground, `batch --service <name> <cmd>` in the background as unit
  `batch-<name>` (restarts on failure, logs via `journalctl -u batch-<name>`). Use `--service` for unattended
  runs such as cron: `0 4 * * * batch --service nightly $HOME/jobs/nightly.sh`.
- Jobs run in `batch.slice`: nice 19, one core, idle IO, `MemoryHigh` 1300M and `MemoryMax` 1500M. Sudoers
  allows only the `batch-run` helper, and the `--` stops a job from passing its own `systemd-run` options.
- Never start heavy Python, node or browser work plain.

## Load guard, swap, ssh

- `load-guard.timer` (every minute): above load 3 it freezes `batch.slice` (cgroup freeze) and sets helper
  processes of the agent user to nice 19; below load 2 it thaws it. Claude, tmux and sshd are left alone.
  Actions show in `journalctl -t load-guard`.
- Add swap (for example 4 GB, `vm.swappiness=10`) and `earlyoom` (acts at about 5% free memory and 10% free
  swap, prefers python and browser processes, never claude, tmux or sshd).
- `ssh-priority.conf` gives sshd a high CPU and IO weight and `OOMScoreAdjust=-900`, so the server stays
  reachable when everything else is busy.

## Pitfalls

- The crontab belongs to the agent user and is shared by all sessions. Always append with
  `(crontab -l; echo "...") | crontab -`, never write a whole new crontab: that deletes other sessions' lines.
- A job that holds everything in memory at once (a few GB) took a 4 GB server down twice. Process in batches,
  stream instead of loading everything, run it through `batch` so `MemoryMax` kills the job and not the
  server, and fix the job before considering a bigger machine.
- Windows-only work (Chrome extension, PowerShell, local logins) cannot run on the server; keep it on your PC.
