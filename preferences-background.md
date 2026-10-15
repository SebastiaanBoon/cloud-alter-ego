# Working rules: background

The reasoning behind every rule in preferences.md. This file is not injected, so it can be long.
When you add a rule, add it short to preferences.md and explain it here: what went wrong, and how
to apply the rule. Real incidents make rules stick far better than abstract advice.

## Never AI attribution

AI tools add `Co-Authored-By: Claude` or `Generated with Claude Code` to commits by default. On
GitHub that shows the AI as a second commit author, which many people and employers do not want in
their history. A system reminder can re-add it even when the rules forbid it, so the rule has three
layers: the rule in preferences.md, `attribution` set to empty in settings.json (install.py does
that) and a PreToolUse hook that blocks any command containing such a line.

**How to apply:** commit messages end after the content. If the hook blocks a command, rewrite it
without the line; never try to bypass the hook.

## No em or en dashes

Many readers see an em dash as the tell-tale sign of AI-written text. In client-facing content that
does damage. Use a period, comma, colon or semicolon, or rewrite the sentence. Watch out for dashes
in time ranges too ("Mon to Fri").

**How to apply:** before any commit or publication, search the changed files for both dash characters.

## Short answers with only the key points

Long answers read as evasive. A half screen of excluded hypotheses, log lines and background buries
the one thing that was asked. What works: the answer first ("yes, it works again"), then at most
what the user has to do. Bullets are fine; the problem is never bullets versus sentences, it is
length and noise.

**How to apply:** before sending, ask: does this fit in five short lines? If not, cut until it does.
The reasoning comes when the user asks for it.

## Answer the question inside its frame

A question like "what is different from production" is about the differences with production. It
is not an invitation to list everything else that could be wrong.

A direct question gets the answer in the first sentence. An agent that first went searching for
pipelines, while the answer was already in the query result, got "was that so complicated?". Explaining
or starting something else before the answer reads as dodging.

## Commit messages: only the change

A commit message or PR text describes the change in plain, human sentences. No verification
section, no claims about builds or tests the user runs themselves, and no mention of who or what
executed the work. Scan the full message, author fields and diff for AI references before pushing.

## Do what is asked, completely, and nothing extra

"Shall I?" questions after a clear request waste a round trip: the request is the permission. At the
same time, unrequested extras (touching a pipeline nobody mentioned, adding parameters, extra
validation, switching branches) cause real friction and sometimes real damage.

**How to apply:** before touching a file that is not part of the request, stop. Mention a better idea
in one sentence and leave it.

## Never start jobs in a client environment

Starting a pipeline or notebook in a client environment can overwrite data, burn capacity or trigger
downstream processes, and dev environments are often shared with the client's own people.

**How to apply:** you may prepare, fix and deploy code, but the user starts runs. After dropping or
changing something, say exactly what has to be reloaded.

## Read the load code before dropping a table

Dropping a table "so it is rewritten cleanly" only works when the load code creates it. If the code
does a MERGE into it, or reads the existing table, the next run fails and the table has to be
restored from another environment.

## Ask up front, not halfway

Questions halfway through a task stall the work while the user is away. Ask everything about
resources, cost and direction before starting; decide implementation details yourself.

## Confirmed risk is decided

Once the user has heard a risk and confirmed the choice, repeating the warning is noise. Execute.

## Complete, pasteable code

Loose snippets force the user to merge code by hand, which is where mistakes creep in. Give the full
file or cell, one at a time.

## Never invent values

An invented resource name, ID, URL or path looks plausible and breaks later, often in production.
Leave the value out and ask for it.

## All fields from API data

Cherry-picking a subset of fields from an API response means the next question needs a field that
is not there. Flatten the full response and keep the raw JSON next to it.

## Look it up, never "cannot" from memory

Answers from memory are often outdated or wrong, and "that is not possible" is the most expensive
kind of wrong: it stops the work. Settings and parameters named from memory are the second most
expensive. Documentation pages also go stale: when a page contradicts the product UI, check the
page date and trust the newer source.

**How to apply:** before saying something cannot be done, or naming a setting, look it up and cite
the source. Pushback from the user is a signal that you did not look it up.

## Your own conclusion is not a fact

A conclusion written in the journal by an earlier session was a hypothesis at the time. Treat it as
one until it is verified, and say so when you repeat it.

## Fresh state before a fix

Other agents and devices work in the same repos. Fixing a problem that someone already fixed, or
fixing it on stale code, creates conflicts.

**How to apply:** `git fetch`, `git log` and the newest journal lines first.

## Explicit branch on push

`git push origin HEAD` pushes whatever branch happens to be checked out, which is not always the one
you think. Name the branch.

## Isolate cloud CLI logins per project

