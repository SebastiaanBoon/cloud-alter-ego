# Read WhatsApp through WhatsApp Web

Lets an agent read your WhatsApp messages by driving `web.whatsapp.com` with the Claude extension
in Chrome. Read only.

## Why this route

- No installation, no extra linked device, no breach of the WhatsApp terms.
- The alternatives fall away:
  - A local bridge (an MCP server built on Baileys or whatsmeow) links as an extra device. That is
    against the terms and can get the number blocked. Rules of thumb seen in practice: under 30
    messages per hour counts as safe, over 60 as dangerous, and re-linking after about 20 days.
  - The official Meta API only works for business numbers and cannot read personal chats.
  - The local database of WhatsApp Desktop on Windows holds no message archive, only a small
    encrypted session file. On macOS it does, on Windows it does not.

## Workflow

1. Chrome runs and the Claude extension is connected.
2. Open a tab on `https://web.whatsapp.com`. You are logged in there, so no QR code is needed while
   the session stays valid.
3. Read the chat list without clicking, with JavaScript:
   `document.querySelector('#pane-side').querySelectorAll('[role="row"]')`, and `innerText` per row.
4. Open a conversation by clicking its row, then read the messages with `#main div[role="row"]`.
   Outgoing messages carry `.message-out`, incoming ones `.message-in`.
5. On a first sync the bottom shows "Syncing chats" with a counter. Wait until it finishes,
   otherwise the list is still empty.

## Limits

- Only what is in the page is readable. Older messages need scrolling in the conversation.
- Works only while Chrome is open and the WhatsApp Web session is valid.
- This is not a searchable archive. For that you need a local bridge, with the blocking risk above.
  That choice is yours.
- **Send nothing.** Read only, unless you explicitly ask to send a message.

## Lessons learned

- **WhatsApp search matches word beginnings only.** Searching for part of a word finds nothing; use
  full words and their variants.
- **The chat list and the message pane are virtualized.** Only 15 to 20 rows exist in the DOM at a
  time and older rows disappear while scrolling. Reading once after scrolling misses almost
  everything. Collect new rows into a `window.__set` (a Set keyed on something unique such as
  `data-pre-plain-text`) during every scroll step and return the collected result at the end.
- **The "Click here to get older messages from your phone" button ignores `element.click()`.** It
  needs a real mouse event: a click on coordinates, or a dispatched
  `pointerdown/mousedown/mouseup/click` sequence with `bubbles: true`. Without it the local history
  stays limited to roughly the last two months.
- **The WhatsApp backup on Google Drive is not reachable.** It lives in Drive's hidden
  `appDataFolder`, which never shows up in file lists or search, not even for the account owner.
- **The most reliable route to a full history: export it yourself.** On the phone: open the chat,
  tap the name, "Export chat", "Without media", and mail it to yourself or paste it into the
  session. That gives a zip with a readable .txt (one line per message: date, time, sender, text)
  plus .vcf contact cards of saved contacts in the chat.
- **The .vcf contact cards can contain a `BDAY` field.** That is a certain birthday, no guessing
  needed. Grep for it first.
- **Deriving a birthday from congratulations:** collect all congratulation lines, group them by
  calendar day regardless of the year. A day that returns four to six years in a row is very
  reliable. The person having the birthday never congratulates themselves, so whoever never appears
  as a sender in that cluster over several years is the one. Cross-check with a known date.

## Pairing, background tabs and polls

- **Pairing when the user is not at the computer:** on the sign-in screen choose "Link with phone
  number instead", fill in their number (through the value setter plus an `input` event; typing does
  not arrive when the window is not in front), press Next and give them the 8-character code from
  `document.body.innerText`. They enter it on the phone under Linked devices, Link with phone number.
- **Background tab:** when another tab is in front the browser pauses rendering. Screenshots, `find`
  and `await setTimeout` then hang, and animated panels (such as poll details) do not open. Use only
  synchronous script calls without timers.
- **Close the "What's new" screen first:** after a new pairing a Continue dialog covers the page and
  blocks clicks.
- **Who did (not) vote in a poll:** read it from the data, not the screen. IndexedDB `model-storage`:
  `group-metadata` (subject to group id), `participant` (members per group), `poll-votes` (per vote
  `parentMsgKey`, `sender`, encrypted choice) and `contact` (member id to name and number). The choices
  themselves are decrypted in `window.require('WAWebCollections').PollVote`: an empty list means the
  vote was withdrawn and counts as not voted. Check the count against "X of Y members voted".
- A pasted `@Name` is plain text. A real mention needs typing @ in WhatsApp and picking the name.
