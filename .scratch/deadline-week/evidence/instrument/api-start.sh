#!/bin/bash
# Start one local API on port $1 with origin $2, fresh caches under $3, log to $4. Prints the PID.
source /private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/c4dba9fe-f4c7-47fd-97b2-5be959246054/scratchpad/env.sh
set -a; source ~/.secrets >/dev/null 2>&1; set +a
mkdir -p $3/results $3/ask
cd $W/apps/api
env $APIENV CORNERSTONE_RATE_LIMIT_PER_MINUTE=600 CORNERSTONE_ALLOWED_ORIGINS=$2 CORNERSTONE_RESULT_CACHE_DIR=$3/results CORNERSTONE_ASK_DIR=$3/ask \
  nohup uv run --exact --package cpc-api uvicorn --factory cornerstone_api.app:app_from_env --host 127.0.0.1 --port $1 > $4 2>&1 &
echo $!
until curl -sf http://127.0.0.1:$1/health >/dev/null; do sleep 1; done