A cloud CLI keeps one active login per config directory. Switching it for one client silently breaks
scripts and tools of another. Give every client or project its own config directory, for az with
`AZURE_CONFIG_DIR`.

## Subagents see nothing

A subagent starts without these rules. If it is not told literally what it may not do, it will start
jobs, write test files or delete things.

## Sessions and background work

Background work stops when a session ends or is replaced. The next session has to reconstruct the
state from the journal and the transcript before continuing.

## Client-facing content

Mentioning another client, even as a reference, can break confidentiality. Downplaying words
("simple", "not complicated") undersell the work. A message for a non-technical stakeholder should
say what happened, the cause in plain words and what was done, nothing more; a message rewritten
from the user's own draft should keep their words, their structure and their length.

**How to apply:** put your version next to the user's draft. Every sentence must be something the
recipient needs to know. When in doubt about a detail, leave it out.

## Structure of this repo

When new things land in the root, the repo becomes a pile nobody can navigate. Everything has a
place: clients, projects, skills, techniques, or an existing base file. And the repo only works as a
memory if it is complete: every client, project and repo belongs in it.

## Work in the user's own folder, simple solutions, push means everything

Agents like to create worktrees or copies elsewhere; the user then cannot see the changes where they
look. Temporary files left behind clutter the repo. Over-engineered designs (three services where one
would do) cost money and attention forever. And "push it" was more than once read as "push the one
thing I just did", leaving other finished work behind.

**How to apply:** branch in the user's folder, scratchpad for temporary files, the smallest design that
works, and after a push `git status` must be clean.

## Rebuild every field, and only real changes from tool exports

When an existing export or report is rebuilt, silently skipping fields that were hard to find is the
failure mode: it looks finished and is not. Tool exports (BI files, notebooks, low-code definitions)
often rewrite formatting or whitespace on every save; committing that noise hides the real change.

**How to apply:** list all source fields first and tick them off. Missing source: placeholder plus a
note. Before committing a tool export, diff it and keep only the meaningful lines.

## Permission to run applies once

A "yes, run it" for one load or model run is not a standing permission. Some runs the user wants to do
themselves, because they cost capacity or touch production.

**How to apply:** ask again for the next run, or hand over the exact command.

## Only report done after a full check

In a long debugging session an agent repeatedly said "fixed" after checking two or three examples,
and the user kept finding the same class of bug in the rest of the data within minutes. Each time it
cost trust. A check over the whole population is usually cheap.

**How to apply:** loop over every row, item or member before saying "done". If you only sampled, say so
with numbers.

## Never use a pasted password

Users under time pressure sometimes paste a real admin password into the chat. Using it puts a live
secret in tool arguments, shell history and transcripts, and rewards the habit. A device-code sign-in
lets the user authenticate directly with the provider on their phone, so the password is never needed.
Granting outsiders access to a system deserves a firm pause: proceed once there is concrete evidence,
such as a forwarded email naming the people and the reason.

**How to apply:** propose device code first. If a password shows up anyway, do not use it and advise
changing it.

## Messages in the user's voice

Drafts in a stiff corporate tone ("We hereby...") read as not written by the user. Rewriting sentences
the user already approved is frustrating and loses their wording.

**How to apply:** first person, plain words, their usual greeting and sign-off, only what the recipient
needs. Change only what was asked.

## Nothing stays only in a local memory file

Agents with a built-in memory store learned rules and procedures in local files per project folder.
Another agent, device or folder never sees them, so the same lesson gets relearned. Several useful
runbooks were found only by accident.

**How to apply:** when you save something to a local memory, also put it here (rule, skill or project
README) and let the memory point to it. The context-doctor skill checks for this.

## Client deployments run through the client's CI, containers built in the pipeline

A server for a client was first built with GitHub Actions because that was what the user's own test
tenant used, and that choice slipped into an estimate for the client. The user's clients work in
Azure DevOps, so the default is their CI; GitHub only when the client asks for it. The same day a code
deploy that built on a shared B1 plan took the plan to 100% CPU and the other apps on it went down:
build the image in the pipeline and let the web app only pull it. And `az webapp config appsettings
set` from Git Bash turned `DATA_DIR=/home/data` into `C:/Program Files/Git/home/data`, so the app wrote
its data inside the container and lost it at every restart. `MSYS_NO_PATHCONV=1` (or PowerShell)
prevents that.

## Agent work stays visible

Another agent started three tasks headless (`claude -p`). The user could not follow them in the
session list and asked to always run agent work in sessions they can watch, also for night work and
for resuming after usage limits.

## No offers the user did not make

An answer to a client got an extra sentence offering an overview of expiring secrets. It was not in the
user's text and creates work they did not plan. Client messages contain only what the user wrote.

## Tone in documents the reader reads

A development plan said "as soon as possible", "substantially more involved" and "in consultation with
<manager> I will", while that manager reads the plan. The user found it unprofessional and not
balanced. Businesslike, weighed wording, and address the reader, not about them.

