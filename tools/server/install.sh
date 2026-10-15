#!/bin/bash
# Installs the session units, batch throttling and load guard. Run as root from this checkout:
#   sudo bash tools/server/install.sh [agent-user]     (default user: agent)
# Idempotent. Session configs go in /etc/claude-sessions/<name>.conf (see session.example.conf).
set -euo pipefail
U="${1:-agent}"
SRC="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
for f in claude-session@.service batch-run load-guard run-session sudoers.example; do
  sed "s/__AGENT_USER__/$U/g" "$SRC/$f" > "$TMP/$f"
done
install -d /usr/local/lib/claude-sessions /etc/claude-sessions /etc/systemd/system/ssh.service.d
install -m 755 "$TMP/run-session" "$SRC/session-state" "$SRC/ensure-sessions" /usr/local/lib/claude-sessions/
install -m 755 "$SRC/batch" /usr/local/bin/batch
install -m 755 "$TMP/batch-run" "$TMP/load-guard" /usr/local/sbin/
install -m 644 "$TMP/claude-session@.service" "$SRC"/claude-sessions-check.service "$SRC"/claude-sessions.timer \
  "$SRC"/claude.slice "$SRC"/batch.slice "$SRC"/load-guard.service "$SRC"/load-guard.timer /etc/systemd/system/
install -m 644 "$SRC/ssh-priority.conf" /etc/systemd/system/ssh.service.d/priority.conf
install -m 440 "$TMP/sudoers.example" /etc/sudoers.d/claude-sessions
visudo -cf /etc/sudoers.d/claude-sessions >/dev/null
systemctl daemon-reload
systemctl enable -q --now claude-sessions.timer load-guard.timer
systemctl try-restart ssh.service
