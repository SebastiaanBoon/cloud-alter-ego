# AI usage per day: weekly indicator page

Use this when the user asks about "AI usage", "the AI indicators", "the chart of AI usage", or when the weekly
routine `ai-usage-weekly` runs. Goal: refresh the page "AI usage per day" with the newest figures, publish it as a
new post on a posting site and report in a few lines what changed. The page and post are in English.

The routine is a cloud routine that dispatches the work to the always-on server, which runs
`tools/run_routine.sh ai-usage-weekly` with the prompt from `tools/routines/ai-usage-weekly.txt`. In the cloud
itself it did not work: the proxy returned 403 on the package registry API and there is no posting key there.
Background and sources: the README of the project that holds the page.

## Steps

1. From the repo folder run the build tool of the project. It fetches the processed tokens per week and per
   provider from an open model router endpoint (public, no account), keeps the tokens of the last day, and fetches
   the daily package downloads since 1 January of the coding agents (for example Claude Code, Codex, Copilot CLI,
   Gemini CLI) and of the AI libraries (OpenAI, Anthropic, Google, Vercel SDKs). It writes the HTML page. It takes a
   few seconds.
2. Publish the page with the Artifact tool to the same URL as last time (kept in the project README; read it first
   with action read if the session does not know it). A new URL only if the old one no longer exists.
3. Post the same page as a new post on the posting site, once a week. First check whether this week's post is
   already there (list the latest posts of the community and filter on the author); if it is, do not post again but
   update that post if needed. Title for example `AI usage per day, week of <date>` and a one-sentence description
   with the key figures, both from a UTF-8 file. The API key is read into a shell variable from the file named in the
   routine prompt, used only in the Authorization header and never printed. Check: the post shows the right title and
   community, and the raw page and the post page return 200.
4. Check that it really worked: the build ended without an error, the published page shows the new date of the last
   day, and the URL is the same as in the README.
5. Report in at most five lines, with the URL of the post: tokens in the last full week against four weeks earlier
   and against the start of the year, the biggest shift in share per provider, and per coding agent the corrected
   growth. If the run failed: the real cause in one line (for example proxy 403), do not keep retrying.
6. As a routine: self-learning according to [routines](routines.md) with `skills/learnings/ai-usage-weekly.md`.
7. On the server, as the very last step: write the message to the routine's result file and close the tmux session
   of the routine. Otherwise the session keeps the lock and the launcher skips every next dispatch.

## Verify the data before you conclude

- The build tool drops days without package data (0) and outliers (above 3 times the median of the surrounding 14
  days) and lists them at the bottom of the page. Check that list: a new outlier is a bot or a mirror, not usage.
- Always compare with the corrected growth (divided by control packages such as react, lodash and express). All of
  npm grows fast, so uncorrected growth overstates what AI itself does.
- If you see a spike, check whether it is also in the control packages before you attribute it to AI.

## Rules

- No investment advice: describe what the figures show, not what to buy or sell.
- No dashes in the message, on the page or in the post.
- One post per week, never a second post to repair something.
- Do not use commits with a co-author line as a measure: many people remove that line.
- Commit only the project folder and the routine's lessons file; locally the hooks commit the rest.

## Check

Build without error, the published page shows the newest day, one post this week with the right title, and the
report contains the URL.

## Self-learning

Read `skills/learnings/ai-usage-weekly.md` at the start and append one line at the end, also when the run failed.
