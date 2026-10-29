# Data platform or pipeline failure: analyse and repair efficiently

Use this for any error message, failed run, empty or stale table, alert ticket or "the numbers are wrong" on a data
platform (Fabric, ADF, Databricks, Synapse; medallion bronze, silver and gold, dbt, semantic model). Goal: find
the real cause, then re-run only the affected part with as little work as possible.

Keep per client a platform card, an incident list, patterns and pitfalls in `clients/<slug>/` (for example
`platform-incidents.md`) and read that first. This file holds the generic method.

## Mandate

- The goal is that the agent does the repair itself. Until the user records that in the preferences file, starting
  something (pipeline, notebook, dbt build, refresh) is only allowed when the user asks to run it. A permission
  holds for that action, not for the next time. Announce what you start and in which order, then tick off each step.
- Always allowed without asking: reading (runs, logs, the Delta log, a read-only SQL endpoint), analysing, writing
  a repair plan.
- Never: drop a table without reading its load code, save a client's config file, move workspaces between
  capacities, touch a full refresh or snapshots, put test files in the environment, query source systems of third
  parties, do an elevation (PIM) or MFA yourself.
- One login per session: per client a script with a stored token (token cache plus authentication record, the
  token also passed to the SQL driver). Never an interactive login per query, and never `az login` on a shared
  config (that broke a running dbt run).

## 1. The real error message

Never name a cause before you have read the message.

- Fabric: the job instance (`failureReason`, `invokeType`, who started it: service principal or user) and per
  activity the activity runs (`error`, `output.rowsRead`). A runMultiple only names the first failed notebook and a
  count.
- Notebook details: the snapshot or Livy sessions. Many platforms have own logging in a monitoring lakehouse or
  warehouse, or a dbt log table.
- ADF or Azure: the activity output plus the Azure activity log (caller, correlation id) for scale or resource actions.
- Read the days before: does it repeat, since when, what changed (deploy, config line, source file, gateway change,
  a conversion at the supplier). Earlier incidents are context, not proof.

## 2. Classify

| Kind | Sign | Default approach |
|---|---|---|
| Resources | OutOfMemory, timeout per cell, 429, capacity exceeded, locks | find the load first, then re-run in a targeted way; do not poll on 429; structurally lower concurrency or rewrite the model |
| Source empty, late or rebuilt | A copy reads 0 rows and is Succeeded; data a day behind | rows read per run and the Delta log; after the source is repaired, reload in a targeted way; inform the supplier |
| Config or bronze missing for dbt | "Invalid object name", model fails on a missing source | check that the bronze tables exist (SQL endpoint, maybe a metadata refresh), check config line and version, only then dbt |
| Source file or config changed | unresolved column, invalid header, empty row, shifted column | have the file repaired (client or user), then reload; otherwise you load the wrong file again |
| Data type or edge case | cast error, a letter in a number, optional key field | generic fix in code (cast to text), pull request, then reload the core notebook |
| Identity, secret, connection | 401 or 403, AADSTS, getSecret, gateway update, service principal lacks rights | establish the identity (principal or user), secret id versus value, owner rights on connections; after a gateway change replace connection ids |
| Pipeline binding | BadRequest on an Invoke Pipeline | remove the activity and put it back exactly, or compare with the acceptance environment |
| Race or order | refresh during a dbt build, two dbt runs at once, a run before the source sync | wait until the other is done, then run again; check leftovers of temporary tables |
| Metadata behind | The SQL endpoint says "does not exist" or counts 0 after a load | use the Delta log or a metadata refresh, do not load again |
| Data content | values negative, empty, wrong grain or currency | compare raw bronze with the source over the whole population; if it is already in bronze, it comes from the source |
| Platform limit | ADF Lookup 4 MiB, 5000 rows, Databricks parameters of 10,000 characters | smaller windows or payload; pass payloads to notebooks base64 encoded |

## 3. Determine the scope

- Green is not loaded: a pipeline with 0 tables, wait-based safety nets, a bronze step that ends Succeeded while a
  source failed, a copy with 0 rows. Look per activity and per source.
- Which tables and runs are affected: per copy `rowsRead`, per Delta table the `_delta_log` (file time,
  `stats.numRecords`). The Delta log also shows yesterday's state.
- The SQL endpoint runs minutes behind the Delta table; for current counts use the Delta log.
- What is like this every day (structurally 0 rows) is reported separately, not as the cause of today.
- A Failed alert can contain a successful data load: first look per activity at what did run.

## 4. Repair in a targeted way, in order, tick off each step

Not the whole orchestration again: it runs everything, takes long and often gives resource errors again.

1. Remove the cause first (file, config line by the user, binding, rights, free capacity). A re-run before the
   source is repaired loads the error again.
2. Bronze: only the source pipeline or notebook of the affected source. Check that the table now has rows;
   otherwise stop and report.
3. Silver: only the notebooks or dbt models of those tables, with any history models after them.
4. Gold: find which gold steps read the table (table name in notebook definitions, or `dbt ls --select <model>+`)
   and run only those. Skip commented out steps. dbt: smallest selection, never a forced build, never
   `--full-refresh`, never snapshots.
5. Semantic model: find in the model definitions which ones use the gold tables. Refresh imports (the Power BI
   refresh API, or the client's refresh notebook or pipeline activity), not Direct Lake. Look at the last refresh
   first and do not refresh while dbt is still building.
6. Check per step: run status, rows (Delta log), tests PASS, comparison with yesterday or the source. Only report
   "done" after checking through the real route.
7. One journal line per step with time and rows. Client message according to
   [client-message-writing](client-message-writing.md): short, whether the data is right, a suspicion as a
   question, no technical steps, no offers, no work for the user.

## Pitfalls from earlier failures

- Agents that started silver, gold and ML runs in dev by themselves after a clean-up round: not without an assignment.
- A table was dropped that is loaded through a merge: the next run failed and it had to be copied back from production.
- A workspace was moved to another capacity during a run: dev became unreachable.
- Dev behind production or acceptance: first know which environment you look at (workspace ids differ).
- A checkpoint plus an incremental path left a table silently empty: release the code first, then reset only that
  checkpoint folder.
- Unrequested tests, config or parameters from agents broke the build.
- An own earlier conclusion turned out wrong: bring it as a suspicion.
- Secret renewal on a legacy connector type can break the connection: check which auth type the linked service uses.

## Check

Before you report: did you read the real error message, did you determine the scope per activity and table, and did
you verify the result through the real route (rows, tests, comparison), not only the run status?

## Self-learning

Every new incident goes as one line in the client's incident list (date, symptom, real cause, repair, check, lesson).
A pattern that comes back twice becomes a row in the classification table.
