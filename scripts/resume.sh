#!/bin/sh
# Resume a Claude Code session for this repo: given a session id, that one; else the most recent.
cd "$(dirname "$0")/.." || exit 1
if [ -n "$1" ]; then exec claude --resume "$1" --dangerously-skip-permissions
else exec claude --continue --dangerously-skip-permissions; fi
