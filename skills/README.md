# Skills

Runbooks an agent follows top to bottom when you ask for that task. Keep each one concrete: exact
commands, checks, and the mistakes that were made before. Add your own as you go.

Every skill starts with a "Use this when" line, then the steps, then a check step. Recurring skills and
routines end with a self-learning step: a correction from the user goes into the skill straight away.

## Core

How the agents work for you, useful whatever your job is.

| Skill | When |
|---|---|
| [remote-control-sessions](remote-control-sessions.md) | "Start the agents" or a session by name: resume your Remote Control sessions |
| [context-doctor](context-doctor.md) | Check-up of this repo: git state, structure, duplicates, local agent memories |
| [client-message-writing](client-message-writing.md) | Any mail or ticket message to a client: template, checklist, keeping the user's voice |
| [routines](routines.md) | Scheduled routines (local, cloud or server cron) that read and append their own lessons in `learnings/` |
| [when-it-fails](when-it-fails.md) | Before you write "cannot", "not supported" or "you have to": the ladder of routes to walk first |
| [model-routing](model-routing.md) | Who does what: main session, client chats, Sonnet agents and Haiku bulk work |
| [token-economy](token-economy.md) | Measure and reduce what sessions, routines and subagents cost of the plan limit |
| [signing-in](signing-in.md) | The order to try before any login, and what never to do |
| [devices](devices.md) | Before you hand work over or say "cannot": which device and session can do what, and how to avoid double work |
| [writing-style](writing-style.md) | Write a message to a client or outside party in the user's voice: form, tone, checklist |

## Examples from real work

Runbooks for one kind of work (data platforms, client tickets, sales, investing). Keep the ones that fit your
work, delete the rest, or use them as a model for your own.

| Skill | When |
|---|---|
| [whatsapp-web-reading](whatsapp-web-reading.md) | Let an agent read your WhatsApp messages through WhatsApp Web and the Claude extension in Chrome |
| [client-presentation](client-presentation.md) | A slide deck for a client, co-branded with their house style |
| [lead-outreach](lead-outreach/README.md) | Find local businesses with an outdated or missing website and prepare personal email drafts |
| [devops-board-update](devops-board-update.md) | Update an Azure DevOps board or backlog with the work that was finished |
| [pipeline-incident](pipeline-incident.md) | A failed run, empty table or "the numbers are wrong" on a data platform: find the real cause, repair only the affected part |
| [ticket-analysis](ticket-analysis.md) | Fill in environment, root cause and analysis on helpdesk tickets from the conversation, review list first |
| [morning-routine](morning-routine.md) | Morning overview of mail and tickets, with the client agents analysing each item |
| [timesheet-proposal](timesheet-proposal.md) | Propose time entries for today from the journals and calendar, plus a weekly cheat sheet |
| [ai-usage-indicators](ai-usage-indicators.md) | Weekly refresh and post of the "AI usage per day" page from public usage data |
| [stock-analysis](stock-analysis.md) | Analyse a stock screener export: check the data, research candidates, rank them |
| [loop-page-editing](loop-page-editing.md) | Read and edit a Microsoft Loop page through a signed-in browser |
