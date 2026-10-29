# Morning routine: ticket system and mail to the client agents

Use this when the user asks for the morning overview, or when the scheduled morning routine runs. Goal: the user
does not have to fetch anything. Per item they get the analysis of the client agent, and then they answer
themselves in chat, the ticket system or mail.

## Where it runs

A scheduled session on the machine that has the browser and mail connector, on working days: the full routine at
the start of the day, a lighter run later in the morning (ticket system only, only what is new since the first
run), a keep-alive every quarter of an hour and usage-limit watching. A schedule that lives only as long as the
session is open expires after a few days: set it again. The machine stays on mains power with the lid open. Keep
lessons and a log in a lessons file (see Self-learning).

## Model per task

- Keep-alive and limit watching: a small, fast model that only returns "ok", "logged out" or "limit".
- Fetching and summarising mail and tickets: a mid-size model that returns per item client, source, date and the
  full content.
- Classifying, steering the client agents and the overview: the main session itself.
- Several missed scheduled prompts in the queue: run once, not once per prompt.

## Steps

1. **Mail.** Mail connector, inbox since the previous run plus everything still open (unread, flagged, or a client
   mail without an answer from the user after it). Skip newsletters, notifications without action and the user's
   own sent mail. A mail that is already a ticket counts as a ticket, not twice.
2. **Ticket system.** Through Claude in Chrome, the browser profile that is signed in, on the pending tickets view
   sorted by newest. Read the list and open new tickets and tickets with a new client message, also when they are
   not assigned to the user; those matter most. Add the notification mails of the ticket system. Never close the
   tab, never sign in yourself. A sign-in page: send a push notification, note it in the overview, continue with
   the mail. Do not suggest an API key and do not have notification settings changed.
3. **Sort per client.** Use the slugs from the repo's main instructions. In doubt about the client: put it in the
   overview, do not guess.
4. **Steer the client agent.** Per client send a message to the session named after the client:

   | Client | Session |
   |---|---|
   | `<client>` | `<session id or name>` |

   No session for the client: note in the overview that the user has to create that chat, with the assignment text.
   Assignment text: ticket number or mail subject, sender, date and the full content, with "Find out what is going
   on and what is needed. Analysis and a draft reply only, send nothing, change nothing in the ticket system,
   deploy nothing. Send your analysis back to session `<this session>` with a message."
5. **Optional daily data check per client.** If a client has a known fragile load, run the client's check tool (for
   example one that lists empty tables in a bronze layer). A table that is empty although the copy says Succeeded
   goes to the top of the overview, with the last Delta commits. Never restart the pipeline yourself. If the tool
   says the workspace cannot be found, the elevated role is not active: report that, do not activate it yourself.
   When you promised a client a daily confirmation, only confirm after you verified the data in the layer the client
   sees; the SQL endpoint there can lag for hours, so look again and never confirm earlier. Draft in the overview
   only, send nothing.
6. **Overview.** A short list: per item client, source, one line on what it is about and to which agent it went.
   When analyses come in, per item the core plus a draft reply ([client-message-writing](client-message-writing.md),
   chat informal, business contacts through the ticket system). Send a push notification when the overview is ready.

## Keep-alive

Refresh the ticket system tab and check with a page text read that it is not a sign-in page. Works: report nothing.
Sign-in page: push notification "ticket system logged out" and note the time in the lessons file.

## Limit watching

Read the usage. If 5% or less of the five-hour limit is left, stop the running turn of every other session that is
running, never this session. Report once per reset window with a push notification.

## Rules

- Never reply to a client yourself, send no mail, change no ticket.
- Do not steer an agent on something that is already handled (an answer from the user after the last client message).

## Check

Does every open item from mail and ticket system appear in the overview or in a client agent's assignment, and did
you send nothing outward?

## Self-learning

Read the lessons file at the start. At the end of each run, also a failed one, append one line:
`YYYY-MM-DD | what worked | what failed and the real cause | what the next run does differently`. Follow
[routines](routines.md).
