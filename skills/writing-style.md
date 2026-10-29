# Writing in the user's voice

Use this for any message the user sends to a client or an outside party, in a ticket system or by mail.
It was built by reading a few hundred of the user's own replies. If the client has its own style file
(`clients/<slug>/ticket-style.md`) that one wins: it holds the greeting, fixed sentences and literal examples
of that client. The checklist for client messages is in [client-message-writing](client-message-writing.md).

Method to build your own: read 100 or more real replies of the user, count what repeats (greeting, length,
closing line, form of address, what they never write) and write only what repeats as rules. Check the result
against a few real replies before you trust it.

## Form

```text
<Greeting> <first name>,

<sentence>
<sentence>

<question or closing sentence>

<Sign-off>,
<Name>
```

- One fixed greeting with the first name. With two recipients, both names. Chat tools are different: informal,
  no sign-off.
- Mail in a mail client: never add a sign-off or a name when the signature is added automatically. The sign-off
  above only applies to the ticket system.
- A blank line after the greeting, between blocks and before the sign-off. No blank line between sign-off and name.
- A block is one or more sentences that belong together (cause, what was done). A question or closing sentence is
  often its own block. Inside a block every sentence is on its own line. Two short sentences that belong together
  may share a line.
- In a ticket system each block is its own paragraph (`<p>`), each line inside a block a `<br>`.
- Usually 2 to 6 lines of text, up to 8 for an explanation of cause or timing. One or two lines is normal.
- No bullet lists, headings, bold, emoji or dashes. An exclamation mark only in a closing sentence, rarely.

## Tone

- "I" for own work, "we" for the team or company. One form of address, always the informal one if that is what the
  user uses.
- Always polite. What the client has to do is a request or a question, never an order. Own next steps are
  conditional ("we could"), not a promise about who does it.
- Calm, businesslike, friendly. No enthusiasm and no stiff phrases.
- Start with the content. No thanks up front, no repeating the question, no introduction.
- Name people and sources.
- Technical level of the reader: business readers get plain words, technical readers may get pipeline, table and
  branch names.
- Always explain the cause shortly, in plain words. If unsure, make only that sentence careful ("it looks like",
  "probably").
- Admit an own mistake shortly.
- Numbers and hours concrete: "about 12 minutes", "at most 4 hours".

## Structure per kind of message

- Incident solved: cause, what was done, result.
- Same error as before: say it in the first or second sentence, with the earlier ticket number.
- Incident still open: "we saw the error and are working on it", what you see, "I will keep you posted".
- No action needed: the cause and "no action needed from your side for now". No closing sentence.
- Delivery: what changed and where, then the request to check. After the check: thanks and "I moved it to production".
- Answering a question: first the finding, then a hypothesis as a question or advice.
- Asking a question: direct, at the end.
- Following up: one line.
- Appointment: concrete, with the times that do and do not work.
- Hours: an estimate up front, and say when the agreed hours are used up.

## Closing sentence

Optional. Leave it out in a short status message or "no action needed". Otherwise pick one of two or three fixed
variants the user really uses, for example "If you have questions, let me know."

## What the user does not do

- No offer, promise or advice that is not in the instruction.
- No content that is not settled yet. If information is missing, say only what is certain and ask the missing
  question. No estimates, costs or explanations up front.
- No extra sentence that adds nothing. No summary of what the client already knows. No date or time of the
  incident unless needed.
- No long apologies, no "I hope that", no "you are welcome", no "thanks in advance".
- No job title or phone number under the name.
- No to-dos or notes for the user under the draft.

## Chat messages to colleagues

Chat is not a letter. Write like the user chats: one or two loose sentences, spoken language, may start with "yes",
"okay" or "sounds". No build-up of claim, example and conclusion, no "do you get what I mean?". Correct spelling and
no awkward sentences. Long explanations belong in a call.

Generic example of a wrong and a right draft. Wrong: five sentences with a technical metaphor, a list of example
tables and a closing "do you get it?". Right: one sentence with cause and consequence.

## Check

1. Put the draft next to a real example of the same kind of message.
2. Longer than the examples? Cut until it is as long.
3. Blank lines between the blocks, every sentence on its own line, ticket number at the top of the draft.
4. No dashes, no emoji, no offers the user did not give.

## Self-learning

When the user changes a draft, that is the most valuable lesson: write the rule here (or in the client style file)
straight away, with one example of the wrong and the right version.
