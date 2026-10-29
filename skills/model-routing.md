# Model routing: who does what

Use this for every task that is more than a direct question. The main session coordinates, judges and
checks. The research and the doing go to the cheapest place that can handle it, because the plan limit
is shared by every session.

## Routing

| Kind of work | Goes to | How |
|---|---|---|
| Judgement, checking a diagnosis, reviewing a client message, a short answer | the main session | yourself, short |
| Research for a client (an incident, an estimate, a capacity question) | the existing chat for that client | list the sessions, then send a message with the client name in it |
| A client without a chat | a new chat named after the client | the user creates it, or spawn it with the client name as title. Do not send it a second time |
| Research or building in your own project | a Sonnet agent in the background | the Agent tool with `model: "sonnet"` and `run_in_background: true`. Follow-up questions go to the same agent, it keeps its context |
| Big but simple work (labelling, writing explanations, summarising, fetching) | Haiku agents | at most 5 at the same time, every item exactly once, see below |

Never use the most expensive model for subagents.

## The assignment to a chat or agent

Always self-contained, because the receiver does not see this conversation:
- The ticket number, who asked, what was asked, and the ids (job id, capacity name).
- What it has to deliver: a diagnosis or an estimate plus a draft message.
- The relevant rules, literally: read only, start or change nothing in the client environment, send
  nothing, invent no values, no em dashes, one journal line with `note.py`.
- For your own projects: exact paths, what already runs (do not start or stop it), a backup of the data
  first, delete nothing, do not commit, report briefly.

## Bulk work with Haiku

1. The main session exports the items to `scratchpad/<task>/batch1..5.json`, with every field needed.
2. Five Haiku agents in parallel, one batch each. The assignment: write `{id: result}` to `out<n>.json`
   and answer only with the count, so no dump lands in the main context. Always name the language of the
   output: that of the product, not that of the chat.
3. The main session merges and checks: missing and extra ids, empty values, dashes and semicolons. Then a
   backup of the database, and only then import.
4. Doubts that Haiku reports ("this key looks wrong") are judged by the main session against the source.
   Haiku never has the last word.

## Reporting back

- Pass results on briefly, with what was not verified ("not checked visually").
- A report that contradicts an earlier report or the journal: say so and let the chat sort it out. Do
  not take it over as fact.
- Follow-up questions go to the same chat or agent, do not research again yourself.

## Check

Is the work in the cheapest place that can do it, does the assignment stand on its own, and did the main
session verify the result instead of copying it?
