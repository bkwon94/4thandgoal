#!/bin/bash
# The EAGLES store, part 1: Lil Fridge holds E, A, G, L, and S in EAGLES. Then AT-16 and the drop of the last E.
source "$(dirname "$0")/lib.sh"
mkdir -p $EV/AT-12 $EV/AT-16
# need: the count of managers who still need each letter over the open egg words, from the board.
NEED="import json,sys,collections; b=json.load(sys.stdin); need=collections.Counter()
for w in b['words']:
    if w['winner']: continue
for m in b['managers']:
    s=set()
    for w in b['words']:
        if w['winner']: continue
        held=[x for x in w['managers'] if x['roster_id']==m['roster_id']][0]['letters']
        s|=set((collections.Counter(w['word'])-collections.Counter(held)).keys())
    need.update(s)
print('managers who need each letter:', dict(sorted(need.items(), key=lambda kv:(-kv[1],kv[0]))))
print('Lil Fridge in EAGLES:', [x for x in b['words'] if x['word']=='EAGLES'][0]['managers'][2]['letters'])"
OUT=$EV/AT-12/setup.txt; : > $OUT
note "A fresh API with an empty store. The drop of week 9 with 11 eggs gives the 11 letters of the egg words, A to T, one each."
EGGS=""; for n in 1 2 3 4 5 6 7 8 9 10; do EGGS="$EGGS{\"page\":\"/midseason/2026/\",\"target\":\"top10-rb-$n\",\"action\":\"tap2\",\"conditions\":{}},"; done
EGGS="$EGGS{\"page\":\"/midseason/2026/\",\"target\":\"bench-4\",\"action\":\"tap2\",\"conditions\":{}}"
run "curl -s -X POST $E/drop -H '$KEY' -H '$J' -d '{\"week\":9,\"eggs\":[$EGGS]}' | python3 -c 'import json,sys; print([(e[\"id\"], e[\"target\"], e[\"letter\"]) for e in json.load(sys.stdin)[\"eggs\"]])'"
note "Lil Fridge (3) claims E, A, G, L, and S into EAGLES. Each claim takes a token from a check of its egg."
for n in 4 1 5 6 10; do
  TOKEN=$(token /midseason/2026/ top10-rb-$n tap2 '{}')
  run "curl -s -X POST $E/claim -H '$PASS' -H '$J' -d '{\"token\":\"$TOKEN\",\"roster_id\":3,\"word\":\"EAGLES\"}'"
done

OUT=$EV/AT-16/output.txt; : > $OUT
note "The board before: Lil Fridge leads EAGLES and needs only an E. E ties at the top of the need, with 11 managers."
run "curl -s $E/board | python3 -c \"\$NEED\""
note "The drop of six test eggs for week 10:"
EGGS=""; for n in 1 2 3 4 5 6; do EGGS="$EGGS{\"page\":\"/2026/week-08/\",\"target\":\"median-$n\",\"action\":\"tap2\",\"conditions\":{}},"; done
run "curl -s -X POST $E/drop -H '$KEY' -H '$J' -d '{\"week\":10,\"eggs\":[${EGGS%,}]}' | python3 -m json.tool"
run "curl -s -X POST $E/drop -H '$KEY' -H '$J' -d '{\"week\":10,\"eggs\":[${EGGS%,}]}' | python3 -c 'import json,sys; l=[e[\"letter\"] for e in json.load(sys.stdin)[\"eggs\"]]; print(\"letters:\", l, \"E in the drop:\", \"E\" in l)'"

OUT=$EV/AT-12/setup.txt
note "The drop of week 11 with 11 eggs. The guard puts E last, so egg 11 holds E. Its target is the Luck cell of London Cooking (luck-5), for the site shots of AT-37."
EGGS=""; for n in 7 8 9 10 11 12; do EGGS="$EGGS{\"page\":\"/2026/week-08/\",\"target\":\"median-$n\",\"action\":\"tap2\",\"conditions\":{}},"; done
for n in 1 2 3 4; do EGGS="$EGGS{\"page\":\"/2026/week-08/\",\"target\":\"leader-qb-$n\",\"action\":\"tap2\",\"conditions\":{}},"; done
EGGS="${EGGS}{\"page\":\"/midseason/2026/\",\"target\":\"luck-5\",\"action\":\"tap2\",\"conditions\":{}}"
run "curl -s -X POST $E/drop -H '$KEY' -H '$J' -d '{\"week\":11,\"eggs\":[$EGGS]}' | python3 -c 'import json,sys; print([(e[\"id\"], e[\"target\"], e[\"letter\"]) for e in json.load(sys.stdin)[\"eggs\"]])'"
run "curl -s $E/board | python3 -c \"\$NEED\""
