# packages/midseason/site/act-one: the chapters of Act I, "How we got here"

## Knows

- The state of the league: the full record, points for and against, the streak, and the playoff odds of each team.
- On a phone, the state and the luck tables scroll inside their cards, and the team column stays in place.
- The arcs of each team with the numbers behind each arc.
- Schedule luck with the one sentence on the All-play record, the Schedule swap grid, and the best schedule missed.
- Position top 10: one position at a time with a switch, opening on RB, and the "Free agent" tag.

## Ports

- `report/chapter-part.tsx` picks each part by the key of its chapter.

## Does not do

- It computes no fact, no arc, and no luck. The pipeline writes them into the midseason file.
- It reads no file, no env, and no config (ADR 0012).
