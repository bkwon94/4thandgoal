# 03: The Season rank and the Recent rank

Spec: `.scratch/grade-clarity/PRD.md`. Acceptance tests AT-6, AT-7, AT-8, and AT-31.

**App:** both

**What to build:** Each player in a grade shows his Season rank, such as WR60, as Sleeper sorts it. A Recent rank shows beside it, with its label, only when the two differ by 12 spots or more. No text says "takes RB1" or "sits on the bench". The finder facts use the same ranks.

**Blocked by:** 02.

**Status:** in-review

- [x] `RECENT_RANK_GAP = 12` is in the analyzer tunables.
- [x] Each player of `trade.sides` carries `season_rank`, and `recent_rank` when the gap holds, else null.
- [x] In a real `2026` week 9 grade, Cooper (`13276`) has `season_rank` WR60 and `recent_rank` WR18.
- [x] The facts of a traded player give the Season rank, and the Recent rank with its label when the gap holds. They give no Position rank number.
- [x] The slot fact is gone from the fact sheet of the grade and of the finder.
- [x] The side card shows the Season rank of each player, and the Recent rank only when it is present.
- [x] `make check-fast` passes at the root.

## Comments

- The Recent rank reads the games a player played in the last 4 weeks, with no due-back step. This gives Cooper WR18, as the research of decision 01 gives. The Position rank by the 4-week measure gives WR16, because the due-back step ranks some receivers out now by their projection ahead. `GLOSSARY.md`, "Recent rank", now says "the last 4 weeks", not "his last 4 games": over his last 4 games, Cooper scores 10.70 a game, not 13.10.
- A player with no game in the last 4 weeks has no Recent rank.
- The finder document carries the ranks too, because the API test holds the finder sides to the shape of the analyze sides. The swap card and the finder cards show no rank. Only the side card shows the ranks.
- `DOCUMENT_VERSION` goes to 13.
- The Season rank is null when the stats of the season are not complete, and the card then shows no rank line.
- The merge: `bb8b441` into `grade-clarity` on 2026-11-05. `make check BASE=main` passed.
