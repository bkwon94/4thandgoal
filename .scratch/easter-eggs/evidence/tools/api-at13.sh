#!/bin/bash
# AT-13: 61 checks from one address, then the analyzer routes for that address. Run it on a freshly started API.
source "$(dirname "$0")/lib.sh"
T2='{"page":"/2026/week-08/","target":"number-median","action":"tap2","conditions":{"clock":"23:00-00:00"}}'
OUT=$EV/AT-13/output.txt; : > $OUT
note "61 checks of T2 from the address 10.13.0.1, set in the header Fly-Client-IP, as the Fly proxy sets it."
note "No check came from this address before. The status of each answer:"
for i in $(seq 1 61); do
  printf 'check %2d: ' $i >> $OUT
  curl -s -o /dev/null -D - -w 'HTTP %{http_code}\n' -X POST $E/check -H 'Fly-Client-IP: 10.13.0.1' -H "$J" -d "$T2" | tr -d '\r' | grep -E '^HTTP |^retry-after' | tr '\n' ' ' >> $OUT
  echo >> $OUT
done
printf '\n' >> $OUT
note "The analyzer routes for the same address. The teams route answers 200. The analyze route answers 422 for an empty body, so it runs no Claude call, and it is not 429."
run "curl -s -o /dev/null -w 'teams HTTP %{http_code}\n' '$API/clients/cpc/teams?season=2026' -H 'Fly-Client-IP: 10.13.0.1' -H '$PASS'"
run "curl -s -w '\nanalyze HTTP %{http_code}\n' -X POST $API/clients/cpc/analyze -H 'Fly-Client-IP: 10.13.0.1' -H '$PASS' -H '$J' -d '{}' | cut -c1-200"
note "One real analyze call for the blocked address 10.13.0.1, with a real Claude call: Chris Rodriguez Jr. (10219) of The Blue Tent for Travis Kelce (1466) of Lil Fridge."
run "curl -s -w '\\nanalyze HTTP %{http_code}\\n' -X POST $API/clients/cpc/analyze -H 'Fly-Client-IP: 10.13.0.1' -H '$PASS' -H '$J' -d '{\"season\":2026,\"asker\":1,\"sides\":[{\"roster_id\":1,\"gives\":[{\"player_id\":\"10219\",\"to\":3}]},{\"roster_id\":3,\"gives\":[{\"player_id\":\"1466\",\"to\":1}]}]}' | python3 -c 'import sys; t=sys.stdin.read(); body,_,code=t.rpartition(\"analyze HTTP\"); import json; d=json.loads(body); print(\"decision:\", d[\"decision\"][\"answer\"], \"| fallback:\", d[\"fallback\"], \"| reason:\", d[\"decision\"][\"reason\"][:160]); print(\"analyze HTTP\"+code.strip())'"
note "A check from another address still answers:"
run "curl -s -o /dev/null -w 'HTTP %{http_code}\n' -X POST $E/check -H 'Fly-Client-IP: 10.13.0.2' -H '$J' -d '$T2'"