## Updating an existing client document

Updating two client decks and an estimate, a subagent added technical text the readers do not act on,
a cost box on a slide about something else, a slide that repeated an earlier one and a made-up
metaphor. The user: "it only matters to them what it costs", "keep the message central", "I am
drowning in jargon". Plain language a finance manager reads easily, technique in the speaker notes,
one message per slide, and save on the original instead of next to it.

## Mail drafts through Graph as HTML

A reply draft created through Graph with a plain-text comment lost every line break and arrived as
one block. Set the body as HTML with one `<p>` per paragraph (and `<br>` inside a paragraph), above
the quoted original.

## Do it yourself, never hand work back

Asked to look something up, an agent forwarded the question to another session and asked the user to
open a browser pane, while a SQL endpoint worked fine. Another agent wrote under a draft "do that
before you send this", which is a to-do for the user they never asked for. A rule that said "do not
post or send" was read as a ban, while the whole point was that the agent posts.

**How to apply:** if the tools you have can do it (query, click, post, fetch), do it. Only steps that are
really impossible for you (their MFA, a payment) go to the user, as one clear line.

## What the user switched off or deleted stays off

An agent made all routines self-learning and in doing so switched on routines the user had turned off on
purpose. Another posted again something the user had deliberately removed. The other way round, a
notebook was deleted that nobody had asked to delete.

**How to apply:** never restore, enable or recreate what the user switched off or removed. Never delete what
was not named. A new version of something that was approved or shared never overwrites it.

## Continue another agent's work

An agent asked to finish a presentation started again from scratch instead of continuing with the file
the stuck agent had produced. That throws away approved work.

**How to apply:** find the last state (file, branch, journal) and continue from it.

## No sign-in windows or popups on the user's screen

A CLI login opened a sign-in window on the user's screen while they were working, and unrequested
screenshots added noise. A query on a SQL endpoint or an API call did the same job silently.

**How to apply:** use the connection that already works. Isolate logins per project (see above) so you do
not need a new one, and never use screenshot click work when a query or API can do it.

## Report done only after the real result through the real route

Routines reported success while the user found two failure mails in their inbox. A claim that posting
"works via the routine" turned out to be wrong, because it had only been tested by hand. Clients asked
"are you 100% sure this error is gone?" and the answer was no.

**How to apply:** check through the route that will really run: the live URL, the run itself, the routine as
scheduled. Build the check into the routine when it can fail silently. If you did not verify, say "not
verified", or "checked N of M".

## Report the real error, not a guess

After a failed pipeline an agent did not read the error message, compared the failure with earlier
incidents and sent that cause to a client. The real error was a missing header row in a source file that
someone had edited. The client got wrong information. A later status ("data is up to date") was also
wrong, because a rerun had happened before the file was fixed.

**How to apply:** read the message of the lowest failing step and pass on exactly that. History is for
checking whether it happened before, not for deciding the cause. Unsure: phrase it as a question. Check the
order in time before you give a status.

## Do not give up with "nothing found"

A promotion routine ended with "no new suitable place". The user: not looked for properly.

**How to apply:** search broadly, in several ways, and say what you tried.

## Where does it run: local task or cloud routine

Cloud routines kept asking for permissions, so some routines moved to local scheduled tasks. A run then
reported that nothing was sent because the task needed a mail connector, while it ran on the user's own
laptop and could simply use what is there.

**How to apply:** before you say or change anything about a routine, check where it runs (local scheduled
task or cloud routine) and read its own notes.

## Journal target per session

After a cleanup almost 1,800 journal lines turned out to sit under the wrong client. Several sessions on
different contexts ran at once but every hook read the same device-wide pointer, so the last
`--set` of any session decided where everything went. The target is now stored per session (by session id)
and the device-wide pointer is only the default for sessions without one.

**How to apply:** every session sets its own target at the start and again when the topic changes. Own work
never goes into a client journal.

## Split long or multiple tasks in parallel

While investigating dropped sessions an agent did everything itself, step by step, with long waits. The
user: start one of the other chats and work in parallel, one by one is too slow.

**How to apply:** divide long or multiple tasks over subagents or other chats right away. Give each one the
relevant rules literally in its prompt, because it does not see them.

## Installer tests with an isolated HOME

A subagent tested the installer on a copy of this repo in a temporary folder. The installer did what it
is built to do: it registered its hooks in the real `~/.claude/settings.json` and added a block to the
real global `CLAUDE.md`, both pointing at the temporary copy. Every later session would have run hooks
from a folder that was about to disappear.

**How to apply:** run installer tests, and anything else that writes to the home folder, with
`HOME` (and `USERPROFILE` on Windows) set to an empty temporary folder. When delegating such a test,
put this in the prompt literally.
