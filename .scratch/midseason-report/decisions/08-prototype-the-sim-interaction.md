# 08: Does the sim replay prebuilt runs, or does the reader pick winners live?

Map: `.scratch/midseason-report/MAP.md`.

**Kind:** prototype

**Blocked by:** 07

**Status:** done

## Question

Brian wants a "sim rest of season" feature that blows a manager away. There are two options. A replay shows one stored run per press, with the odds from all runs. A live sim lets the reader pick the winner of future games and runs again in the browser. Brian must see both before the decision. Build both as throwaway boards in the redesign look, then delete the code.

## Decision

Brian decided it on 2026-11-05, after three variants on real CPC week 8 data: a replay, a live picker, and a seed heat map with picks.

- The sim chapter is a replay. Each press plays one stored run from the sample of 200. The odds of all 10,000 runs sit beside it. The reader cannot change a result.
- The live picker is out. Brian found a pick confusing, like a pick for your own team. The heat map with picks is out for the same reason.
- The replay keeps the playoffs, weeks 15 to 17, and ends on a champion. The title odds are the best story in the data.
- The split from the regular season to the playoffs must be clear. The week strip has two labeled groups: the regular season, weeks 9 to 14, and the playoffs, weeks 15 to 17. After week 14 the standings freeze as the final standings, with the cut and the two bye seeds marked. The bracket plays by round: Round 1, the semifinal, and the final.
- The motion of each beat is new fog: ticket 13.

What the prototype also showed:

- The Python model with the bracket matches the published week 8 playoff odds within about 1 point.
- The CPC title race is wide open: six teams at 13% to 17%. The team with the most mean wins has 9.7% title odds, because of the projections of weeks 15 to 17.
- The week 8 `bracket.json` of CPC agrees with the reseed: seed 1 meets the lowest seed left.
- `projected_totals` must run to week 17 for the playoff draw. The NFL schedule cache `games.csv` is gitignored, so a build in a fresh worktree needs it.

