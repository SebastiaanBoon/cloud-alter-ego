# Writing client messages (mail and ticket system)

Use this before every message to a client or other outsider, also when the user only says "fix this
message" or "what do we tell them". A chat tool such as Teams is different, see Channel at the bottom.

## Template

```text
<Greeting> <first name>,

<One line of context: what is it about, and has it happened before.>

<What happened and why, one sentence per line.>
<What went fine, or what the client does not notice.>

<What we did, concrete and in the past tense.>

<Fixed closing line, for example: If there are any questions, let me know.>

<Sign-off>
<Name>
```

Blocks with an empty line between them, inside a block every sentence on its own line. Never merge
sentences into one paragraph. For a delivery, the last block asks the client to check the result in the
development environment. Use the greeting and sign-off the user normally uses.

## Check before you hand it over

1. Every sentence on its own line, blocks separated by an empty line?
2. Short sentences: one thought each, no chain of subclauses.
3. Concrete: what exactly was changed, in plain words with numbers ("now waits 5 minutes instead of 30
   seconds"), not "we adjusted it".
4. Finished work in the past tense ("We changed ..."), never "I propose" when the user says it is done or
   will be done. Unsure whether it is done yet: write the message as the user means it and add one line
   below it.
5. Has it happened before? Say so ("This is the same error as last week").
6. No dates or times of the incident unless the user names them; the client knows which ticket it is.
7. No technique the recipient does not act on: no pipeline, table or resource names, error codes, SKUs or
   settings. Say "the process", "the database", "the reports".
8. Unconfirmed cause: only that sentence carefully ("It looks like ..."), the rest direct. Never send an
   unproven cause.
9. No offer, commitment or advice that is not in the user's text or instruction. The fixed closing line is
   the exception.
10. First person or "we" as the user writes, plain words, not stiff.
11. The user's own text is the base: keep its length, order and good sentences. On a correction change only
    the part they mentioned.
12. Do not copy the user's instructions word for word, put them in your own subtle wording. Their
    instruction is the message, not the text.
13. No remarks or to-dos for the user under the message, except one line when something in the message is
    not true yet.

## Keep the user's voice

- First person, direct, plain words. Stiff corporate phrases ("We hereby...") read as not written by them.
- Put your version next to their draft. Every sentence must be something the recipient needs to know.
- A sentence they approved stays exactly as it is.
- Prettify means only wording and punctuation, no new content.
- Match the level of the recipient: a non-technical manager gets what happened, the cause in plain words
  and what was done.

## Channel

- Mail and ticket system: the template above. Via Microsoft Graph: HTML body with one `<p>` per line.
- Chat (Teams and similar): no template. Short lines in the tone of the existing chat, no greeting block.
- Use the channel the client already uses for that topic.

## Self-learning step

When the user corrects a message in a way that is new, add it to this checklist or to the background
file right away, with what went wrong. The same mistake should not cost a second round.
