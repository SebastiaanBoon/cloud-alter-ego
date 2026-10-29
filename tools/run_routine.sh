#!/bin/bash
# Starts a scheduled routine as a visible Remote Control session in tmux, with the prompt from
# tools/routines/<name>.txt. Meant for cron on Linux or a server, or for a claude.ai routine that
# dispatches to the server over ssh.
#   run_routine.sh <name> [HH[,HH]] [--codex]   only run in these local hours (24h), otherwise exit quietly
#   run_routine.sh <name> --idle                put the routine session online without a task if it is not running
# Example crontab line (append with: (crontab -l; echo "...") | crontab -):
#   7 8 * * * /path/to/repo/tools/run_routine.sh example 8
# Optional per routine:
#   tools/routines/<name>.secrets   lines "<key vault> <secret name>": each secret is written to a file only
#                                   this user can read, and its path is added to the prompt
#   /etc/claude-sessions/routine-<name>.conf   run it through the systemd unit of tools/server, so it continues
#                                   after an outage
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
NAME="$1"; HOURS=; IDLE=; CODEX=
for arg in "${@:2}"; do
  case "$arg" in --idle) IDLE=1 ;; --codex) CODEX=1 ;; *) HOURS="$arg" ;; esac
done
REPO="$(cd "$(dirname "$0")/.." && pwd)"
LOGDIR="$HOME/.local/share/routines"; mkdir -p "$LOGDIR/work" "$LOGDIR/keys"
LOG="$LOGDIR/$NAME.log"
log() { echo "$(date -Is) $*" >> "$LOG"; }

if [ -n "$HOURS" ] && [[ ",$HOURS," != *",$(date +%H),"* ]]; then exit 0; fi

# Anti double-run: one worker per routine.
exec 9>"$LOGDIR/$NAME.lock"
flock -n 9 || { log "skipped: a worker already owns this routine"; exit 0; }

# One fixed session per routine, so it shows up once in Remote Control instead of a new copy per run.
ID_FILE="$LOGDIR/$NAME.session"
[ -f "$ID_FILE" ] || cat /proc/sys/kernel/random/uuid > "$ID_FILE"
ID=$(cat "$ID_FILE")
WORK="$LOGDIR/work"
TRANSCRIPT="$HOME/.claude/projects/$(echo "$WORK" | sed 's/[^A-Za-z0-9]/-/g')/$ID.jsonl"
RC_NAME="Routine-$NAME"
# Trust the working folder, otherwise Claude waits on the trust question.
trust() { jq --arg p "$1" '.projects[$p].hasTrustDialogAccepted=true' ~/.claude.json > ~/.claude.json.tmp.$$ && mv ~/.claude.json.tmp.$$ ~/.claude.json; }

if [ -n "$IDLE" ]; then
  if [ -f "/etc/claude-sessions/routine-$NAME.conf" ]; then sudo -n /usr/local/lib/claude-sessions/ensure-sessions; exit 0; fi
  tmux has-session -t "routine-$NAME" 2>/dev/null && exit 0
  [ -f "$TRANSCRIPT" ] || { log "idle skipped: no transcript for $ID yet, not starting a new session"; exit 0; }
  cd "$WORK"; trust "$WORK"
  tmux new-session -d -s "routine-$NAME" -x 200 -y 50 -c "$WORK" \
    "claude --dangerously-skip-permissions --model sonnet --resume $ID --remote-control '$RC_NAME'; bash"
  log "idle session started session=$ID"; exit 0
fi

PROMPT_FILE="$REPO/tools/routines/$NAME.txt"
[ -f "$PROMPT_FILE" ] || { log "FAILED: no prompt file $PROMPT_FILE"; exit 1; }

# Latest runbooks, but never stash someone else's work in progress.
if [ -z "$(git -C "$REPO" status --porcelain)" ]; then git -C "$REPO" pull -q --no-rebase >> "$LOG" 2>&1 || log "sync failed: using existing runbooks"
else log "sync skipped: checkout has local changes"; fi

PROMPT="$(cat "$PROMPT_FILE")"
SECRETS="$REPO/tools/routines/$NAME.secrets"
if [ -f "$SECRETS" ]; then
  while read -r VAULT SECRET; do
    [ -n "${SECRET:-}" ] || continue
    KEY="$LOGDIR/keys/$SECRET"
    ( umask 077; az keyvault secret show --vault-name "$VAULT" -n "$SECRET" --query value -o tsv > "$KEY.tmp" ) \
      && mv "$KEY.tmp" "$KEY" || { rm -f "$KEY.tmp"; log "FAILED: secret $SECRET not readable from $VAULT"; exit 1; }
    PROMPT="$PROMPT
The secret $SECRET is in the file $KEY. Never print it."
  done < "$SECRETS"
fi
printf '%s' "$PROMPT" > "$LOGDIR/$NAME.prompt"

# Stop the previous run of this routine.
tmux kill-session -t "routine-$NAME" 2>/dev/null || true
STAMP=$(date +%Y-%m-%d_%H%M%S)

if [ -n "$CODEX" ]; then
  CWORK="$LOGDIR/codex-work/$STAMP"; mkdir -p "$CWORK"
  tmux new-session -d -s "routine-$NAME" -x 200 -y 50 -c "$CWORK" \
    "codex exec --skip-git-repo-check -C '$CWORK' -s danger-full-access -c 'approval_policy=\"never\"' -o '$LOGDIR/$NAME-$STAMP-result.txt' - < '$LOGDIR/$NAME.prompt' 2>&1 | tee '$LOGDIR/$NAME-$STAMP-agent.log'; echo \"agent_exited \$(date -Is)\" >> '$LOG'"
  log "agent started engine=codex tmux=routine-$NAME; verify the result separately"
  exit 0
fi

# With a systemd unit for this routine: leave the prompt for the unit and restart it. The unit resumes the
# fixed session with this prompt; if it drops halfway, it continues after the restart.
if [ -f "/etc/claude-sessions/routine-$NAME.conf" ]; then
  cp "$LOGDIR/$NAME.prompt" "$LOGDIR/$NAME.pending"
  sudo -n systemctl restart "claude-session@routine-$NAME.service"
  log "agent started engine=claude session=$ID unit=claude-session@routine-$NAME; verify the result separately"
  exit 0
fi

# Executing a runbook needs no top model: Sonnet.
cd "$WORK"; trust "$WORK"
if [ -f "$TRANSCRIPT" ]; then SESSION="--resume $ID"; else SESSION="--session-id $ID"; fi
tmux new-session -d -s "routine-$NAME" -x 200 -y 50 -c "$WORK" \
  "claude --dangerously-skip-permissions --model sonnet $SESSION --remote-control '$RC_NAME' \"\$(cat '$LOGDIR/$NAME.prompt')\"; bash"
log "agent started engine=claude session=$ID tmux=routine-$NAME; verify the result separately"
