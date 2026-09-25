# Clients

One folder per client. Create one with:

```
python tools/note.py --new-client <slug>
```

That copies `_template/`, adds a row below and makes it the active context. Each client folder
grows by itself:

- `README.md`: overview, stack, key facts, chronological history of incidents and fixes, and
  client-specific working preferences. You and the agent keep this current.
- `journal/<year-month>.md`: one line per turn, written by the agent and by tools/auto_journal.py.
- `sessions/`: full transcripts saved by tools/save_session.py at the end of each session.
- `chats/` (optional): older conversations you import by hand.

`_unsorted/` catches everything that does not belong to a client or project.

| Client | What | Stack |
|---|---|---|
<!-- new rows are added above this line -->
