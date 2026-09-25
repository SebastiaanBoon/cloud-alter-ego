# Databricks Auto Loader

## Checkpoints

- The checkpoint records which files were processed. A rerun only picks up files that are new to the
  checkpoint.
- A table that ended up empty stays empty on the next runs: the files are already booked as
  processed. Deleting only the checkpoint folder makes Auto Loader read all files again; with a MERGE
  into the existing (empty) table that is enough.
- Notebooks that choose a full-load path only when the table does not exist need both the table
  dropped and the checkpoint deleted for a clean full reload. Dropping only the table sends the next
  run into the incremental path with nothing to read.
- Delete a checkpoint only after the fixed code is deployed, otherwise the old code reprocesses and
  books the files again.

## CSV and schemas

- CSV with `header=true` and an explicit schema: Spark applies the schema by position and ignores the
  header names (`enforceSchema` defaults to true). A column order that differs from the schema goes
  unnoticed. Check the order when a table looks wrong.
- Diagnose without running the pipeline: read the raw files directly. In a notebook with
  `spark.read.option("header", "true").option("recursiveFileLookup", "true").csv(path)`, or in the SQL
  editor with `SELECT ... FROM read_files('<path>', format => 'csv', header => true)` (reads folders
  recursively), and count empty values per key column.

## Business Central exports (bc2adls style)

- Headers look like `FieldName-<fieldno>` (`CustomerItemNo-1`), plus `$Company`, `timestamp-0` (row
  version) and `systemId-2000000000`. A `.cdm.json` file per table carries the schema and the
  primary key as defined in Business Central.
- Deleted records arrive with only `systemId` and an empty `SystemCreatedAt`: derive `_is_deleted`
  from that.
- Business Central allows empty values in primary key fields (a blank batch number, a blank starting
  date). A filter that requires every primary key column to be filled can drop a whole table without
  any error. Filter on a filled `systemId` and merge on `systemId`.
- Keep the latest version per `systemId` by the highest `timestamp-0`.

## Jobs

- Databricks job parameters have a size limit (10,000 characters). A big JSON payload passed as a
  parameter fails; pass less (for example trim an API `$select`) or pass a reference.
