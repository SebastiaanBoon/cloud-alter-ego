# Power BI

- Field parameters with slicer-driven switching: read the numeric order column with
  `SELECTEDVALUE` and translate it to labels with a `SWITCH`, instead of looking up the text column
  (which can give composite key errors).
- Keep one canonical report per subject instead of parallel versions; parallel reports confuse users.
- After cleaning up tables in a lakehouse or warehouse, check every semantic model's source tables
  (schema and item navigation) against what still exists. A model can keep reading an old table that
  is never refreshed, or break when it is removed.
- A value that looks converted in the source application (for example a price in another currency)
  may be converted with a fixed rate table that never reached the data platform. Recompute and
  compare before trusting it.
- Refresh automation through the REST API in parallel groups: deduplicate the dataset list first,
  otherwise a dataset gets refreshed twice at the same time.
- Model changes made in Power BI Desktop also touch metadata (lineage tags). Commit those with the
  change instead of leaving them as a stray diff.
