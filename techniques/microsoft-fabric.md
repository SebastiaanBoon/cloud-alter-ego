# Microsoft Fabric

## Lakehouses and Spark

- Use `OverwriteSchema` in copy activities, not the UI option "Overwrite". The latter has triggered a
  bug that keeps creating `_backup_<guid>` tables.
- Schema-enabled lakehouses need three-part names (`lakehouse.schema.table`) in `CREATE SCHEMA` and
  `CREATE TABLE`, otherwise you get `getDatabaseMetadata` failures.
- A notebook's `default_lakehouse_workspace_id` must match the target environment. When it points to
  another workspace, every `spark.sql()` call fails silently.
- Source data with dates before 1900 (common in older ERPs): set
  `spark.sql.parquet.datetimeRebaseModeInRead` and `...InWrite` to `CORRECTED` for Spark reads and
  Delta writes.
- CSV with trailing semicolons makes `inferSchema` drop the last column silently. Use an explicit
  `StructType`.
- Filter or catch bad values (`try_to_timestamp()`, `try_cast`) instead of turning ANSI mode off.
- Keep concurrency low (10 to 15) for parallel writes to a shared Delta table in large DAGs
  (`notebookutils.notebook.runMultiple`), otherwise the catalog service gets overwhelmed. The same
  goes for ForEach batch counts: OutOfMemory on the integration runtime usually means too much in
  parallel.
- `refreshMetadata` with a 300 s timeout is too short for large lakehouses; 900 s works, but watch
  `lro_max_attempts` as the next bottleneck.
- For small capacities, Python notebooks with `deltalake` (delta-rs) are far cheaper than PySpark.
  One ingest notebook per source that loops over config rows works well.

## SQL analytics endpoint

- `CREATE USER FROM EXTERNAL PROVIDER` does not work on a lakehouse SQL analytics endpoint. `GRANT
  SELECT ON SCHEMA::<schema> TO [principal]` directly does.
- The endpoint (TDS, port 1433) accepts Entra user and service principal logins only. SQL
  authentication with username and password is not supported.
- Query rejected with ODBC error 15806 "current capacity constraints" after a second or two means
  admission control refused it, not a SQL error. Retry once: if it fails the same way, the query
  asks too much for the SKU (shorten the window, reduce a cross join, make it incremental).

## Notebooks in pipelines

- `%pip install` is disabled by default in pipeline runs (MagicUsageError). Pass a bool base
  parameter `_inlineInstallationEnabled = true` on the notebook activity. It still does not work in
  High Concurrency mode or in a referenced (`%run`) notebook. An Environment with the libraries is
  the heavier alternative.
- Inline lakehouse connections in pipelines can cache a user-bound token that expires overnight
  (especially under PIM). Use the workspace identity for scheduled work.

## User Data Functions

- Key Vault from a UDF: `@udf.generic_connection(argName="keyVaultClient", audienceType="KeyVault")`
  and `keyVaultClient.get_access_token()`. `DefaultAzureCredential` does not work there (no IMDS).
- A UDF that reads a Variable Library through `@udf.connection` fails with a 401 when the item owner
  is a service principal, which is always the case after a fabric-cicd deploy
  (`ItemOwnerValidationFailure`). Keep that connection out of the UDF: constants in code, the rest
  as parameters.
- The Variable Library method is `getVariables()` (returns plain strings), not `get_variable()`.
- The `azure` meta-package cannot be installed; use the specific sub-packages.
- UDF code cannot run in a notebook context; test it as a UDF.

## Workspace administration

- Soft-deleted items in the workspace recycle bin can block deleting a pipeline. Delete them
  permanently through the recycle bin API.
- Service principals calling admin APIs need the Fabric admin portal tenant setting plus membership
  of the allowed security group, not an Entra role.
- Check who ran something before interpreting a 403: interactive runs use your user, pipelines use
  the workspace identity or the owner.
- Documentation pages go stale: a limitations page can still say "not supported" months after a
  feature shipped. Check the page date against the UI.

## Activator

- Posting to a Teams channel is supported (it was added after some docs still said otherwise). The
  list of teams loads for the account the rule runs under, so that account needs a Teams license and
  membership of the team, and the Fabric Activator app must be allowed in the Teams admin center.

## External access to Fabric data

- Fabric has no auth model for outside parties: every route (SQL endpoint, GraphQL, UDF) needs an
  Entra token of a principal with rights.
- API for GraphQL accepts a service principal via client credentials: token from Entra with scope
  `https://api.fabric.microsoft.com/.default`, Bearer header on a POST to the endpoint. The tenant
  setting "Service principals can use Fabric APIs" must be on (or scoped to a group with the
  principal in it).
- With **saved credentials** on the GraphQL data source, the principal only needs "Run Queries and
  Mutations" on the API item, no access to the lakehouse itself. With SSO it also needs read access
  to the data. One API per external party, with saved credentials, gives clean isolation.
- Parties that can only do API keys or basic auth: put an Azure Function or API Management in front
  that takes the key and fetches the token itself.
- Never share a client secret in plain text; rotate it if that happened.

## Conventions that worked

- Silver stays raw 1:1 (typecasting and deduplication only), gold builds a star schema, keeps silver
  column names and only adds derived columns. `fact_` and `dim_` prefixes, UTC everywhere.
- A separate item per layer instead of table prefixes like `brz_` and `slv_`.
- Config that humans edit: CSV over xlsx in version control, xlsx diffs are unreadable. An Excel file
  that suddenly fails with ExcelInvalidHeader often has a sheet name mismatch: copy the data to a new
  sheet, delete the old one and rename.
