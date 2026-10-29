# Stock analysis

Use this when the user sends an export of a stock screener (a CSV, usually in Downloads) or asks for "good stock
picks", which shares are undervalued, how the market looks, or whether to change the portfolio. Background, the
user's profile and earlier analyses: the README of the stock analysis project.

## Steps

1. Read the whole CSV and check the data before you filter: a P/E below 2 or above 500, a price that does not fit
   the earnings (split, wrong trailing EPS), missing history. Report suspicious rows separately and leave them out.
   Structural data errors: have them fixed in the screener project.
2. Filter on a P/E well below the share's own historical median, not just a low P/E.
3. Research the candidates yourself with agents (one agent per three names, in parallel, with web search): why is
   the price low, are the earnings real or one-off, what is going on in operations and market, what is the next
   catalyst (results, a ruling, a product launch). Do not push this back to the user.
4. Put the result next to the market indicators: earnings expectations (a weekly earnings insight report) and AI
   usage ([ai-usage-indicators](ai-usage-indicators.md)).
5. Answer briefly and as a strategist: a ranking of the strongest candidates for the user's profile (for example
   "high risk, high reward": temporarily low because of unrest, recovery within months, then sell), per name why it
   is low, the risk and the catalyst. State the source and date of every figure.
6. Add the analysis in one line to "Earlier analyses" in the project README.

## Rules

- Do not prescribe amounts or an allocation of the portfolio; describe what the data shows. Do choose and rank: a
  list without a verdict is useless to the user.
- Never refer to a financial adviser.
- No dashes.
- Never a figure from memory: prices, P/E and earnings always from the export or a dated source.
- Check a strange price for a split or corporate action before you call it wrong.

## Check

- Every figure in the answer comes from the export or a dated source; suspicious rows are reported separately.
- The line in "Earlier analyses" is in.

## Self-learning

A correction from the user about a ranking, a data check or the tone goes into the Rules section straight away.
