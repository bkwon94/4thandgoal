#!/bin/bash
# The API evidence on one store: T1 to T4 dropped, then AT-1, 2, 3, 4, 8, 7, 5, 18, 17, 11, 6, 9, 10, 14, and 13.
# Start the API first with a fresh CORNERSTONE_EGGS_DIR. The real path of each route has the /clients/cpc/ prefix.
source "$(dirname "$0")/lib.sh"
mkdir -p $EV/AT-{1,2,3,4,5,6,7,8,9,10,11,13,14,17,18}
T1='{"page":"/midseason/2026/","target":"luck-3","action":"tap3","conditions":{"theme":"light"}}'
T2='{"page":"/2026/week-08/","target":"number-median","action":"tap2","conditions":{"clock":"23:00-00:00"}}'
T3='{"page":"/midseason/2026/","target":"sim-trophy","action":"tap2","conditions":{"sim_champion":12}}'
T4='{"page":"/2026/week-08/","target":"number-closest","action":"tap3","conditions":{}}'
F1='{"page":"/2026/week-08/","target":"number-top-score","action":"tap2","conditions":{}}'
F5='{"page":"/midseason/2026/","target":"heading-luck","action":"tap4","conditions":{}}'
F6='{"page":"/2026/week-08/","target":"heading-awards","action":"hold3","conditions":{}}'
F7='{"page":"/midseason/2026/","target":"heading-arcs","action":"tap2","conditions":{}}'
F9='{"page":"/midseason/2026/","target":"heading-draft","action":"tap2","conditions":{}}'
F10='{"page":"/midseason/2026/","target":"heading-waivers","action":"tap2","conditions":{}}'
F11='{"page":"/midseason/2026/","target":"heading-trades","action":"tap2","conditions":{}}'
F12='{"page":"/midseason/2026/","target":"heading-records","action":"tap2","conditions":{}}'

OUT=$EV/AT-1/setup.txt; : > $OUT
note "The setup of AT-1 to AT-18: an empty store, then the drop of week 9 with T1, T2, and T3, and of week 10 with T4."
note "The API gives each letter by the letter rule. In an empty store the six letters are A, C, D, E, G, L, in the order of the eggs."
run "curl -s -X POST $E/drop -H '$KEY' -H '$J' -d '{\"week\":9,\"eggs\":[$F1,$T1,$T2,$T3,$F5,$F6]}'"
run "curl -s -X POST $E/drop -H '$KEY' -H '$J' -d '{\"week\":10,\"eggs\":[$F7,$T4,$F9,$F10,$F11,$F12]}'"
run "curl -s $E/board | python3 -c 'import json,sys; b=json.load(sys.stdin); print(b[\"counts\"])'"

OUT=$EV/AT-1/output.txt; : > $OUT
note "T1 is egg 2 of week 9, letter C. The real path is /clients/cpc/eggs/check."
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/check -H '$J' -d '{\"page\":\"/midseason/2026/\",\"target\":\"luck-3\",\"action\":\"tap3\",\"conditions\":{\"theme\":\"light\"}}' | tee $EV/AT-1/.answer"
TOKEN=$(head -1 $EV/AT-1/.answer | python3 -c "import json,sys; print(json.load(sys.stdin)['token'])"); rm -f $EV/AT-1/.answer

OUT=$EV/AT-2/output.txt; : > $OUT
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/check -H '$J' -d '{\"page\":\"/midseason/2026/\",\"target\":\"luck-3\",\"action\":\"tap3\",\"conditions\":{\"theme\":\"dark\"}}'"

OUT=$EV/AT-3/output.txt; : > $OUT
note "T2 is egg 3 of week 9, letter D, with the clock window 23:00-00:00 on the clock of the client, America/New_York."
run "TZ=America/New_York date '+%Y-%m-%d %H:%M:%S %Z'"
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/check -H '$J' -d '{\"page\":\"/2026/week-08/\",\"target\":\"number-median\",\"action\":\"tap2\",\"conditions\":{}}'"

OUT=$EV/AT-4/output.txt; : > $OUT
note "T3 is egg 4 of week 9, letter E, on the sim trophy, with the champion Teehee (roster 12). Lil Fridge is roster 3."
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/check -H '$J' -d '{\"page\":\"/midseason/2026/\",\"target\":\"sim-trophy\",\"action\":\"tap2\",\"conditions\":{\"theme\":\"dark\",\"sim_champion\":3}}'"
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/check -H '$J' -d '{\"page\":\"/midseason/2026/\",\"target\":\"sim-trophy\",\"action\":\"tap2\",\"conditions\":{\"theme\":\"dark\",\"sim_champion\":12}}' | sed -E 's/\"token\":\"[^\"]+\"/\"token\":\"<cut>\"/'"

