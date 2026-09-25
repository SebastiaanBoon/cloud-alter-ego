# dbt

## Authentication against Fabric or Azure SQL

- dbt-fabric with `authentication: CLI` uses the az CLI token. Give every project its own token cache
  with `AZURE_CONFIG_DIR`, set in a small `set_env.bat` (or `.sh`) that also sets the other env vars.
- On Windows cmd, call it with `call set_env.bat`; without `call` the script ends the parent batch and
  the variables are lost.
- For the first build of a session, log in inside the same window, because the token has expired:
  `az login --tenant <tenant-id> --use-device-code`, then the dbt command. Login error 18456 usually
  means dbt used a missing or expired token cache.
- If conditional access blocks device code, use the browser login (see entra-id-and-oauth.md).

## Modeling checks

- Check the grain against the source: row count of the model versus the source at the same grain.
  A total that still matches can hide a wrong split per person or per item.
- Grouping on a key that the source leaves empty (for example an employee number missing for some
  rows) collapses all those rows into one. Add a second identifying column to the grain and extend
  the uniqueness test with it.
- A cross join of a date spine with a large combination set, with running windows on top, grows fast.
  Widening its window (for example from one year to five) can push a model past the capacity limit
  (see the 15806 note in microsoft-fabric.md). Options: shorter window, start the grid at the first
  relevant date per key, or make the model incremental.
- An opening balance computed as "everything before the window start" keeps running totals correct
  when you move the window.

## Working agreements

- Agents change models, the user runs the builds (unless asked). Commit messages describe the change
  only, never claims about a build the agent did not run.
- Keep test and model changes on a branch and let the user merge.
