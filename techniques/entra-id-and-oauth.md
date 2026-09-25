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
