# Microsoft 365 groups and guest users

For associations, clubs and small organisations that run a member list as a Microsoft 365 group with
external guests, managed from a shared board mailbox. Verify against the current Microsoft Graph docs
before relying on a detail; Graph changes.

## Signing in without a password

The document or mail connector of an AI tool is usually tied to one account and one tenant, so it
cannot reach a second tenant. Use a device-code sign-in against Microsoft Graph instead: the agent
starts the flow, the user opens `https://login.microsoft.com/device` on their phone, enters the code and
signs in with MFA. No password ever passes through the agent.

- Client: the public Microsoft Graph Command Line Tools app (`14d82eec-204b-4c2f-b7e8-296a70dab67e`)
  accepts delegated scopes, as long as the signed-in user may consent to them.
- Request every scope the task needs in one go, for example
  `Mail.ReadWrite User.ReadWrite.All Group.ReadWrite.All GroupMember.ReadWrite.All
  Directory.ReadWrite.All offline_access`. A missing scope means a second sign-in later.
- Store the token response outside any repo (for example under `%LOCALAPPDATA%`), and use the refresh
  token so later runs need no new sign-in.
- A cached `az` login for that tenant is not a reliable shortcut: getting a Graph token from it can
  fail with AADSTS50020.

## Adding members

1. `POST /invitations` with `invitedUserEmailAddress`, `inviteRedirectUrl`
   (`https://myapplications.microsoft.com`) and `sendInvitationMessage: true`.
2. Add the returned `invitedUser.id` to the group with `POST /groups/{id}/members/$ref`.
3. Check membership with `$top=999` and follow `@odata.nextLink`; the default page size silently
   truncates, and a spot check on page one misses recent additions.

## Finding addresses that no longer work

Every event invitation sent to the group produces automatic replies in the board mailbox. Search it
with `GET /me/messages?$search="..."` (terms such as Undeliverable, Delivery has failed, Automatic
reply, plus local-language variants) and request the body as text with the header
`Prefer: outlook.body-content-type="text"`.

- **Bounces** are reliable: parse the failed address from "Your message to X couldn't be delivered" or
  the block after "Delivery has failed to these recipients or groups". A bounce lists every recipient of
  the original message, so only take the addresses in the failure section.
- **Automatic replies** only count when they say the person left or the mailbox is no longer read
  ("no longer work for", "not in use", "will not be read"). Ordinary out-of-office replies with a return
  date do not count.
- Cross-check every candidate with the current group members and show the list to the user before
  changing anything. Mention separately addresses of the organisation itself and addresses that are not
  in the group.

## Removing members without losing track

- Never just remove someone. Keep an archive group (for example "Former members") and move everyone who
  leaves there: dead address, unsubscribe or board decision. Add to the archive first, then
  `DELETE /groups/{id}/members/{memberId}/$ref` on the member group.
- Create the archive group as a private Microsoft 365 group with `resourceBehaviorOptions:
  ["WelcomeEmailDisabled"]`, otherwise every moved person gets a welcome mail.
- Do not delete the guest users from the tenant: that also removes them from the archive group, and the
  history is gone.
- People who ask to stop receiving Teams invitations usually cannot unsubscribe themselves: the
  invitations come from their group membership, so the fix is moving them to the archive group.

## Counting organisations

Counting distinct email domains among members gives a rough number of organisations. Exclude private
mail domains and the organisation's own domains, and merge known pairs (a company using both `.com` and
`.nl`). A member administration spreadsheet, when there is one, is the real source; compare the group
against it to find organisations that are mailed but not registered as members.
