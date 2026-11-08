#!/bin/bash
# AT-21 and AT-23: the drop step of the publish against the running local API. Usage: api-publish-drop.sh <AT-21 file> <AT-23 file>
source "$(dirname "$0")/lib.sh"
P=/Users/brian.kwon/repos/cpcfantasyfootball/.claude/worktrees/easter-eggs/apps/pipeline
STEP="cd $P && CORNERSTONE_API_URL=$API CORNERSTONE_COMMISSIONER_KEY_CPC=localkey uv run --exact --package cornerstone python ../../.scratch/easter-eggs/evidence/tools/drop_step.py"
mkdir -p $EV/AT-21 $EV/AT-23
OUT=$EV/AT-21/output.txt; : > $OUT
note "The drop step is the last step of make publish: drop_after_publish of cornerstone/egg_drop.py. drop_step.py runs only that step, so no commit and no push run."
note "The temp egg file: six spots for week 8, four of them confirmed."
run "grep -c '^\[\[eggs\]\]' $1; grep -c 'confirmed = true' $1"
note "The board before:"
run "curl -s $E/board | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"counts\"])'"
run "$STEP cpc 2026 8 $1 2>&1 | grep -v '^INFO\|nstalled'; echo \"exit \${PIPESTATUS[0]}\""
note "The board after:"
run "curl -s $E/board | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"counts\"])'"
OUT=$EV/AT-23/output.txt; : > $OUT
note "The temp egg file: six spots for week 8, none confirmed."
run "grep -c '^\[\[eggs\]\]' $2; grep -c 'confirmed = true' $2"
run "$STEP cpc 2026 8 $2 2>&1 | grep -v '^INFO\|nstalled'; echo \"exit \${PIPESTATUS[0]}\""
