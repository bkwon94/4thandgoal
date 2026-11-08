#!/bin/bash
# The EAGLES store, part 2, AT-12: Lil Fridge claims the last E into EAGLES, then Teehee claims another E into EAGLES.
source "$(dirname "$0")/lib.sh"
OUT=$EV/AT-12/output.txt; : > $OUT
note "The state of AT-12/setup.txt: Lil Fridge (3) holds E, A, G, L, and S in EAGLES. Egg 28 holds E. The real path is /clients/cpc/eggs/."
run "curl -s $E/board | python3 -c 'import json,sys; b=json.load(sys.stdin); w=[x for x in b[\"words\"] if x[\"word\"]==\"EAGLES\"][0]; print(\"EAGLES winner\", w[\"winner\"], \"| Lil Fridge\", [m[\"letters\"] for m in w[\"managers\"] if m[\"roster_id\"]==3][0])'"
TOKEN=$(token /midseason/2026/ luck-5 tap2 '{}')
note "A token from a check of egg 28, then the claim of Lil Fridge into EAGLES:"
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/claim -H '$PASS' -H '$J' -d '{\"token\":\"$TOKEN\",\"roster_id\":3,\"word\":\"EAGLES\"}'"
note "Another E for Teehee (12): the drop of week 12 with 11 eggs. EAGLES has a winner, so the letter rule reads only CORNERSTONE and LANSDALE."
EGGS=""; for n in 1 2 3 4 5 6 7 8 9 10 11; do EGGS="$EGGS{\"page\":\"/midseason/2026/\",\"target\":\"look-ahead-1-$((n+3))\",\"action\":\"tap2\",\"conditions\":{}},"; done
run "curl -s -X POST $E/drop -H '$KEY' -H '$J' -d '{\"week\":12,\"eggs\":[${EGGS%,}]}' | python3 -c 'import json,sys; print([(e[\"id\"], e[\"target\"], e[\"letter\"]) for e in json.load(sys.stdin)[\"eggs\"]])' | tee /tmp/ee-w12.txt"
T=$(python3 -c "import ast; l=ast.literal_eval(open('/tmp/ee-w12.txt').read()); print([t for i,t,x in l if x=='E'][0])"); rm -f /tmp/ee-w12.txt
TOKEN=$(token /midseason/2026/ $T tap2 '{}')
note "A token from a check of the E egg on $T, then the claim of Teehee into EAGLES:"
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/claim -H '$PASS' -H '$J' -d '{\"token\":\"$TOKEN\",\"roster_id\":12,\"word\":\"EAGLES\"}'"
note "The board:"
run "curl -s $E/board | python3 -c 'import json,sys; b=json.load(sys.stdin); print(\"counts\", b[\"counts\"]); [print(w[\"word\"], \"winner:\", w[\"winner\"]) for w in b[\"words\"]]; print(\"Teehee in EAGLES\", [m[\"letters\"] for m in [x for x in b[\"words\"] if x[\"word\"]==\"EAGLES\"][0][\"managers\"] if m[\"roster_id\"]==12][0]); print(\"latest\", b[\"latest\"][:2])'"
