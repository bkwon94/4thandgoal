#!/bin/bash
# AT-22: the drop step with the local API stopped, then make egg-drop after the API starts. Usage: api-down-drop.sh <AT-21 file> <step>
# step "down" runs the drop step with no API. Step "up" runs make egg-drop against the running API.
source "$(dirname "$0")/lib.sh"
P=/Users/brian.kwon/repos/cpcfantasyfootball/.claude/worktrees/easter-eggs/apps/pipeline
mkdir -p $EV/AT-22; OUT=$EV/AT-22/output.txt
if [ "$2" = down ]; then
  : > $OUT
  note "The file of AT-21: six spots for week 8, four confirmed. The local API is stopped:"
  run "curl -s -o /dev/null -w 'HTTP %{http_code}\n' $API/health; echo \"curl exit \$?\""
  run "cd $P && CORNERSTONE_API_URL=$API CORNERSTONE_COMMISSIONER_KEY_CPC=localkey uv run --exact --package cornerstone python ../../.scratch/easter-eggs/evidence/tools/drop_step.py cpc 2026 8 $1 2>&1 | grep -v '^INFO\|nstalled'; echo \"exit \${PIPESTATUS[0]}\""
else
  note "The API starts again, with a fresh store:"
  run "curl -s -w ' HTTP %{http_code}\n' $API/health; curl -s $E/board | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"counts\"])'"
  run "cd $P && CORNERSTONE_API_URL=$API CORNERSTONE_COMMISSIONER_KEY_CPC=localkey make egg-drop CLIENT=cpc WEEK=8 EGGS_FILE=$1 2>&1 | grep -v '^INFO\|nstalled'; echo \"exit \${PIPESTATUS[0]}\""
  run "curl -s $E/board | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"counts\"])'"
fi
