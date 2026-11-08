#!/bin/bash
# The API evidence of the catalog of ticket 07 and ticket 10 on one fresh store: AT-53, AT-54, AT-55, and AT-56.
# Start the API first with a fresh CORNERSTONE_EGGS_DIR. The real path of each route has the /clients/cpc/ prefix.
source "$(dirname "$0")/lib.sh"
mkdir -p $EV/AT-{53,54,55,56}
DB=\$CORNERSTONE_EGGS_DIR/cpc.sqlite
CUT="sed -E 's/\"token\":\"[^\"]+\"/\"token\":\"<cut>\"/'"

OUT=$EV/AT-53/output.txt; : > $OUT
note "A test egg on the 404 hero (not-found-hero) with the action tap2 and the condition not_found = true, dropped with the page /golden-egg/."
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/drop -H '$KEY' -H '$J' -d '{\"week\":9,\"eggs\":[{\"page\":\"/golden-egg/\",\"target\":\"not-found-hero\",\"action\":\"tap2\",\"conditions\":{\"not_found\":true}}]}'"
run "sqlite3 -header $DB 'SELECT id, week, page, target, action, conditions FROM eggs'"
for PAGE in /golden-egg /no-such-page/ /2026/week-99; do
  note "The check from the 404 page of $PAGE, with not_found true:"
  run "curl -s -w '\nHTTP %{http_code}' -X POST $E/check -H '$J' -d '{\"page\":\"$PAGE\",\"target\":\"not-found-hero\",\"action\":\"tap2\",\"conditions\":{\"theme\":\"light\",\"not_found\":true}}' | $CUT"
done
note "The check from /golden-egg/ with no not_found:"
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/check -H '$J' -d '{\"page\":\"/golden-egg/\",\"target\":\"not-found-hero\",\"action\":\"tap2\",\"conditions\":{\"theme\":\"light\"}}'"

OUT=$EV/AT-54/output.txt; : > $OUT
note "A test egg on the verdict word of the analyzer (route /analyze/) with the action tap2 and trade_teams [1, 3]: The Blue Tent (1) and Lil Fridge (3)."
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/drop -H '$KEY' -H '$J' -d '{\"week\":10,\"eggs\":[{\"page\":\"/analyze/\",\"target\":\"verdict-word\",\"action\":\"tap2\",\"conditions\":{\"trade_teams\":[1,3]}}]}'"
for TEAMS in "1,3" "3,1" "1,12" "1,3,12"; do
  note "The check with trade_teams [$TEAMS]:"
  run "curl -s -w '\nHTTP %{http_code}' -X POST $E/check -H '$J' -d '{\"page\":\"/analyze/\",\"target\":\"verdict-word\",\"action\":\"tap2\",\"conditions\":{\"theme\":\"light\",\"trade_teams\":[$TEAMS],\"trade_answer\":\"yes\"}}' | $CUT"
done
note "The drop of an egg with the old trade condition, an exact trade key:"
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/drop -H '$KEY' -H '$J' -d '{\"week\":11,\"eggs\":[{\"page\":\"/analyze/\",\"target\":\"verdict-word\",\"action\":\"tap2\",\"conditions\":{\"trade\":\"1:4046|3:6794\"}}]}'"
run "sqlite3 $DB 'SELECT count(*) AS eggs_of_week_11 FROM eggs WHERE week=11'"

OUT=$EV/AT-55/output.txt; : > $OUT
note "The drop of one egg with each old action. Each drop is week 12."
for ACTION in tap3 tap5 hold1 hold3 hold5; do
  run "curl -s -w '\nHTTP %{http_code}' -X POST $E/drop -H '$KEY' -H '$J' -d '{\"week\":12,\"eggs\":[{\"page\":\"/midseason/2026/\",\"target\":\"luck-5\",\"action\":\"$ACTION\",\"conditions\":{}}]}'"
done
run "sqlite3 $DB 'SELECT count(*) AS eggs_of_week_12 FROM eggs WHERE week=12'"

OUT=$EV/AT-56/drop.txt; : > $OUT
note "The drop of an egg with the action hold on the target blurb-luck:"
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/drop -H '$KEY' -H '$J' -d '{\"week\":13,\"eggs\":[{\"page\":\"/midseason/2026/\",\"target\":\"blurb-luck\",\"action\":\"hold\",\"conditions\":{}}]}'"
run "sqlite3 $DB \"SELECT count(*) AS eggs_on_blurb_luck FROM eggs WHERE target='blurb-luck'\""
note "The drop of an egg with the action tap2 on the target blurb-luck:"
run "curl -s -w '\nHTTP %{http_code}' -X POST $E/drop -H '$KEY' -H '$J' -d '{\"week\":13,\"eggs\":[{\"page\":\"/midseason/2026/\",\"target\":\"blurb-luck\",\"action\":\"tap2\",\"conditions\":{}}]}'"
run "sqlite3 -header $DB \"SELECT id, week, page, target, action FROM eggs WHERE target='blurb-luck'\""
