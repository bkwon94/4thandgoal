# 08: The live next matchup card and its win odds

Spec: `.scratch/front-door-lineup/PRD.md`. Acceptance tests AT-25.

**App:** both

**What to build:** The API builds the matchup card of Your next matchup live from the Sleeper projections of the week and sends it on the stream of the Topic. The win odds come from the gap of the two projected totals, with the league `spread` of `sim.json` as the noise. The rest of the Topic still comes from `topics.json`.

**Blocked by:** 06

**Status:** done

- [x] The stream of Your next matchup carries a matchup card with the projected totals of the live week and a read time within the minute of the request (AT-25).
- [x] The team with the higher projected total has odds above 50% (AT-25).
- [x] A pytest shows that a starter on a bye lowers the projected total and the odds.
- [ ] Site screenshots show the live card.

## Comments
- Closes with the squash merge of the spec PR.
