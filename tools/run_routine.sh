#!/bin/bash
# Starts a scheduled routine as a visible Remote Control session in tmux, with the prompt from
# tools/routines/<name>.txt. Meant for cron on Linux or a server.
#   run_routine.sh <name> [HH[,HH]]   only run in these local hours (24h), otherwise exit quietly
# Example crontab line (append with: (crontab -l; echo "...") | crontab -):
#   7 8 * * * /path/to/repo/tools/run_routine.sh example 8
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
NAME="$1"; HOURS="${2:-}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
LOGDIR="$HOME/.local/share/routines"; mkdir -p "$LOGDIR/work"
LOG="$LOGDIR/$NAME.log"
log() { echo "$(date -Is) $*" >> "$LOG"; }

if [ -n "$HOURS" ] && [[ ",$HOURS," != *",$(date +%H),"* ]]; then exit 0; fi

# Anti double-run: one worker per routine.
exec 9>"$LOGDIR/$NAME.lock"
flock -n 9 || { log "skipped: a worker already owns this routine"; exit 0; }

PROMPT_FILE="$REPO/tools/routines/$NAME.txt"
[ -f "$PROMPT_FILE" ] || { log "FAILED: no prompt file $PROMPT_FILE"; exit 1; }

# Latest runbooks, but never stash someone else's work in progress.
if [ -z "$(git -C "$REPO" status --porcelain)" ]; then git -C "$REPO" pull -q --rebase >> "$LOG" 2>&1
else log "sync skipped: checkout has local changes"; fi

# Stop the previous run of this routine, then start a fresh one.
tmux kill-session -t "routine-$NAME" 2>/dev/null || true
cp "$PROMPT_FILE" "$LOGDIR/$NAME.prompt"
WORK="$LOGDIR/work"; cd "$WORK"
tmux new-session -d -s "routine-$NAME" -x 200 -y 50 -c "$WORK" \
  "claude --dangerously-skip-permissions --remote-control 'Routine-$NAME' \"\$(cat '$LOGDIR/$NAME.prompt')\"; bash"
log "agent started tmux=routine-$NAME; verify the result separately"
