# 02 — Odds engine

**What to build:** a function that turns the season so far and the remaining schedule into playoff
odds, so a test can feed a small league and read the result. In: the weekly scores per roster, the
real wins, losses, and points for per roster, the remaining pairings per week, the week, the playoff
spots, and the bye count. Out: per roster the playoff odds, the bye odds, the most likely seed or
none, and the status `in`, `out`, or `open`; and per pair of week N+1 the playoff odds of each side
after a head-to-head win and after a loss. No network, no Claude.

The engine is Monte Carlo. Each run draws one of the roster's own weekly scores for each remaining
week, with the last `RECENT_WEEKS` weeks weighted `RECENT_WEIGHT` times, plays the pair game and
the median game with the existing median rule, and sorts the final table by wins, then points for,
then roster id. The random seed derives from the season and the week. The status comes from a
plain check, not from the runs: `in` when no roster outside the top spots can reach the roster's
wins with 2 wins in every remaining week, `out` when the roster cannot reach the last spot's wins
the same way. Odds round to a whole percent and clamp to 1 to 99 for `open`, and show 100 for `in`
and 0 for `out`. The seed shows only at or above `SEED_SHOW_AT`. With no weeks left the engine
skips the runs and the check sets every roster.

Spec: `.scratch/stakes/pipeline/PRD.md`, "The engine". Research: `.scratch/stakes/pipeline/research.md`, facts 2 to 4.

**Blocked by:** None — can start immediately.

**Status:** done

- [x] A new module holds the engine behind one function with the inputs and outputs above.
- [x] Tunables `SIM_RUNS` 5000, `RECENT_WEEKS` 3, `RECENT_WEIGHT` 2, `SEED_SHOW_AT` 50 join the tunable table with a one-line "why" each.
- [x] The same seed gives the same odds twice. The seed derives from the season and the week.
- [x] Both games count: a fixture where only the median game differs gives different odds.
- [x] The seed order is wins, then points for, then roster id, and the bye goes to the top 2.
- [x] The status check: a 4-win lead with 1 week left is `in`; 5 wins back with 2 weeks left is `out`; else `open`.
- [x] `in` shows 100, `out` shows 0, `open` clamps to 1 to 99 after the round.
- [x] The most likely seed is the modal seed over the runs where the roster makes it, and is none below `SEED_SHOW_AT`.
- [x] The swing splits the runs by the week N+1 head-to-head result only, and gives both sides' odds per half.
- [x] With no weeks left the engine returns the check result and the final table, with no runs.
- [x] Tests on a 4-team fixture, 2 weeks played, 2 weeks left, 2 spots, 200 runs, fixed seed. No test pins real week 6 odds.
- [x] The odds of all rosters sum to the spots times 100 within rounding.
- [x] The full run of 12 teams and 8 weeks at 5,000 runs takes under 10 seconds on the fixture.
- [x] Ruff clean, the full suite passes.
