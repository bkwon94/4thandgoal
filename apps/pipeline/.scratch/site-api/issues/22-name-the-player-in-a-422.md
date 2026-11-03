# 22: The 422 names the player and the team

**What to build:** When a proposed trade names a player who is not on the giving roster, the 422 message reads "Ja'Marr Chase is no longer on All You Need Is Love." Today it reads "Player 7564 is not on roster 6". The `player_id` field stays. The site shows the message as it is and refetches the rosters, so no site change is needed.

**Why:** The teams in the form can be up to 10 minutes old between the two caches. A manager who reads the error must know who moved.

**Blocked by:** None.

**Status:** done

- [x] `check_trade` in `src/cornerstone/rubric.py` names the player and the team from the snapshot. A roster that is not in the league keeps its message with the id.
- [x] Tests in `tests/test_rubric.py` and `tests/test_api.py` assert the new text and the `player_id`.
- [x] `uv run pytest -q` passes with no failed test.
- [x] Deployed 2026-10-22.
