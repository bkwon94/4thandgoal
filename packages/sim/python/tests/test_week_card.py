"""
Tests for the week card of The Race: the four results of the next week, the root-for list of every other game for each
result, the median rooting, and the tiebreak gap, on the small hand-built league of test_paths.py.
"""
import pytest

from league.league_settings import LeagueSettings
from sim.season import SetResult, season_sim

SEASON = 2026
ROSTERS = range(1, 9)
# A league in its regular season: 2 weeks played, 2 weeks left, as in test_paths.py.
SCORES = {rid: [100.0 + 7 * rid, 120.0 - 5 * rid] for rid in ROSTERS}
RECORDS = {rid: (2 + rid % 3, 2 - rid % 3, 220.0 + rid, 200.0 + rid) for rid in ROSTERS}
REMAINING = {3: [(1, 2), (3, 4), (5, 6), (7, 8)], 4: [(1, 3), (2, 4), (5, 7), (6, 8)]}


def _settings(*, median_game: bool) -> LeagueSettings:
    return LeagueSettings(
        team_count=len(ROSTERS), playoff_spots=4, bye_count=2, star_rank_by_position={}, roster_slots=("QB",),
        last_regular_week=4, reception_points=0.5, median_game=median_game, reseed=True,
    )


def _sim(median_game: bool = True, runs: int = 6_000, records=RECORDS, **what_if):
    return season_sim(SCORES, records, REMAINING, season=SEASON, week=2, settings=_settings(median_game=median_game),
                      runs=runs, pages=what_if.pop("pages", list(ROSTERS)), **what_if)


@pytest.fixture(scope="module")
def sim():
    return _sim()


def _card(page):
    assert page.week_card is not None
    return page.week_card


def _open(page, key):
    return page.goals[key].status == "open"


def test_the_week_card_holds_the_next_week_with_four_results_and_the_odds_of_each_goal(sim):
    for rid, page in sim.pages.items():
        card = page.week_card
        assert card is not None
        assert card.week == 3
        assert card.opponent == next(b if a == rid else a for a, b in REMAINING[3] if rid in (a, b))
        assert [(r.game, r.median) for r in card.results] == [
            ("win", "above"), ("win", "below"), ("loss", "above"), ("loss", "below")]
        assert sum(r.chance for r in card.results) == pytest.approx(100, abs=1)
        assert set(card.goals) == set(page.goals)
        assert all(len(goal.odds) == 4 for goal in card.goals.values())


def test_the_spot_tiles_agree_with_the_results_of_the_page_week(sim):
    for page in sim.pages.values():
        old = page.weeks[0].results
        assert _card(page).goals["spot"].odds == [r.playoff for r in old]
        assert [r.chance for r in _card(page).results] == [r.chance for r in old]


def test_each_result_roots_for_every_other_game_with_both_odds_on_an_open_spot_or_bye(sim):
    flat = 0
    for rid, page in sim.pages.items():
        others = {frozenset(pair) for pair in REMAINING[3] if rid not in pair}
        for key, goal in _card(page).goals.items():
            if key.startswith("seed-") or not _open(page, key):
                # A seed and a settled Goal hold the tiles only, to keep sim.json small.
                assert goal.root_for == [] and goal.median_root == []
                continue
            assert len(goal.root_for) == 4
            for rows in goal.root_for:
                assert {frozenset((row.winner, row.loser)) for row in rows} == others
                assert all(row.odds >= row.other for row in rows)
                lifts = [row.odds - row.other for row in rows]
                assert lifts == sorted(lifts, reverse=True)
                flat += sum(lift < 1 for lift in lifts)
    assert flat


def test_the_median_rooting_names_1_or_2_other_teams_and_the_second_lifts_by_a_point(sim):
    for rid, page in sim.pages.items():
        for key in ("spot", "bye"):
            goal = _card(page).goals[key]
            if not _open(page, key):
                continue
            for value, rows in zip(goal.odds, goal.median_root, strict=True):
                assert 1 <= len(rows) <= 2
                assert rid not in {row.roster_id for row in rows}
                if len(rows) == 2:
                    assert rows[1].odds - value >= 1


def test_a_league_with_no_median_game_has_two_tiles_and_no_median_rooting():
    plain = _sim(median_game=False, runs=2_000)
    for page in plain.pages.values():
        assert [(r.game, r.median) for r in _card(page).results] == [("win", None), ("loss", None)]
        assert all(goal.median_root == [] for goal in _card(page).goals.values())


def test_a_what_if_of_the_week_keeps_the_odds_of_the_set_result_only():
    held = _sim(runs=2_000, you=1, pages=[1], set_results=[SetResult(week=3, game="loss", median="below")])
    card = _card(held.pages[1])
    assert [r.chance for r in card.results] == [0.0, 0.0, 0.0, 100.0]
    spot = card.goals["spot"]
    assert spot.odds[:3] == [None, None, None] and spot.odds[3] == held.pages[1].playoff
    assert spot.root_for[:3] == [[], [], []] and len(spot.root_for[3]) == 3


def test_the_tiebreak_gap_shows_only_for_a_close_team_across_the_edge_of_the_goal():
    # Roster 4 holds the last spot at 3-1 with 300 points. Roster 5 sits just out at 2-2 with 280 points, so it is
    # within 1 win and 50 points. Roster 6 is out at 2-2 but 60 points behind.
    records = {1: (4, 0, 400.0, 200.0), 2: (4, 0, 390.0, 200.0), 3: (3, 1, 350.0, 200.0), 4: (3, 1, 300.0, 200.0),
               5: (2, 2, 280.0, 200.0), 6: (2, 2, 240.0, 200.0), 7: (0, 4, 200.0, 200.0), 8: (0, 4, 190.0, 200.0)}
    close = _sim(runs=2_000, records=records)
    spot = {rid: _card(page).goals["spot"] for rid, page in close.pages.items()}
    assert spot[4].tiebreak is not None and spot[4].tiebreak.roster_id == 5 and spot[4].tiebreak.points == 20.0
    assert spot[5].tiebreak is not None and spot[5].tiebreak.roster_id == 4 and spot[5].tiebreak.points == -20.0
    assert spot[6].tiebreak is None
    assert spot[7].tiebreak is None
