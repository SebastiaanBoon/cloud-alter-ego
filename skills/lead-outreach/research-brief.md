# Research brief: leads

Reusable assignment for one research batch. Run several batches in parallel (one per sector) and
merge the results following the runbook. Fill in `<REGION>`, `<SECTOR>`, `<EXAMPLES>` and
`<SEARCH TERMS>` per batch.

```
Research assignment for lead generation for a web design business.

Goal: find ~18-20 REAL <SECTOR> businesses (<EXAMPLES>) physically located in <REGION> that have a
visibly outdated website, OR no website at all. Do not waste slots on businesses with modern,
professional sites.

Process per candidate:
1. Use web search to find real businesses in the target area (for example <SEARCH TERMS>, local
   directories, map results).
2. If they have a website, actually open it. Judge whether it looks outdated: old design era, not
   mobile friendly, no HTTPS, broken images or links, no recent updates in dated content.
   An old copyright year alone is NOT proof of when the site was last updated.
   Only keep candidates that are genuinely outdated, or have no site at all.
3. Find and check their Instagram and Facebook pages and their Google Business listing
   (address, phone, reviews, opening hours).
4. Extract real details only. NEVER invent or guess a phone number, email, address or contact person
   name. If something cannot be found, write exactly "not available".

For each business, collect these exact fields:
- Business name
- Phone (real only)
- Email (real only)
- Sector (e.g. "Hospitality - Restaurant")
- Main activities (short description of what they actually do)
- Current website (real URL you visited, or "no website")
- Instagram (real URL, or "not found")
- Facebook (real URL, or "not found")
- Google listing (real URL, or "not found")
- Town
- Address (street, number, postcode, else "not available")
- Website quality (1-2 honest sentences on what is outdated, or "no website")
- Contact person (owner or manager if findable, else "not available")
- Short description (2-3 sentences: what kind of business, its character)
- Estimated size ("independent/small", "medium" or "not available")
- Social media activity (which platforms and how active)
- Sales chance ("high", "medium" or "low", with a one-line reason: how outdated versus how active
  and healthy the business seems)

Output: a markdown table with exactly those 17 columns in that order, one row per verified business,
plus a one-line count at the top. No placeholder or unverified rows. Fewer real rows is better than
padding. No other commentary.
```

## After the batches

- Add the 18th column **Alternative contact** while merging (see the runbook, step 3).
- Deduplicate against the lists in `leads/` before any email is written.
