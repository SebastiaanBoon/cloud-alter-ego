# Lead outreach: runbook

Recurring process for a small web or service business: find local businesses with an outdated or
missing website and prepare one personal email draft per business. Works for any AI that picks it
up (Claude Code, Codex). Work through it top to bottom.

| File | What for |
|---|---|
| [research-brief.md](research-brief.md) | Reusable research assignment per sector, with the exact columns |
| [writing-style.md](writing-style.md) | Structure, tone and checks for the emails; fill in your own details |
| `leads/` (create it) | One lead list per round, plus `leads/rounds.md` with who already got a draft |

## 1. Prepare

- Pull this repo, read `preferences.md`, this runbook, `writing-style.md` and `leads/rounds.md`.
- Read your own current website (and its `llms.txt` if you have one). The email must match what is
  there: positioning, packages, pricing approach.

## 2. Research online

- Use [research-brief.md](research-brief.md). Work in parallel batches per sector, 18 to 20 real
  businesses each. Examples of sectors: hospitality, construction and installation, retail,
  automotive, beauty and wellness, care, crafts, other services.
- Only businesses with a demonstrably outdated website, or none. Skip modern sites.
- Never invent data. What cannot be found is literally "not available".

## 3. Lead list (spreadsheet)

- Merge all batches into one spreadsheet with one sheet "Leads <region>" and the columns from the
  research brief, plus an 18th column **Alternative contact**: without an email address, note the
  best other route (contact form, Instagram, Facebook); with phone or email known, "n/a".
- Freeze the header row and turn the filter on.
- Deduplicate on email address, website domain and business name against all earlier lists in
  `leads/`. Whoever got a draft in an earlier round does not come back.
- Save as `leads/<yyyy-mm>_<region>_outdated-websites.xlsx`.

## 4. Write the emails

- Only for leads with an email address. One email per business.
- Follow [writing-style.md](writing-style.md) exactly: structure, tone, signature.
- The specific part per business comes from the columns Main activities, Short description, Website
  quality and Social media activity. Write only what follows from them.

## 5. Check before saving

Go through every email:

- The recipient is exactly the email address from the spreadsheet.
- Greeting with a first name only when the contact person is known.
- No claim that does not follow from the research: no compliments, no verdict that their site is
  "outdated". An old copyright year does not prove when a site was last updated.
- No promises about search rankings.
- Prices only as in your current price list.
- Plain text, no Markdown or HTML.
- No em dashes, no names of other clients, no downplaying words like "simple".
- Signature complete.

## 6. Save as drafts

- **Never send.** Drafts only. You send them yourself, unless you explicitly ask the agent to.
- Claude Code: a Microsoft 365 or Gmail connector with a create-draft action.
- An agent that cannot edit existing drafts: create new drafts and move replaced versions to an
  archive folder, so the drafts folder only holds the current set.
- On a 429 from the mail API, wait a moment and continue.
- Read the drafts folder back and check count, recipients and subjects.

## 7. Record

- Update `leads/rounds.md` with the new round.
- Write a journal line with tools/note.py.
- New insights about tone or approach go into `writing-style.md` or this runbook, not only the journal.
