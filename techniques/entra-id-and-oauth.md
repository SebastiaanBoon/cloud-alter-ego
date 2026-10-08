# Entra ID, OAuth and logins

## OAuth flows

- A client id plus a client secret is enough for exactly one flow: client credentials. The app then
  signs in as itself, without a user, and only if the API supports that grant and the app has
  application permissions (with admin consent) or rights as a service principal.
- "Connects via OAuth" usually means the authorization code flow: client id and secret identify the
  app, but a user still has to sign in and consent. The id and secret alone get you nothing there.
- Some APIs refuse client credentials for certain operations (delegated-only endpoints). Then a
  service principal cannot do it, however well configured.

## Secrets

- AADSTS7000215 "invalid client secret": check that the stored value is the secret **value**, not the
  secret **ID**. A 36-character string with four dashes is a GUID, so it is the ID.
- Portal-created secrets live on the app registration. Legacy SharePoint ACS authentication (used by
  the SharePoint Online List connector in Data Factory) validates against the service principal
  object instead, so portal secrets fail with `invalid_request`. Fix: a secret on the service
  principal (`Add-MgServicePrincipalPassword`, needs an admin) or certificate auth. ACS is being
  retired; plan the move to certificates or Graph.
- Importing a self-signed certificate into Key Vault fails with "Failed to create certificate from
  certificate raw data and password" when the content type is not PKCS #12 or the private key was not
  marked exportable.
- Never paste a secret into chat or a ticket. If it happened, rotate it.

## Scheduled work

- User tokens expire, especially under PIM. Scheduled jobs should run as a workspace identity or a
  service principal.
- Figure out which identity actually ran before interpreting a 403.

## Azure CLI logins

- One active login per config directory. Isolate per client or project with `AZURE_CONFIG_DIR`, for
  example `%LOCALAPPDATA%\<project>-azure`, so switching tenants for one client never breaks another.
- Conditional access can block device code login. On Windows, `az config set
  core.enable_broker_on_windows=false` and then a normal browser login works.

## MFA with a password manager

- To store the TOTP code in a password manager: My Sign-ins, Security info, Add sign-in method,
  Microsoft Authenticator, then "I want to use a different authenticator app" and scan the QR code
  (or use "Can't scan image" for the secret).
- If that link is missing, third-party authenticator apps are turned off in the tenant: an admin
  enables "Third-party software OATH tokens" in the Authentication methods policy. The "Hardware
  token" option is only for physical tokens an admin registered.

## An MCP server behind Entra ID

For a remote MCP server that Claude (web, desktop, Code) or another client signs in to with Entra:

- Entra has no dynamic client registration: the client gets the client id and secret of the app
  registration (Claude: advanced settings of the custom connector; Claude Code: `--client-id`,
  `--client-secret` and a fixed `--callback-port` whose `http://localhost:<port>/callback` is a redirect
  URI of the app).
- Claude Code sends the server address `https://<host>/mcp` as OAuth `resource` and only accepts
  protected resource metadata whose resource matches that address. Entra only issues the token when the
  resource is an Application ID URI of the app; otherwise the browser shows "Authentication successful"
  but the token exchange fails with AADSTS9010010 ("The resource parameter provided in the request
  doesn't match with the requested scopes"). Add `https://<host>/mcp` as Application ID URI and let the
  server announce the scope `https://<host>/mcp/<scope>`. The MCP log of the client shows the real
  error (Claude Code: `%LOCALAPPDATA%\claude-cli-nodejs\Cache\<project>\mcp-logs-<server>\`).
- Who may use the server at all: turn on "Assignment required" on the enterprise application and assign
  an Entra group to an app role. Once the app has app roles, the default access role can no longer be
  assigned: create a role such as `User`. Turning it on locks out everyone not in a group yet: add the
  existing users first, guests from other tenants included. A changed membership needs a new sign-in
  before the token carries the role.
- A second app role (for example `KeyUser`) in the `roles` claim lets the server allow certain actions
  to a group only, checked server side.
- Queries as the user: exchange the user's token on-behalf-of for a token of the downstream API, so its
  own permissions and row level security apply. A service principal often cannot query data that has
  row level security at all.
