#!/bin/zsh
# Runs one phase of the instrument: serves out-<phase> on 127.0.0.1:8392, runs the Playwright file, and stops the server.
unset -f node npm npx nvm 2>/dev/null; export PATH=$HOME/.nvm/versions/node/v24.15.0/bin:$PATH
S=<scratch>
W=/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/deadline-week
P=$1; OUTDIR=${2:-$P}
node $S/serve.mjs $S/out-$OUTDIR 8392 & SRV=$!
sleep 1
start=$(date +%s)
cd $W/apps/site && EVIDENCE_DIR=$W/.scratch/deadline-week/evidence PHASE=$P SITE_OUT=$S/out-$OUTDIR SITE_PORT=8392 RESULT_CACHE=$S/api-run/results ONLY=$ONLY pnpm exec playwright test -c $S/pw.config.mjs > $S/phase-$P.log 2>&1
code=$?
echo "phase $P: exit $code, $(( $(date +%s) - start )) s, $(date +%H:%M:%S)" >> $S/phases.txt
kill $SRV
