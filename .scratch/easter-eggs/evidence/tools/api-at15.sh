#!/bin/bash
# AT-15 on a fresh store: the drop of six test eggs for week 9.
source "$(dirname "$0")/lib.sh"
mkdir -p $EV/AT-15; OUT=$EV/AT-15/output.txt; : > $OUT
note "A fresh API with an empty store in a new CORNERSTONE_EGGS_DIR. The real path is /clients/cpc/eggs/."
run "curl -s $E/board | python3 -c 'import json,sys; b=json.load(sys.stdin); print(b[\"counts\"], b[\"latest\"], b[\"last_drop\"])'"
EGGS=""; for n in 1 2 3 4 5 6; do EGGS="$EGGS{\"page\":\"/midseason/2026/\",\"target\":\"top10-rb-$n\",\"action\":\"tap2\",\"conditions\":{}},"; done
run "curl -s -X POST $E/drop -H '$KEY' -H '$J' -d '{\"week\":9,\"eggs\":[${EGGS%,}]}' | python3 -m json.tool"
run "curl -s -X POST $E/drop -H '$KEY' -H '$J' -d '{\"week\":9,\"eggs\":[${EGGS%,}]}' | python3 -c 'import json,sys; print(\"letters:\", [e[\"letter\"] for e in json.load(sys.stdin)[\"eggs\"]])'"
