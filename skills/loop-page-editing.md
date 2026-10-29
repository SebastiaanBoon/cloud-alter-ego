# Read and edit a Microsoft Loop page

Use this as soon as the user sends a Loop page link, asks to add something to a Loop page, or wants feedback on a
Loop page processed (for example team standards in a shared Loop workspace).

## 1. Access

- The Microsoft 365 connector and Graph (also through the Azure CLI) give "access denied" on Loop workspaces. They
  live in separate storage. Do not try again.
- What does work: a browser in which the user is signed in. Claude in Chrome if it is connected, otherwise the
  built-in browser: open the Loop link, the user signs in there. At "Stay signed in?" choose No.

## 2. Read

- Loop does not render the page in one go, so a page text read returns only part. Read the full text with
  JavaScript over the text nodes of the article:
  `document.createTreeWalker(document.querySelector('article'), NodeFilter.SHOW_TEXT)`.
- Jump to a place with find on a piece of text, then scroll to that ref.
- Look in the navigation on the left whether the page has subpages (expand the arrow). Feedback on a main page
  almost always touches the subpages too.

## 3. Edit

- **New paragraph:** click at the end of the paragraph above, press `End` and then `Return`, and type.
- **Bold label** such as "Goal." or "Note.": `ctrl+b`, type the label, `ctrl+b`, type the rest.
- **List:** start a line with `- `. Two times `Return` ends the list.
- **Replace a table cell:** `triple_click` on the cell text selects the whole cell, then type. `Escape` leaves the cell.
- **Add a table row:** click "New" under the table. The row number comes by itself.
- Loop saves automatically. Check after each step with a screenshot, and at the end read the whole page again with
  the TreeWalker to see that all changes are there. Report per page what was changed.

## 4. Content rules

- Follow the structure and tone that are already there, for example Goal, What happens here, What does not belong
  here, Note, and tables with Rule and Example.
- Do not remove existing text. Change a rule only if it contradicts the new agreement. Example: "Tables only" in
  silver became "No files, clean-up as views and models as tables".
- Standards are deliberately technology neutral. No client names in examples. No dashes.
- Afterwards record in the journal of the owning context what was changed on which page.

## Set page icons in bulk

- Do everything in JavaScript, never click on screen coordinates (the screenshot is scaled, those clicks miss).
- Tree items: `[role="treeitem"]`. The name is in the attribute `title`, the icon is the start of `textContent`.
  `innerText` is empty for items out of view.
- Per page: click the tree item, wait until `document.title` is the page name, click the button with the icon
  label, set the emoji picker search input to a search word (native value setter plus an input event) and click
  the emoji button by its `data-emoji` and `title`. Never pick by button order: a half loaded picker gave a wrong
  click and a new empty page in the personal workspace.
- Below about 1000 pixels wide the tree collapses after each click. Make the window wider or reopen it through the tab.
- A JavaScript call stops after 45 seconds. Run the loop in the background (`__run().then(...)`) and read a log.
  Stop the loop at the first error. A hidden pane slows timers; slower but it works.
- Agree a status colour convention with the team (for example red do not use, orange in progress, yellow usable
  with small revisions, green ready) and give subpages the colour of their folder.

## Check

Read the whole page again after editing: are all changes there, and was no existing text removed by accident?

## Self-learning

A new quirk of the editor, with the working key sequence or selector, goes into the matching step straight away.
