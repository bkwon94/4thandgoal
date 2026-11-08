#!/bin/bash
# AT-19: grep the repo and the built CPC site for each page, target, and reason of the test egg file.
# Usage: at19-grep.sh <test egg file> <built site dir>
source "$(dirname "$0")/lib.sh"
FILE=$1; SITE=$2; ROOT=/Users/brian.kwon/repos/cpcfantasyfootball/.claude/worktrees/easter-eggs
mkdir -p $EV/AT-19; OUT=$EV/AT-19/output.txt; : > $OUT
note "The test egg file sits outside the repo. Its four eggs T1 to T4, with each reason:"
run "cat $FILE"
note "Each reason, in the tracked files of the repo and in the built site. The evidence folder of this test is left out, because it quotes the file."
python3 -c "import tomllib,sys; [print(e['reason']) for e in tomllib.load(open(sys.argv[1],'rb'))['eggs']]" $FILE | while read -r reason; do
  run "git -C $ROOT grep -c -F \"$reason\" -- ':!.scratch/easter-eggs/evidence' | wc -l | sed 's/^ */repo files: /'; grep -r -l -F \"$reason\" $SITE | wc -l | sed 's/^ */built site files: /'"
done
note "Each target. A target is the stable id that the site gives every element of its kind, so a hit is the id of the element and no egg mark."
for t in luck-3 number-median sim-trophy number-closest; do
  run "grep -r -o -h \"data-stable-id=\\\"$t\\\"\" $SITE | wc -l | sed 's/^ */built site elements with this id: /'; grep -r -o -h 'data-stable-id=\"[^\"]*\"' $SITE | sort -u | wc -l | sed 's/^ */distinct stable ids in the built site: /'"
done
note "Where each target name is in the source of the repo: the code that makes the stable id of every element of the kind, and the tests of the eggs, never an egg list."
run "git -C $ROOT grep -n -E 'stableId\\(\"(luck|number|sim-trophy)' -- apps packages | cut -c1-160"
run "git -C $ROOT grep -l -E 'luck-3|number-median|sim-trophy|number-closest' -- ':!.scratch' ':!clients' | sort"
note "Each page. A page is a route of the site, so each is a built page of every client of the package and no egg mark."
run "ls -d $SITE/midseason/2026 $SITE/2026/week-08"
note "A search of the built site for the conditions and the action of the test eggs, which only an egg holds. A grade on a manager page also has the key letter, so the search leaves the key letter out."
run "grep -r -l -E '\"conditions\":|\"sim_champion\":12|23:00-00:00|\"action\":\"tap2\"' $SITE | wc -l | sed 's/^ */built site files: /'"
