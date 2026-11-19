#!/bin/bash
# AT-49: 10 fresh asks for trade ideas on the front door of cpc, each against a freshly started local API with empty caches.
source /private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/c4dba9fe-f4c7-47fd-97b2-5be959246054/scratchpad/env.sh
read PS PA < $S/ports.txt
mkdir -p $E/AT-49
COMBOS=(375-light 375-dark 768-light 768-dark 1280-light 1280-dark 390-light 390-light 390-light 390-light)
for n in $(seq ${START:-1} 10); do
  rm -rf $S/at49/run-$n
  pid=$($S/api-start.sh $PA http://127.0.0.1:$PS $S/at49/run-$n $E/AT-49/api-run-$n.log | head -1)
  (cd $W/apps/site && EVIDENCE_DIR=$E PHASE=at49 RUN=$n COMBO=${COMBOS[$((n-1))]} SITE_OUT=$S/out-off SITE_PORT=$PS pnpm exec playwright test -c $S/pw.config.mjs --workers 1 > $S/at49-run-$n.log 2>&1)
  sleep 3
  pkill -f "port $PA" ; sleep 3
  echo "run $n (${COMBOS[$((n-1))]}): $(python3 -c "import json;d=json.load(open('$E/AT-49/run-$n.json'));print(d['outcome'], d['secondsToAnswer'], 's, retry lines', d['retryLineCount'])" 2>&1), 'Trade stream failed' lines in api-run-$n.log: $(grep -c 'Trade stream failed' $E/AT-49/api-run-$n.log)"
done