OUT=$EV/AT-8/output.txt; : > $OUT
note "The token of AT-1, a claim with no X-League-Passphrase header. The real path is /clients/cpc/eggs/claim."
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/claim -H '$J' -d '{\"token\":\"$TOKEN\",\"roster_id\":3,\"word\":\"CORNERSTONE\"}'"

OUT=$EV/AT-7/output.txt; : > $OUT
note "The token of AT-1, a claim for Bo Girds, roster 6, the commissioner of values.eggs.commissioner."
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/claim -H '$PASS' -H '$J' -d '{\"token\":\"$TOKEN\",\"roster_id\":6,\"word\":\"CORNERSTONE\"}'"
note "The board after: found stays 0, so T1 stays live."
run "curl -s $E/board | python3 -c 'import json,sys; b=json.load(sys.stdin); print(b[\"counts\"], b[\"latest\"])'"
note "T1 still matches with a token:"
run "curl -s -X POST $E/check -H '$J' -d '$T1' | sed -E 's/\"token\":\"[^\"]+\"/\"token\":\"<cut>\"/'"

OUT=$EV/AT-5/output.txt; : > $OUT
note "The token of AT-1, the roster of Lil Fridge (3), the egg word CORNERSTONE, and the passphrase."
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/claim -H '$PASS' -H '$J' -d '{\"token\":\"$TOKEN\",\"roster_id\":3,\"word\":\"CORNERSTONE\"}'"
run "curl -s $E/board | python3 -c 'import json,sys; b=json.load(sys.stdin); w=[x for x in b[\"words\"] if x[\"word\"]==\"CORNERSTONE\"][0]; print(\"counts\", b[\"counts\"]); print(\"CORNERSTONE\", [(m[\"team\"], m[\"letters\"]) for m in w[\"managers\"] if m[\"letters\"]]); print(\"latest\", b[\"latest\"])'"

OUT=$EV/AT-18/output.txt; : > $OUT
note "T1, T2, T3, and T4 dropped, and T1 claimed. The full board JSON:"
run "curl -s $E/board | python3 -m json.tool"
note "A search of the answer for each page, target, action, and condition name of T1 to T4:"
run "curl -s $E/board | grep -o -E 'midseason|week-08|luck-3|number-median|sim-trophy|number-closest|tap[0-9]|hold[0-9]|theme|clock|sim_champion|\"page\"|\"target\"|\"action\"|\"conditions\"' | sort | uniq -c; echo \"matches: \$(curl -s $E/board | grep -c -E 'midseason|week-08|luck-3|number-median|sim-trophy|number-closest|tap[0-9]|hold[0-9]|theme|clock|sim_champion|\"page\"|\"target\"|\"action\"|\"conditions\"')\""

OUT=$EV/AT-17/output.txt; : > $OUT
note "The claim of AT-5 holds T1, egg 2. The undo runs through make egg-undo against the local API."
run "cd /Users/brian.kwon/repos/cpcfantasyfootball/.claude/worktrees/easter-eggs/apps/pipeline && CORNERSTONE_API_URL=$API CORNERSTONE_COMMISSIONER_KEY_CPC=localkey make egg-undo CLIENT=cpc EGG=2; echo \"exit \$?\""
run "curl -s $E/board | python3 -c 'import json,sys; b=json.load(sys.stdin); w=[x for x in b[\"words\"] if x[\"word\"]==\"CORNERSTONE\"][0]; print(\"counts\", b[\"counts\"]); print(\"Lil Fridge in CORNERSTONE\", [m[\"letters\"] for m in w[\"managers\"] if m[\"roster_id\"]==3]); print(\"latest\", b[\"latest\"])'"
run "sqlite3 -header \$CORNERSTONE_EGGS_DIR/cpc.sqlite 'SELECT rowid, egg_id, roster_id, word, claimed_at, undone_at FROM claims'"
run "curl -s -X POST $E/check -H '$J' -d '$T1' | sed -E 's/\"token\":\"[^\"]+\"/\"token\":\"<cut>\"/'"

OUT=$EV/AT-11/output.txt; : > $OUT
note "After the undo of AT-17, Teehee (12) holds no letter. A new token of T1, letter C, then a claim as a block (word null)."
run "curl -s $E/board | python3 -c 'import json,sys; b=json.load(sys.stdin); print(\"Teehee letters\", {w[\"word\"]: [m[\"letters\"] for m in w[\"managers\"] if m[\"roster_id\"]==12][0] for w in b[\"words\"]})'"
TOKEN=$(token /midseason/2026/ luck-3 tap3 '{"theme":"light"}')
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/claim -H '$PASS' -H '$J' -d '{\"token\":\"$TOKEN\",\"roster_id\":12,\"word\":null}'"

