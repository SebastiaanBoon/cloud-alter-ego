# Timesheet proposal at the end of the day

Use this when the end-of-day routine `timesheet-proposal` runs on working days, or when the user asks "how do I
write my hours today", "timesheet proposal" or "what do I put in the time tracking tool". Goal: a proposal of hours
per client and activity for today, based on the journals and the calendar. The user approves or changes it.

At the top of the answer: last week (Monday to Sunday) and, if hours are already in, this week separately: per
client the hours and the user's own remarks from the time tracking tool, as a cheat sheet for a weekly update meeting.

## Steps

1. Read the lessons: `skills/learnings/timesheet-proposal.md`. The rules there come first.
2. What is already in and which activities the user uses: read the month from the time tracking tool (through a
   small tool in `tools/` that uses the signed-in browser profile). Note the lines of today and, per client, the
   activity used in the last 10 working days. At a month change: the new month activity if it is in the timesheet,
   otherwise the last used one.
3. Last week and this week: per project, with hours and the remark of each cell. Make a total per client and two to
   four bullets of what was done, summarised from the remarks (tickets and subjects, no repetition per day). Order:
   client support, projects, internal. Leave out leave and kilometres.
4. What the user did today, with times:
   - The journals of today (`clients/*/journal/<YYYY-MM>.md`, `projects/*/journal/<YYYY-MM>.md`), lines under
     today's heading. Every line has a time (`- 10:15 ...`). Client = folder. `_unsorted` only if the work clearly
     belongs to a client or internal project.
   - Today's calendar through the calendar connector: a client meeting counts for that client.
   - Do not read mail and chat, only when a journal line refers to it.
5. Estimate hours per client:
   - A block is the first to the last journal line of an uninterrupted series (a gap over 30 minutes starts a new
     block), plus the duration of calendar appointments. Round to a quarter, minimum 0.25.
   - Loose short lines (ticket read, message answered) without a block: 0.25.
   - What is already in the tool counts as fact: propose only the difference and say what is already there.
   - No source, no hours. Invent nothing to reach a full day. Do report how many hours are covered in total today.
6. Choose the activity:
   - Support contract of the client: the activity from step 2.
   - Project work with its own project: the consultancy activity on that project.
   - Own platform, knowledge, tooling, monitoring, skills: the internal hours activity. Own side projects and
     personal projects are never booked.
   - In doubt between support and project: support if it is a ticket or incident, project if it is new work.
7. Remark per line: a few words like the user writes them, no internal details, no dashes.
8. Answer in the chat, first the week, then today:
   ```
   Last week (19 to 25 Oct), 40 hours
   <Client> 3.25: tickets ..., ... / short remark / short remark

   This week (26 and 27 Oct), 12.75 hours
   ...

   Timesheet proposal Tue 27 Oct (covered 6.5 hours, already in the tool 3.25)
   | Client | Activity | Already there | Proposal | Remark |
   ```
   Below that at most two lines: what is uncertain, and the question "Shall I fill this in?". Writing in the tool
   only happens after approval.
9. After approval ("yes", with or without changes): per line set the hours through the tool, read it back and give
   the new state. If the tool cannot set remarks yet, give them so the user can paste them, or extend the tool.
10. Learn: at the end of every run append a log line in `skills/learnings/timesheet-proposal.md` according to
    [routines](routines.md). When the user changes the proposal, that is the most important lesson (which client,
    which activity, which estimate).

## Rules

- Read only until the user approves. Never submit or have anything approved.
- No client names or work of one client in the remark of another.
- Never close the user's own browser.
- Fetching (time tracking, journals, calendar) may be done by a mid-size model agent; estimating and the proposal
  happen in the main session.

## Check

Is every hour in the proposal backed by a journal line or calendar appointment, and did you report the total covered
hours? After writing: did you read the tool back and name the new state?

## Self-learning

Read the lessons file at the start and append one line at the end, also when the run failed.
