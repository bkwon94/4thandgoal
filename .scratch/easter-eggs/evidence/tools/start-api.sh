#!/bin/bash
# Start the local API like make -C apps/api api-evidence, with a temp egg store and the origins of 4173 and 4174.
# Usage: start-api.sh <eggs dir> <log file>
S=${EGGS_SCRATCH:?set EGGS_SCRATCH, a folder outside the repo}
ROOT=/Users/brian.kwon/repos/cpcfantasyfootball/.claude/worktrees/easter-eggs
mkdir -p "$1"
cd "$ROOT/apps/api"
export UV_PROJECT_ENVIRONMENT=$S/api-venv
CORNERSTONE_PASSPHRASE_CPC=localtest CORNERSTONE_COMMISSIONER_KEY_CPC=localkey \
CORNERSTONE_PASSPHRASE_NORCAL=localtest CORNERSTONE_COMMISSIONER_KEY_NORCAL=localkey \
CORNERSTONE_RATE_LIMIT_PER_MINUTE=600 \
CORNERSTONE_ALLOWED_ORIGINS=http://127.0.0.1:4173,http://127.0.0.1:4174 \
CORNERSTONE_REPO=$ROOT CORNERSTONE_EGGS_DIR="$1" \
nohup uv run --exact --package cpc-api uvicorn --factory cornerstone_api.app:app_from_env --port 8080 > "$2" 2>&1 &
echo $! > $S/api.pid
for i in $(seq 1 60); do curl -sf http://127.0.0.1:8080/health >/dev/null && { echo "api up after ${i}x0.5s pid $(cat $S/api.pid)"; exit 0; }; sleep 0.5; done
echo "api did not start"; tail -20 "$2"; exit 1
