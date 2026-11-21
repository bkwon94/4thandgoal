#!/bin/zsh
# AT-49: 10 fresh asks for trade ideas on the front door of cpc, each in a fresh browser context, against the one
# evidence API of the round, with its result cache emptied before each ask. The API log of each run is its segment.
unset -f node npm npx nvm 2>/dev/null; export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$PATH
S=<scratch>
W=/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/deadline-week
E=$W/.scratch/deadline-week/evidence
mkdir -p $E/AT-49
node $S/serve.mjs $S/out-off 8392 & SRV=$!
sleep 1
COMBOS=(375-light 375-dark 768-light 768-dark 1280-light 1280-dark 390-light 390-light 390-light 390-light)
for n in $(seq 1 10); do
  find $S/api-run/results -type f -delete
  a=$(wc -l < $S/api-main.log)
  (cd $W/apps/site && EVIDENCE_DIR=$E PHASE=at49 RUN=$n COMBO=${COMBOS[$n]} SITE_OUT=$S/out-off SITE_PORT=8392 pnpm exec playwright test -c $S/pw.config.mjs --workers 1 > $S/at49-run-$n.log 2>&1)
  sleep 3
  b=$(wc -l < $S/api-main.log)
  { echo "# The API log of AT-49 run $n: lines $((a+1)) to $b of the log of the evidence API, with the Jev and Sleeper HTTP request lines cut."; sed -n "$((a+1)),${b}p" $S/api-main.log | grep -v "typesafe_sdk\|httpx"; } > $E/AT-49/api-run-$n.log
  echo "run $n (${COMBOS[$n]}): $(python3 -c "import json;d=json.load(open('$E/AT-49/run-$n.json'));print(d['outcome'], d['secondsToAnswer'], 's, retry lines', d['retryLineCount'])" 2>&1), 'Trade stream failed' lines: $(grep -c 'Trade stream failed' $E/AT-49/api-run-$n.log), press line: $(grep 'Press of' $E/AT-49/api-run-$n.log | sed 's/.*Press of/Press of/' | tr '\n' ' ')" >> $E/AT-49/runs.txt
done
kill $SRV
