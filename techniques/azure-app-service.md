# Azure App Service, Static Web Apps and GitHub Actions

## Deploying

- Code deploys: `azure/login` with a service principal, then `az webapp deploy --async true`. A
  synchronous deploy regularly times out on small (B1) plans. Follow it with a health check on an
  `/api/health` endpoint and, ideally, a check that the deployed commit is the expected one.
- Container deploys: build and push to Azure Container Registry, then
  `az webapp config container set`. That command can leave `DOCKER_REGISTRY_SERVER_USERNAME/PASSWORD`
  app settings behind that take precedence over managed-identity pulls; delete them after setting
  the container.
- A stale `appCommandLine` (startup command) overrides the Docker `CMD`. Clear it on every deploy
  (`az webapp update` or `az webapp config set --startup-file ""`).
- Turn Always On on for APIs that must not unload when idle.
- Node APIs with Prisma: run `prisma generate` while building the deploy package, and start the HTTP
  server before database setup, otherwise the container can miss the startup timeout.
- Don't retry a deploy in a loop when another deploy is running: parallel deploys give 409 conflicts
  and block the app.

## Shared App Service plans

- Many small apps on one plan is cheap, but one heavy job takes all of them down (502s on the whole
  plan). Never run heavy computation on a shared plan; precompute elsewhere and push results.
- Putting a memory-hungry API in its own container isolates its memory from the other apps.

## Outbound IP blocks

- Some public data sources block Azure's outbound IP ranges entirely (Yahoo Finance is one). Pattern
  that works: a small job queue on the app (`trigger`, `claim` with a lease, `complete`) and a worker
  on a machine that is not blocked, started by a scheduled task. The app does all computation, the
  worker only fetches and forwards. Protect the worker endpoints with a bearer token.
- Undocumented endpoints can block an IP for hours after too many requests in a day; spread the load.

## Static Web Apps

- Deploy with the `Azure/static-web-apps-deploy` action or the SWA CLI and a deployment token. Pull
  requests get a staging environment that the close-PR job removes.
- Add the Static Web App URL (and custom domain) to the API's CORS origins.
- Payment providers redirect to the URL you pass; keep a `FRONTEND_URL` setting pointing at the live
  site.

## Domains

- Registering some country domains through the Azure ARM API fails on registrar fields that the ARM
  schema does not have. Register through the portal or a registrar and only bind the domain in Azure.

## Persistent data, files and logs

- Only `/home` survives restarts and deploys (with `WEBSITES_ENABLE_APP_SERVICE_STORAGE=true` for a
  container). Point data folders there, for example `DATA_DIR=/home/data`. Any other path is inside the
  container and is gone at the next restart.
- Kudu's VFS API reads and writes those files without a shell: `https://<app>.scm.azurewebsites.net/api/vfs/<path>`
  with an Azure management token (`az account get-access-token --resource https://management.azure.com/`)
  of an identity with Website Contributor. PUT and DELETE need `If-Match: *`. A pipeline can use it with
  its deploy identity, so the app itself needs no extra credentials.
- Log stream: log only what matters (real requests on the app, errors, the app's own events). Internet
  scanners hit every App Service (`/wp-login.php` and the like); filter their 404s and the start and stop
  lines of the web server out of the access log.

## Syncing app data to git without secrets in the app

When an app produces something that should be visible in git (generated config, learned rules), let the
repository's pipeline do the sync instead of giving the app a git token: read the files through Kudu with
the deploy identity (OIDC in GitHub Actions, workload identity federation in Azure Pipelines), commit on a
branch, open a pull request and merge it. GitHub Actions needs "Allow GitHub Actions to create and approve
pull requests" (repository setting, also via `PUT /repos/<owner>/<repo>/actions/permissions/workflow`).
A merge by the workflow token does not trigger other workflows, so there is no loop; exclude the synced
files from the deploy trigger.
