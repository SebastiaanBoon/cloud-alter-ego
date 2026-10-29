# Signing in to a client or tool

Use this before every action that needs a login: a cloud portal, a data platform, a ticket system, a
repository host, an API. Signing in costs the user time and tokens and pops windows up on their screen.
The goal is that they sign in once per account at most, and everything after that runs on what already
works.

## Order

1. **A stored login for that client.** Look in `clients/<slug>/tools/` and in the table below. If it
   works, use it and look no further.
2. **A browser where the user is already signed in.** Check, start nothing new: the browser extension
   session, or the built-in browser pane if it is already signed in.
3. **The cloud CLI of the project**, if it already has a valid login (`az account show` with the right
   `AZURE_CONFIG_DIR`). Never start a login yourself.
4. **A token or page from an existing Firefox profile** with single sign-on: keep one profile per client,
   signed in once, and use `python tools/firefox_profile.py <profile> --token <scope>` or
   `... <profile> <url> --text`. It works on a copy, so the user's own Firefox stays untouched. If it hangs
   (a timeout, a federation page), stop.
5. Still not working: walk `skills/when-it-fails.md` first (an earlier route in the journals, another
   session with a browser or the mail connector). Only then say in one line which login is missing and
   ask for a single sign-in at the place that stays valid afterwards. Do not start windows, browser
   instances or device codes yourself.

Elevated roles (PIM and the like) the user activates. A 401 or 403 at a client with such roles: ask
whether the role is active before you debug.

## Never

- Use a password that was pasted into the chat, also when offered: device code or the user's own MFA.
- Put a secret in a file or a repository: it belongs in a key vault.
- Retry a refused login in a loop. Every failed attempt can lock the account; after two, stop and use
  another route (the official API with a token, a session from the user's own browser).

## Where what already works

Keep this table per client in your own copy: system, route, how.

| System | Route | How |
|---|---|---|
| (example) a data platform | the cloud CLI of the project | `AZURE_CONFIG_DIR` per project, a token for the SQL endpoint through the CLI |
| (example) a ticket system | a signed-in browser profile | the token from the page storage, never printed |

## Check

Did the action run without a new window on the user's screen and without a new login for them?

## Self-learning

A route that works or stops working goes in the table straight away.
