# Front door: the hands-on round

Brian tested the preview of `front-door` on his phone, at head `0ceabf20`, on 2026-11-10. Each issue below has its cause, when known, and its triage.

Triage: **blocks** means the issue must be fixed before the merge. **follow-up** means the issue becomes its own spec after the merge.

After the triage, each issue that blocks becomes a ticket from 13 up. Then the evidence of all 58 tests is recorded again, and a fresh Judge runs.

| # | Issue | Cause | State | Triage |
| --- | --- | --- | --- | --- |
| H1 | The dock at the foot shows 2 lines of chips, so the Answers have no room. | The AT-4 fix wrapped the chips in every state. The PRD wants one row at the foot. | Fixed: `55eb676f`, merged | blocks |
| H2 | Trade ideas finds no trade for Bo Girds, which has no QB. | `weak_starting_slots` read `lineup_slots`, which fills the best lineup from the whole roster, IR included. Lamar Jackson is on IR, so the QB slot looked full. | Fixed: `f5857f0a` on `front-door-fix-ir` (`lineup_now`). Live: "QB: empty", `/find` gives 95 offers | blocks: ticket 13 |
| H3 | The personal Topics stall at "Reading the rosters…" in the dev server. | In dev, React Strict Mode mounts twice. `useChat` drops the first request, and the guard blocks a resend. The static export works. | Not fixed | follow-up |
| H4 | The Waiver targets Answer has a "Read the full report" link that gives a 404. | CPC has no waiver package, so it has no waiver page. | Fix runs on `front-door-fix-waiver-link` | blocks: ticket 14 |
| H5 | The waiver list holds weak players with bids that make no sense, such as Drew Sample for 13. | Logic in `packages/waiver/`, every week, both clients. Each bid is the last winning claim at the position plus $1. A player with no Sleeper projection counts 0 and ties into the top half. A rise in usage outranks the role. `behind_injury` fires on a backup and skips every check. Old tickets `.scratch/waiver/pipeline/issues/09`, `10`, `11`. | Split, Brian chose | blocks: ticket 15 (2 hard rules, the Answer leans on the trending bucket, no bids). follow-up: a waiver spec for a Jev add judgment and the price |
| H6 | "i want to trade parker washington" streams a text, then ends as the honest miss. | The route score `fits_topic` sits at the 0.7 cutoff (0.68 to 0.75). The check failed advice and opinion sentences, not numbers. The rewrite prompt lets Claude reword, not drop. | Brian chose: route to trade ideas | blocks: ticket 16 (route and eval), ticket 17 (facts only, rewrite drops). follow-up: `/find` around one named player |
| H7 | The Thread folds each older question and Answer into a box. It feels clunky. | Decision 08 and PRD stories 38 and 39 chose the fold. Brian now wants a plain chat: each Answer stays as it rendered, and he scrolls up to reread. | Brian chose: plain chat, content as is | blocks: ticket 18. Spec change: PRD stories 38 and 39, AT-30, AT-31 |
| H8 | On a phone, the keyboard opens and the bottom nav dock covers the ask box. The nav also takes too much room. | The nav dock of the site stays at the foot while the keyboard is open. | Brian reported | blocks: ticket 19 (the nav hides while the ask box has focus, the ask box sits above the keyboard) |
| H9 | The copy says "front door", and the miss runs long. | The refusal line says "not a question the front door answers". The miss line lists what the site lacks. Two prompts tell Claude and Jev they write "on the front door". | Brian: never say front door; if it cannot answer, just say so | blocks: ticket 20 (miss and refusal say "I can't answer that.", prompts drop the phrase) |
| H10 | Text streams, then a different answer replaces it. | Claude's text streams before the Jev check. A failed text gets a rewrite that replaces it. | Brian chose: hold, then reveal | blocks: ticket 21 (step lines only until the check passes, then the word reveal) |
| H11 | "Cant choose mine" after "who has best roster" gives the miss. Each question has no chat context. | Each question goes to the router and to Claude alone. | Brian chose: the whole Thread, made efficient | blocks: ticket 22 (the turns of the Thread, newest last, about 8,000 tokens at most, cached) |

## Follow-ups after the merge

- H3: the dev server stall of `useChat` under Strict Mode.
- The waiver spec: a Jev add judgment, the price from it, a waiver-only rebuild command, and the week 9 republish.
- `/find` around one named player to give.
- `FreeRoutes` keeps a free route for 600 s after a later topic route.
- `due_back_week` gives `None` in the playoffs for an IR player with no returns row.
- The weak spots fact and the trade ideas fact can name different positions for one team.
