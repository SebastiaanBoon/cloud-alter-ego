# Scheduled routines that learn

A routine is a prompt that runs on a schedule without you. Keep the prompt short and let it point at a
skill (the runbook); the routine adds one thing on top: it learns from every run.

## Where a routine runs

| Where | How | Good for |
|---|---|---|
| Local scheduled task | Windows task "Routine <name>" running `tools/run_routine.ps1 -Name <name>` | Work that needs your computer, logins or browser |
| Cloud routine | claude.ai routine with the prompt from `tools/routines/<name>.txt` | Work that needs only the repo and connectors; the computer can be off |
| Server cron | `tools/run_routine.sh <name> [hours]` from cron, see `techniques/linux-server-sessions.md` | Always-on work on a small server |

A claude.ai routine can also dispatch to the server: when the work needs something the cloud cannot reach (a
package registry behind the proxy, a posting key, a signed-in browser), name the routine `H-<name>` and let it run
a dispatch script that starts the server launcher `tools/run_routine.sh <name>` with the prompt from
`tools/routines/<name>.txt`. The server then runs it as a visible Remote Control session in tmux. Keep old cloud
versions of such routines switched off, and never change a schedule without the owner asking.

Put the prompt in `tools/routines/<name>.txt` (see `example.txt`), keep a table of routines, schedules and
runbooks in the context that owns them, and never change a schedule without the owner asking.

Both launchers take "run only in these local hours", so a cron or task set in UTC or retried after a
logon does not run at the wrong time.

## Anti double-run

- The launchers hold a lock (`flock` on Linux, a named mutex on Windows) for the whole run: a second start
  exits with "skipped" in the log.
- For routines that create something external (a post, a mail, a record), the runbook must first check
  what already exists today and only do what is missing. A retry then never repeats a success.
- A running session is not proof of a result. Check the outcome, not the process. A dispatch or an online Remote
  Control session does not prove that something was published: check the posts or records.
- A routine on the server closes its own session as the very last step: write the result message to the
  routine's result file, then end the tmux session (`tmux kill-session -t routine-<name>`). A session that stays
  open keeps the lock, and the launcher skips every next dispatch as "already running".

## Per run: skills/learnings/<routine>.md

1. **Start:** read `skills/learnings/<routine>.md` (create it with the headings from
   `skills/learnings/README.md` if missing) and follow its rules. They beat your own approach; the runbook
   stays leading for what has to happen.
2. **End, always, also when the run failed:** append one line under `## Log`:
   `YYYY-MM-DD | what worked | what failed and the real cause | what the next run does differently`.
3. **Tidy:** a lesson that comes back twice, or clearly always applies, becomes a short rule under
   `## Rules` and the loose log lines about it go. Drop rules that are no longer true. Keep the file
   under 120 lines.
4. **Save:** commit and push only that one file, without AI attribution:
   ```
   git add skills/learnings/<routine>.md
   git commit -m "Lessons <routine> <date>"
   git pull --rebase origin <branch> && git push origin HEAD:<branch>
   ```
   A cloud routine uses the repo's default branch. If pushing fails, say so in the final message.