OUT=$EV/AT-6/output.txt; : > $OUT
note "Two checks of T1 give two tokens. The two claims go at once, in the background, for Lil Fridge (3) and Teehee (12)."
A=$(token /midseason/2026/ luck-3 tap3 '{"theme":"light"}'); B=$(token /midseason/2026/ luck-3 tap3 '{"theme":"light"}')
note "token A ${A:0:6}... and token B ${B:0:6}... (cut)"
run "( curl -s -w ' HTTP %{http_code} (Lil Fridge)\n' -X POST $E/claim -H '$PASS' -H '$J' -d '{\"token\":\"$A\",\"roster_id\":3,\"word\":\"CORNERSTONE\"}' & curl -s -w ' HTTP %{http_code} (Teehee)\n' -X POST $E/claim -H '$PASS' -H '$J' -d '{\"token\":\"$B\",\"roster_id\":12,\"word\":\"CORNERSTONE\"}' & wait )"
run "sqlite3 -header \$CORNERSTONE_EGGS_DIR/cpc.sqlite 'SELECT rowid, egg_id, roster_id, word, claimed_at, undone_at FROM claims'"

# The state of AT-9 and AT-10: Lil Fridge holds the C of T1 in CORNERSTONE. If Teehee won AT-6, the undo gives T1 back.
WINNER=$(sqlite3 $CORNERSTONE_EGGS_DIR/cpc.sqlite "SELECT roster_id FROM claims WHERE egg_id=2 AND undone_at IS NULL")
OUT=$EV/AT-9/output.txt; : > $OUT
note "The setup: Lil Fridge (3) holds the one C of CORNERSTONE, from T1. AT-6 left roster $WINNER on T1."
if [ "$WINNER" != "3" ]; then
  run "curl -s -X POST $E/undo -H '$KEY' -H '$J' -d '{\"egg_id\":2}'"
  TOKEN=$(token /midseason/2026/ luck-3 tap3 '{"theme":"light"}')
  run "curl -s -X POST $E/claim -H '$PASS' -H '$J' -d '{\"token\":\"$TOKEN\",\"roster_id\":3,\"word\":\"CORNERSTONE\"}'"
fi
note "T4 is egg 8, egg 2 of week 10, letter C. A token of T4, then a claim for Lil Fridge into CORNERSTONE:"
TOKEN=$(token /2026/week-08/ number-closest tap3 '{}')
run "curl -s -X POST $E/check -H '$J' -d '$T4' | sed -E 's/\"token\":\"[^\"]+\"/\"token\":\"<cut>\"/'"
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/claim -H '$PASS' -H '$J' -d '{\"token\":\"$TOKEN\",\"roster_id\":3,\"word\":\"CORNERSTONE\"}'"

OUT=$EV/AT-10/output.txt; : > $OUT
note "The same state as AT-9: Lil Fridge holds the C of CORNERSTONE. LANSDALE and EAGLES hold no C. The token of AT-9 stays good after the refusal."
note "The board before:"
run "curl -s $E/board | python3 -c 'import json,sys; b=json.load(sys.stdin); print(\"counts\", b[\"counts\"]); print(\"Lil Fridge\", {w[\"word\"]: [m[\"letters\"] for m in w[\"managers\"] if m[\"roster_id\"]==3][0] for w in b[\"words\"]}); print(\"latest\", b[\"latest\"])'"
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/claim -H '$PASS' -H '$J' -d '{\"token\":\"$TOKEN\",\"roster_id\":3,\"word\":null}'"
note "The board after:"
run "curl -s $E/board | python3 -c 'import json,sys; b=json.load(sys.stdin); print(\"counts\", b[\"counts\"]); print(\"Lil Fridge\", {w[\"word\"]: [m[\"letters\"] for m in w[\"managers\"] if m[\"roster_id\"]==3][0] for w in b[\"words\"]}); print(\"latest\", b[\"latest\"])'"
run "sqlite3 -header \$CORNERSTONE_EGGS_DIR/cpc.sqlite 'SELECT rowid, egg_id, roster_id, word, claimed_at, undone_at FROM claims'"

OUT=$EV/AT-14/output.txt; : > $OUT
note "A test drop of one egg for week 11, with the passphrase and no X-Commissioner-Key. The real path is /clients/cpc/eggs/drop."
run "curl -s $E/board | python3 -c 'import json,sys; b=json.load(sys.stdin); print(\"before\", b[\"counts\"], b[\"last_drop\"])'"
run "curl -s -i -X POST $E/drop -H '$PASS' -H '$J' -d '{\"week\":11,\"eggs\":[{\"page\":\"/2026/week-08/\",\"target\":\"heading-leaders\",\"action\":\"tap2\",\"conditions\":{}}]}' | tr -d '\r'"
run "curl -s $E/board | python3 -c 'import json,sys; b=json.load(sys.stdin); print(\"after\", b[\"counts\"], b[\"last_drop\"])'"
run "sqlite3 \$CORNERSTONE_EGGS_DIR/cpc.sqlite 'SELECT count(*) AS eggs_of_week_11 FROM eggs WHERE week=11'"

# AT-13 runs in api-at13.sh.
