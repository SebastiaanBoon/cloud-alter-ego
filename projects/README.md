# Projects

Everything you build yourself, separate from your clients: your own business, side projects, apps,
experiments. One folder per project. Create one with:

```
python tools/note.py --new-project <slug>
```

A project that spans several repos gets one folder that lists all of them. Tip: ask an agent to
walk through all repos on your GitHub account (`gh repo list`) and create a folder for each one, so
nothing is missing.

| Project | What | Status |
|---|---|---|
<!-- new rows are added above this line -->

## Shared infrastructure

Describe what your projects share, so an agent does not have to rediscover it every time:

- Cloud account, subscription or tenant: <NAME>
- Resource group or project: <NAME>
- Hosting pattern: <FOR EXAMPLE APP SERVICE FOR APIS, STATIC WEB APPS FOR FRONTENDS>
- Shared plans, registries or databases, and their limits: <NAME AND WHAT NOT TO DO ON IT>
- CI/CD pattern: <FOR EXAMPLE GITHUB ACTIONS ON PUSH TO MAIN>
- Default branch per repo differs: always check before pushing.
