# Client presentation (co-branded deck)

Use this as soon as the user asks for a presentation, deck, slides or PowerPoint for a client (sprint
review, advice, monthly meeting, progress update, onboarding, training), or wants an existing client
deck changed. The deck combines the client's house style with your own, and reuses an existing
co-branded format whenever one exists. Follow it without asking whether the user wants it this way.

## 0. Is a deck already in progress

If the user or another agent was already working on this deck, continue from the latest version and never
build something new. The user also edits decks themselves: read the file again before you change anything,
also in the middle of a session. If the client folder is synced to the computer, work on the original file
there. If the file is open, say so and wait, then check afterwards that your changes are in it.

## 1. Look for an existing format first

Before building a single slide, search the client's document store (SharePoint, Drive, Teams chat
files). The client almost always has decks already.

- Search on the client name with file type pptx, and separately on "sprint review", "advice",
  "monthly", "onboarding", "format", "house style", "template".
- Walk the folders of the client site, including the Teams chat files of the people on the project;
  the latest versions often live there.
- Read `clients/<slug>/README.md` and the newest journal for what is already known, including colours.

## 2. A format exists: use it

Read its structure (title, contents, section names, closing slide) and put your content in that same
structure.

Know this limit before losing time (it only applies when the file is not synced locally, see step 0): some document connectors can read text and images but cannot
download file bytes. Without bytes you cannot unpack a pptx, so layouts, logos and brand marks cannot
be inherited. In that case ask the user once to drop that specific file into the chat, and say why.
Once you have it:

- work on a copy, never on the original;
- do all structural work first (duplicate, delete and order slides), fill text afterwards;
- set text per run (python-pptx `run.text`), never via `text_frame.text`, or the formatting is lost;
- validate the result against the original.

## 3. No format: build a co-branded deck on the spot

Get the client's logo from their public website. It is the fastest route and returns real bytes:

```
curl -sSL https://<client-domain> -o site.html
grep -oiE '(src|href)="[^"]*(logo|favicon)[^"]*"' site.html | sort -u
```

Prefer the svg and rasterise it (for example with cairosvg) at around 1600 px wide. Watch for a light
variant meant for dark backgrounds. Fix the exact colours by sampling the logo's pixels, not by eye.

Where to find the rest of the house style, in this order: a house-style folder on the client site, an
existing design deck of the client, their BI theme or reports, hex codes in their website source, and
finally the client README.

A co-branded deck: client colour dominant, your own colour as accent, both logos on the title slide,
your brand mark small on content slides, your own closing slide last. Record the house style you found
in `clients/<slug>/README.md` so the next session does not have to search again. Keep your own house
style (font, colours, logo source, closing slide) in the user's own context, not in this public skill.

## Slide copy rules

- No system names, people or one-off examples on the slide itself; those go in the speaker notes. Plain
  language on the slide, jargon and technique in the notes.
- No labels such as "Decision" or "Question"; they come across as bossy. Plain questions without a label.
- No invented numbers. Only figures you recalculated or that are in the journal or README.
- No em or en dashes, also not in the notes.
- Every slide gets speaker notes.
- One message per slide and nothing twice. A slide that largely repeats another is merged or dropped;
  an extra slide makes the story longer and weaker. Costs only on the cost slide.
- Plain language and few slides: a management team drops out at jargon and long decks. Make costs
  concrete and comparable, for example a table with the number of questions per month against cost.
- Vendor neutral: say "the language model you already have" instead of naming one product again and again,
  unless the deck is about that product.
- Training or knowledge session: teach the room what they can use themselves, do not present what you built.
- If a second version is asked (for example a neutral one without your branding): apply every change to
  both versions.
- Updating an existing deck: only what is asked, no slides, boxes or comparisons of your own. Save on
  the original; when the file is open, say so and wait, never a copy named "(updated)".

## Build and check

Build a new deck with a slide library of your choice (pptxgenjs and python-pptx both work). Afterwards
always run three checks:

1. a structural validation of the pptx;
2. a text extraction (for example markitdown) to check content and catch leftover placeholders;
3. a geometry check for shapes outside the slide or overlapping each other.

A visual render needs LibreOffice. In remote sessions it is sometimes broken (`soffice` then fails on
every file, even plain text). Say so and rely on the three checks; never pretend you have seen the slides.

## Deliver

Hand the file over in the chat, or save on the original when you updated an existing deck. Say which of
the three checks were done and whether you looked at the slides visually. Upload it to the client's document store only when asked, into the
right existing folder, without creating folders of your own.
