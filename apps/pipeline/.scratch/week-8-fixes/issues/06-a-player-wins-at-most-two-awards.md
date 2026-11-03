# 06: A player wins at most two awards

Spec: `.scratch/week-8-fixes/PRD.md`, part 2. Brian's decision on 2026-11-03: "cap of two is fine".

**What to build:** Ticket 02 let each award pick its own winner, and Joe Burrow took three tiles in week 8:
Game Changer, Top Scorer, and Overachiever. A player now wins at most two. Once a player holds two awards, the
later awards skip him and take the next player. The awards keep their pick order.

**Blocked by:** none.

**Status:** done

- [x] Find the pick order of the awards in `awards()` of `src/cornerstone/facts_league.py` and the expected awards in `facts_nflverse.py`. Name the order in the close comment.
- [x] A player with two awards is skipped by every later award. The cap is one tunable `AWARDS_PER_PLAYER = 2` in `tunables.py`, with a comment that says why two: a reader expects the top scorer to be the top scorer, and three tiles for one player reads as a bug.
- [x] A test shows a player who leads three awards wins the first two and the third goes to the next player.
- [x] A test shows a player who leads two awards wins both.
- [x] The week 8 awards from the saved raw data: Burrow holds Game Changer and Top Scorer, and Overachiever goes to the next player. Name him in the close comment.
- [x] `make golden` ran, and the golden diff is named in the close comment.
- [x] `make check` passes.

## Comments

- 2026-11-03: merged into `main` from branch `week-8-fixes-06-cap`, commits b1c5913, 79d4255, and 109067d, with `--no-ff`. 1529 passed, 9 deselected. Pick order: Game Changer, Top Scorer, MVB, Underperformer, Overachiever in `awards()`, then Unlucky and Lucky in `expected_awards()`, which takes the map of awards held so the cap reaches them. `AWARDS_PER_PLAYER = 2` in `tunables.py`. No golden change: no week 6 player leads three awards. Week 8 from the saved data: Burrow holds Game Changer and Top Scorer, and Overachiever goes to Tee Higgins, 32.5 on a 13.67 projection. Two reviewers passed it after one fix pass. The ticket 02 close comment was enough to skip the READMEs. Read 15 files: CLAUDE.md, docs/agents/state.md, the ticket, ticket 02, src/cornerstone/README.md, sheet/README.md, facts_league.py, facts_nflverse.py, tunables.py, sheet/awards.py, models.py, tests/test_facts_league.py, tests/test_facts_nflverse.py, Makefile, tests/test_layers.py.
