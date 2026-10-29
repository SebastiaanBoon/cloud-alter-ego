# Ticket analysis: root cause and analysis fields

Use this when someone asks "do the ticket analysis", "fill in root cause and analysis" for a client, or when it runs
as a monthly routine. Goal: every ticket in the chosen view of the ticket system has an environment, a root cause
and a short analysis, based on the ticket conversation. First a review list, write back only after approval.

## Settings

Fill these in once before you use the skill (keep them in `clients/<slug>/`).

| Setting | Value |
|---|---|
| Ticket system tenant | `<tenant>` |
| View with the tickets | `<view id and name>` |
| Excluded tickets | `<ticket numbers that stay empty on purpose, or none>` |
| Folder for the rounds | `<path where each round gets its files>` |

## The three fields

| Field | Type | Values |
|---|---|---|
| Affected environment | multi-select | DEV, TST, ACC, PRD |
| Analysis root cause | single choice | see below |
| Analysis comment | text | one or two short sentences |

The option ids differ per tenant: fetch them with the field options endpoint of the ticket system.

## Root cause categories

Use the definitions your client uses. A usable default:

1. External data source issue: the cause lies with the external source or its supplier. Examples: the supplier
   delivers no data or late data, file format or API changed, the source holds wrong or incomplete data, an
   external system is unavailable. Result: reports not available or not current.
2. Manual data source issue: the cause lies with manual input of source data. Examples: a manual upload misses
   files, a file with the wrong structure, columns, fields or encoding, incomplete or inconsistent input.
3. Code bug: an error in the code or configuration of the data platform. Examples: an error in a transformation or
   calculation, wrong data mapping, a configuration error in a pipeline, model or report, a change breaks something
   that worked.
4. Business process issue: the cause lies in a business process. Examples: data is not or insufficiently validated
   before use, unclear acceptance criteria, a changed way of working, a process step skipped or done wrong.
5. Unknown: the conversation gives too little indication for one of the four.

A failure of a platform or service outside your control (for example the cloud provider) is an external data
source issue. Re-running helped and nothing else is known: choose by what the messages say, otherwise Unknown.

## Steps

1. Fetch all tickets from the view, with per ticket the details (the three fields) and the full conversation.
   Use the web app's own API with the bearer token of the signed in user (valid for about 20 minutes), read from the
   browser page and never printed or stored. If an API key is not available to the user, do not suggest one.
2. Take only tickets where at least one of the three fields is empty. Skip the excluded tickets.
3. Read the conversation of each ticket and make a proposal:
   - Environment: from the tag in the subject (`[ACC]`, `[PRD]`), otherwise from the messages. No tag does not
     automatically mean PRD: read the messages.
   - Root cause: one category from the list.
   - Comment: one or two short, factual sentences in the language of the existing comments. What went wrong and how
     it was solved. No names of people, no dashes.
   - Confidence: high, medium or low, with a short note for inferences. Tickets with status New, Open or Waiting for
     Customer get confidence `open` and empty proposals.
   - Merged tickets get the values of the main ticket, with the comment "Duplicate of ticket X. Merged and closed."
4. Put the proposals in a review list (spreadsheet) with per ticket: number, subject, status, the proposals,
   confidence, note and a column "Approved? (y/n)". Open the list for the user. Write nothing yet.
5. Write back only after approval, only the rows with y. Fill in the environment only where it is empty. Through
   the update-fields call of the ticket system. A "no changes found" error means the value was already there.
6. Check all tickets again and report "N of M filled in" plus which tickets stay open and why.
7. Add a journal line with the ticket numbers filled in and what stays open.

## Rules

- Write nothing to the ticket system without approval on the review list.
- Change only the three fields: no status, assignment or escalation, and send no messages to the client.
- Never store or show a token.
- If the user asks whether a ticket has already gone to production: that is in the repository or release system of
  the client (pull request, merge, release), not in the ticket system. Do not open the ticket system first.

## Check

After writing back, the tool checks all tickets again. Report "N of M filled in" and which stay open (status open or
waiting), never only "done".

## Self-learning

As a routine: read `skills/learnings/ticket-analysis.md` at the start, append one line at the end, also when it
failed, according to [routines](routines.md). A correction of a proposal by the user is the most important
lesson: which wording or category was changed, and why.
