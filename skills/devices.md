# Devices: who can do what

Use this when you are about to hand work to another session, or about to write that something cannot be
done. It tells you which device and session can do a task. Without it, sessions said they could not do
something that another device could do, and one task (reading a social media reel) went to two sessions at
the same time. When these facts are no longer true, update this file right away.

## 1. Fill in your own overview

Keep one table with a row per device. Use the letter prefix of your session names (see
[remote-control-sessions](remote-control-sessions.md)).

| Device | Sessions | Can | Cannot | Is on |
|---|---|---|---|---|
| `<server>` (small always-on Linux server, no root) | `<sessions and routines in tmux>` | Cloud CLI with the key vault, posting through API tokens, systemd user timers, git push to own repos, a server browser with remote desktop for a one-time login from a phone | Log in to services that block a new device on a datacenter address. Read content of others that needs a login. Work for clients if you agreed so | Always |
| `<work laptop>` | `<sessions>` | Claude in Chrome, signed in to the work accounts. Browser profiles per client. Tokens and tools that only exist on this machine. Work connectors for work mail and chat | Always being available. Key vault writes and tokens are often refused by the permission classifier in one session, then a session with wider permissions does that | Only when it is working. Does not sleep on mains power |
| `<own computer>` (Wi-Fi only) | `<sessions>` | Claude in Chrome with the personal logins. Windows management of the computer. A watchdog that resumes the sessions | Wake-on-LAN (Wi-Fi only). Changing scheduled tasks to run without a logon needs an elevation click by the user at the computer | Mostly on. A system update restarts it at night |
| Cloud (claude.ai routines) | `C-*` | Schedules (cron) and work that needs only the repo and connectors. Dispatch to the server with a script | Reaching the server directly (connect rejected) or Remote Control sessions. Package installs through the proxy can return 403 | Always |

What runs where and when: the routine registry of this repo. How sessions start and recover:
[remote-control-sessions](remote-control-sessions.md). Logins per system: [signing-in](signing-in.md).

## 2. Which work goes to whom

| Work | Goes to |
|---|---|
| Routines, posting, cloud CLI, reading the key vault, your own sites and repos | the server |
| Settings of a social media account or app, anything that needs a login in a browser | the machine with Claude in Chrome signed in, otherwise the other one |
| Client work (ticket system, data platform, time tracking, chat) | the work laptop |
| Something on the computer itself (tasks, watchdog, Windows) | the session on that computer |
| The classifier refuses a token or key vault write | Tell the user. Only when the user puts that exact request in the session with wider permissions does it happen there (no permission laundering) |

## 3. Work together without double work

- **One task, one session.** Give a task to one session and wait for it. If it is in requires_action or does not
  respond and you give the work to another session, first send the first one a stop message, and state in both
  messages who does it now.
- **Look who is free first.** Check the agent list before you hand work over. Do not message a session that is busy.
- **Everything in the assignment.** Every assignment stands on its own: who asks, what exactly has to happen, what
  has to come back, and the rules word for word.
- **Approval in their own chat.** Some sessions do nothing that goes outside without the user's approval in their
  own chat (for example a session that handles an external organisation). Say in one sentence where the user's
  "yes" is needed.
- **Results come here.** Findings go to the chat where the user is, even if another session did the work.
- **Wait without confirmation.** Remote Control does not confirm that a message was read. Wait for the answer and do
  not say it is arranged before the answer is there.

## Check

Before you hand work over: did you check the table for the right device, check that the session is free, and put
the full assignment in one message? Before you write "cannot": did you check this table for another device?

## Self-learning

A new fact about a device (a block, a new capability, a changed schedule) goes in the table straight away, with
the date.
