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
