#!/bin/bash
S=${EGGS_SCRATCH:?set EGGS_SCRATCH, a folder outside the repo}
pid=$(lsof -nP -tiTCP:8080 -sTCP:LISTEN); [ -n "$pid" ] && ps -o command= -p $pid | grep -q cornerstone_api && kill $pid
[ -f $S/api.pid ] && kill $(cat $S/api.pid) 2>/dev/null
for i in $(seq 1 20); do lsof -nP -tiTCP:8080 -sTCP:LISTEN >/dev/null || { echo stopped; exit 0; }; sleep 0.3; done; echo "still up"
