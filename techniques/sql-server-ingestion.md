# Ingesting from on-premises SQL Server

- Error 40 (Named Pipes) when connecting by IP while the host name works: use the host name. Login
  error 18456 state 1 with the host name usually means the account has no instance-level login or
  database user mapping, even when table rights were granted through a group.
- Hot transactional tables (open orders) can hang a copy for many minutes on shared read locks
  against active writes. `WITH (NOLOCK)` on those tables avoids the hang; accept the dirty-read
  trade-off consciously.
- Tables with an immutable, processed part and a small mutable part: incremental upsert with a
  lookback window on the processed status, full overwrite of the mutable part. Child tables without
  their own status column can be split by joining on the parent keys.
- Prefer raw ingestion over views maintained by the source's IT team: views hide logic outside the
  platform, create a dependency on another team and block incremental loading.
- A MERGE that fails on duplicate keys in staging (error 8672) can be transient when a retry
  mechanism reloads the batch; if it returns, deduplicate on the key before the merge.
- A data gateway returning OData 401 `invalid_request` points to the credentials on the gateway
  connection, not the query.
