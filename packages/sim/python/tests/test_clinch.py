"""
Tests for the Clinch lines of the League board: a small hand-built league at the seam of season_sim, checked against a
brute-force count of every set of results of this week, written here by hand. The real cpc week 11 runs in the pipeline.
"""
from itertools import combinations, product

import pytest

from league.league_settings import LeagueSettings
from sim.season import SetResult, rerun, season_sim

SEASON = 2026
ROSTERS = range(1, 9)
SCORES = {rid: [100.0 + 7 * rid, 120.0 - 5 * rid] for rid in ROSTERS}
# A spread of real wins from 1 to 8 after 2 weeks with the median game, so some teams can clinch or go out this week.
WIDE = {rid: (rid, 8 - rid, 220.0 + rid, 200.0 + rid) for rid in ROSTERS}
REMAINING = {3: [(1, 2), (3, 4), (5, 6), (7, 8)], 4: [(1, 3), (2, 4), (5, 7), (6, 8)]}
GOALS = {"spot": 4, "bye": 2}


def _settings(*, median_game: bool) -> LeagueSettings:
    return LeagueSettings(
        team_count=len(ROSTERS), playoff_spots=4, bye_count=2, star_rank_by_position={}, roster_slots=("QB",),
        last_regular_week=4, reception_points=0.5, median_game=median_game, reseed=True,
    )


def _sim(median_game: bool, **kwargs):
    return season_sim(SCORES, WIDE, REMAINING, season=SEASON, week=2, settings=_settings(median_game=median_game),
                      runs=2_000, pages=list(ROSTERS), **kwargs)


def _hand_status(rid: int, wins: dict[int, int], reach: int, k: int) -> str:
    """The plain check on wins for the top k places, by hand."""
    others = [o for o in wins if o != rid]
    if sum(wins[o] + reach >= wins[rid] for o in others) < k:
        return "in"
    if sum(wins[o] > wins[rid] + reach for o in others) >= k:
        return "out"
    return "open"


def _every_set(median_game: bool):
    """Each set of results of the first week left: the winner of each game and the teams above the median. A game
    winner always outscores its loser, so a loser above the median needs its winner above it too."""
    pairs = REMAINING[3]
    aboves = [frozenset(c) for c in combinations(ROSTERS, len(ROSTERS) // 2)] if median_game else [frozenset()]
    for winners in product(*pairs):
        losers = [b if w == a else a for (a, b), w in zip(pairs, winners, strict=True)]
        for above in aboves:
            if any(loser in above and winner not in above for winner, loser in zip(winners, losers, strict=True)):
                continue
            yield frozenset(winners), above


def _fits(way: dict, rid: int, winners: frozenset, above: frozenset) -> bool:
    if way["game"] is not None and (rid in winners) != (way["game"] == "win"):
        return False
    if way["median"] is not None and (rid in above) != (way["median"] == "above"):
        return False
    for other in way["others"]:
        if other["kind"] == "game" and other["winner"] not in winners:
            return False
        if other["kind"] == "median" and (other["roster_id"] in above) != (other["median"] == "above"):
            return False
    return True


@pytest.mark.parametrize("median_game", [True, False])
def test_the_clinch_lines_agree_with_a_brute_force_count_of_every_set_of_results(median_game):
    sim = _sim(median_game, clinch=True)
    per_week = 2 if median_game else 1
    reach_now, reach_after = per_week * 2, per_week
    now = {rid: WIDE[rid][0] for rid in ROSTERS}
    sets = list(_every_set(median_game))
    # 4 games give 16 sets of winners. With the median game, 19 splits of the 4 teams above the line fit each one.
    assert len(sets) == (16 * 19 if median_game else 16)
    lines_seen = 0
    for row in sim.board:
        rid = row.roster_id
        lines = {(line.goal, line.status): line.model_dump(mode="json") for line in row.clinch}
        for goal, k in GOALS.items():
            for status in ("in", "out"):
                hits = []
                for winners, above in sets:
                    after = {r: now[r] + (r in winners) + (r in above) for r in ROSTERS}
                    if _hand_status(rid, after, reach_after, k) == status:
                        hits.append((winners, above))
                line = lines.get((goal, status))
                if _hand_status(rid, now, reach_now, k) != "open":
                    assert line is None, (rid, goal, status)
                    continue
                assert (line is not None) == bool(hits), (rid, goal, status)
                if line is None:
                    continue
                lines_seen += 1
                hit_keys = set(hits)
                for way in line["ways"]:
                    fitting = [s for s in sets if _fits(way, rid, *s)]
                    assert fitting and set(fitting) <= hit_keys, (rid, goal, status, way)
                # The ways together list every set that clinches or ends the Goal.
                assert all(any(_fits(way, rid, *s) for way in line["ways"]) for s in hits), (rid, goal, status)
                chances = [way["chance"] for way in line["ways"]]
                assert chances == sorted(chances, reverse=True)
    assert lines_seen > 0


def test_a_sim_with_no_clinch_asked_and_a_what_if_hold_no_clinch_line():
    sim = _sim(True, clinch=True)
    assert any(row.clinch for row in sim.board)
    assert all(not row.clinch for row in _sim(True).board)
    after = rerun(sim, you=4, set_results=[SetResult(week=3, game="win", median="above")], pages=[4])
    assert all(not row.clinch for row in after.board)
