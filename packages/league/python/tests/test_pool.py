"""
Tests for the waiver pool rule of ranks.in_pool: the roster slots of the league set the positions of the pool.
The free agents of the snapshot and the waiver board both read the rule.
"""
from league.ranks import in_pool

CPC_POSITIONS = ("QB", "RB", "WR", "TE", "DEF")
KICKER = {"position": "K", "team": "BUF", "status": "Active", "active": True}
DEFENSE = {"position": "DEF", "team": "BUF", "active": True}


def test_a_kicker_is_out_of_the_pool_of_a_league_with_no_k_slot():
    assert not in_pool(KICKER, set(), "1", CPC_POSITIONS)


def test_a_kicker_is_in_the_pool_of_a_league_with_a_k_slot():
    assert in_pool(KICKER, set(), "1", (*CPC_POSITIONS, "K"))


def test_a_defense_is_out_of_the_pool_of_a_league_with_no_def_slot():
    assert in_pool(DEFENSE, set(), "BUF", CPC_POSITIONS)
    assert not in_pool(DEFENSE, set(), "BUF", ("QB", "RB", "WR", "TE"))
