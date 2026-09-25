# Git hygiene when agents commit

- Push to a named branch: `git push origin <branch>`, never `git push origin HEAD` blindly.
- Before a push or a PR, scan the messages, author fields and diff for AI references:

  ```
  git log origin/<base>..HEAD --format='%an %ae %cn %ce%n%B' | grep -i -E 'claude|anthropic|co-authored|generated with|agent|assistant|bot'
  git diff origin/<base>..HEAD | grep -i -E 'co-authored-by|generated with'
  ```

- A commit message describes the change in plain sentences. No verification section, no claims about
  builds the user runs, no "done by the agent".
- Rewriting pushed history (`--force-with-lease`) only when the user explicitly allows it and nobody
  else built on the branch. Once a PR is merged, fix forward with a new commit.
- Other agents and devices work in the same repos: `git fetch` and read `git log` before diagnosing
  or fixing anything.
