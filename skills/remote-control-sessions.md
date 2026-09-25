# Resume Remote Control sessions

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
is not enough: the window must show `/remote-control is active`, or the original transcript must
contain a fresh `bridge_status` line. No new `.jsonl` files may appear in `~/.claude/projects/`.

Two processes on one session id break logging: the transcript stops being written. auto_journal.py
then writes a WARNING line in the journal. Stop the extra process.

## Accidentally made a copy

`claude rm <id>` for background sessions, close elevated processes with `Stop-Process` from an admin
shell, then delete `<id>.jsonl` and the folder `<id>` in `~/.claude/projects/<project>/` so they no
longer show up in /resume.
