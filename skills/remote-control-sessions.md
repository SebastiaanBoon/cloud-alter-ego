# Resume Remote Control sessions

Use this when the user asks to "start the agents", names a session ("General", a client or project
session), or reports that a session is offline ("I cannot reach it", "it is gone from the list").

With Remote Control you steer a Claude Code session on your computer from your phone or any browser.
Long-running named sessions ("General", one per client, one per project) are worth keeping: they
hold their history. When you ask to "start the agents" or a session by name, it always means:
resume the existing sessions on their original session id. Do it right away, without questions.

## 1. Check the login first

```
claude auth status
```

Continue only when `loggedIn` is `true`. Otherwise log in once with `/login` in an interactive
session. Processes started while Claude was logged out do not get Remote Control after the login;
stop and restart them.

## 2. Start them

Put your sessions in `tools/sessions.json` (copy `tools/sessions.example.json`): name, session id,
the folder the session was originally started in, and whether to skip permission prompts. Then:

```
powershell -ExecutionPolicy Bypass -File tools\start_agents.ps1
```

The script checks the login, closes old processes on the same session ids and opens one window per
session with `claude --resume <id> --remote-control "<name>"`.

## Fixed rules

- Always `--resume <original id>`. Never a new session with the same name, never `--fork-session`.
- Never `--bg`: that creates copies with new ids instead of resuming.
- Resume from the original working directory, otherwise `--resume` cannot find the transcript.
- Unattended sessions: `--dangerously-skip-permissions` (set `skipPermissions` in sessions.json).
  Not `--allow-dangerously-skip-permissions`: that only makes it an option, it does not turn it on.
- Do not put the session that runs the script in sessions.json; it would close itself.
- Only use an elevated shell when the work in that session needs admin rights.
- Start sessions with `--chrome` if they have to use Claude in Chrome: without that flag the session has no
  Claude in Chrome tools. Set `chrome` in sessions.json if your start script supports it, otherwise add the flag.

## Naming (optional convention)

If you run sessions on more than one machine, start every session and routine name with where it runs,
for example `H-` server, `W-` work laptop, `T-` own computer, `C-` cloud routines. Pick your own letters
and keep them. When a session moves to another machine, move the existing session (copy the transcript,
`--resume <original id>` with the new name). Never start a new session next to the old one.

## Rename a running session

Rename only from inside the running session with `/rename <name>`. That sets the `customTitle`, which is
the name the app shows. Never restart a session to rename it: a restart closes the Remote Control session
in the app, and `--remote-control <name>` does not change the displayed name.

- Windows, hidden windows: `tools/type_into_session.ps1` finds the `claude.exe` of the session and types
  into its console. Type in chunks with a pause: `/rename`, a space, each word of the name (spaces
  separately), then Enter. Typing it in one go fails for names with spaces.
- Linux: see [techniques/linux-server-sessions.md](../techniques/linux-server-sessions.md).

## Find a session id

The id is the file name of the transcript that carries the session name:

```
cd ~/.claude/projects && grep -l '"customTitle":"<name>"' */*.jsonl
```

## 3. Check

```
Get-CimInstance Win32_Process -Filter "Name='claude.exe'" | Select-Object ProcessId, CommandLine
```

Exactly one process per session, with the original id and the right name. A running process alone
is not enough. Proof that Remote Control is really active is one of these:

- a fresh `bridge_status` line in the original transcript (the windows of the script are hidden);
- `/remote-control is active` in a visible window;
- the session shows as idle or running in the agent list.

No new `.jsonl` files may appear in `~/.claude/projects/`. Report per session in one line: name, active yes or no.

Two processes on one session id break logging: the transcript stops being written. auto_journal.py
then writes a WARNING line in the journal. Stop the oldest extra process, never your own.

## Resume dropped sessions on their own id

`tools/watch_sessions.ps1` is a watchdog for the sessions in sessions.json. Run it every 5 minutes and at
logon (a Windows scheduled task). Each session without a `claude.exe` is resumed on its original id. If
the transcript shows it was in the middle of a task, a short "continue where you were, do nothing if you
were done" prompt is typed into its console. Idle sessions get nothing. A session you closed on purpose
must be removed from sessions.json, otherwise it comes back.

## Session stays offline

Do not keep guessing with variants. In this order:

1. The process runs but nothing new appears in the transcript: it waits for a question in its window.
   Start it again with a visible window and look at the screen.
2. "Is this a project you trust?": trust is stored per path string in `~/.claude.json`
   (`projects.<path>.hasTrustDialogAccepted`). An elevated window starts in another path spelling than a
   normal one. Back up the file and write it atomically, running processes write to it too.
3. `loggedIn` is true but there is no Remote Control, and a browser shows a sign-in page: an agent cannot
   fix that, the user has to sign in. Restart afterwards.
4. Started while logged out: stop the old processes and restart them normally.
5. All processes gone at once: they were tabs in one terminal window. Always one window per session.
6. Why they went offline: usually a scheduled system restart (event 1074 in the System log).

Linux server: one service per session is described in
[techniques/linux-server-sessions.md](../techniques/linux-server-sessions.md).

## Git sync warning

The journal tool commits and pushes after every question and answer, and the session start script fetches the
remote. Both merge (no rebase, no autostash) and write the outcome to `.auto-journal/sync-status.json`. When the
sync stalls, a WARNING about the sync appears at session start and at every question. Then do this first, yourself:

- `git status -sb` and `git stash list`. A stuck `.git/rebase-merge` or `rebase-apply` older than 10 minutes is
  cleaned up by the sync itself (the autostash goes to the stash list). A hanging merge: resolve the conflict and commit.
- Look at every autostash (`git stash show -p`), restore what is still missing, then rename it to
  "checked <date>: ..." (`git stash drop` and `git stash store -m ... <sha>`). Never throw it away.
- Never stash, reset or overwrite the work of another session in the working folder.
- Push to the default branch and report back in one sentence.

## Accidentally made a copy

`claude rm <id>` for background sessions, close elevated processes with `Stop-Process` from an admin
shell, then delete `<id>.jsonl` and the folder `<id>` in `~/.claude/projects/<project>/` so they no
longer show up in /resume.
