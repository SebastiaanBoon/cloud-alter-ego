# Context doctor

Runbook to keep this repo tidy and trustworthy. Run it when the user asks for a check-up, after a busy
week, or when something turns up in the wrong place. Fix what is clear, report the rest in a few lines.

## 1. Git state first

- `git status -sb` and `git branch -a`. A repo stuck halfway through a rebase ("no branch, rebasing")
  blocks every hook. Finish it: journal conflicts are resolved by keeping both sides (the union merge
  in `.gitattributes` normally does this for you), then `git rebase --continue`.
- Branches on the remote that were never merged: read what they add. Useful content goes to the main
  branch in the right folder; then delete the branch.
- Untracked folders: a new context that was never committed is invisible on other devices.

## 2. Structure and indexes

- Every folder in `clients/` and `projects/` has a README and a row in its index, and every index row
  points to an existing folder.
- No loose files or new folders in the root. Runbooks in `skills/`, technical knowledge in
  `techniques/`, context-specific runbooks and scripts inside that context.
- Every skill is listed in `skills/README.md`, every technique in `techniques/README.md`.

## 3. Duplicates and stale facts

- The same fact in two places drifts apart. Keep it once, in the most specific place (a project README
  beats a general profile file), and link to it from elsewhere.
- Remove empty headings and placeholder sections that hold no information.
- Paths mentioned in the files still exist.

## 4. Local agent memories

Agents with a built-in memory store keep files per working folder (for Claude Code:
`~/.claude/projects/*/memory/`). Read them all and check each one against this repo:

- a rule or procedure that is only in a memory file: move it here (preferences, skill, project README)
  and let the memory point to it;
- a memory that contradicts a current rule here: remove or correct it;
- a memory that points to a moved or renamed file: fix the path.

## 5. Agent instructions

The global instruction files of every agent (for example `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`)
must list the same contexts and paths as this repo.

## Report

Plain bullets: what was wrong, what you fixed, what the user still has to decide. Write one journal line.
