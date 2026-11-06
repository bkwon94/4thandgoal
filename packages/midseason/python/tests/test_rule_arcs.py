"""
The rules of the arcs, on small hand-built leagues: the start and now windows on the full record, a tie as half a
win, the streak arcs on head to head only, the luck arcs, the 2-arc limit, and the order by the size of the swing.
"""
from league.models import History, PastWeek
from midseason.arcs import team_arcs
from midseason.state import league_state

NAMES = {1: "One", 2: "Two", 3: "Three", 4: "Four"}


def _season(results: str, *, other: str | None = None) -> History:
    """Eight or more weeks where team 1 meets team 2 and team 3 meets team 4 each week. `results` gives team 1 a W,
    an L, or a T each week. `other` gives team 3 its results, and by default team 3 wins and loses in turn."""
    other = other or "WL" * (len(results) // 2 + 1)
    weeks = {}
    for number, (one, three) in enumerate(zip(results, other, strict=False), start=1):
        scores = {1: 100.0, 2: 100.0, 3: 100.0, 4: 100.0}
        if one != "T":
            scores[1 if one == "W" else 2] = 110.0
        if three != "T":
            scores[3 if three == "W" else 4] = 105.0
        weeks[number] = PastWeek(week=number, scores=scores, pairs=[(1, 2), (3, 4)], points={}, projections={},
                                 stats={}, moves=[])
    return History(week=len(results), weeks=weeks)


def _arcs(history: History, luck: dict[int, float] | None = None, *, median_game: bool = False):
    through = history.week
    state = league_state(history, through, NAMES, playoff_odds={}, median_game=median_game)
    arcs = team_arcs(history, through, state, luck or {}, median_game=median_game)
    return {team.roster_id: [arc.kind for arc in team.arcs] for team in arcs.teams}, arcs


def test_a_bad_start_and_a_good_now_is_a_turnaround_and_the_reverse_is_a_collapse():
    kinds, _ = _arcs(_season("LWLLWWLW"))
    # Team 1 is 1-3 in weeks 1 to 4 and 3-1 in weeks 5 to 8.
    assert kinds[1] == ["Turnaround"]
    assert kinds[2] == ["Collapse"]


def test_good_in_both_windows_is_wire_to_wire_and_bad_in_both_is_never_got_going():
    kinds, _ = _arcs(_season("WWLWWLWW"))
    assert kinds[1] == ["Wire to wire"]
    assert kinds[2] == ["Never got going"]


def test_a_window_arc_counts_the_median_game_so_it_agrees_with_the_standings():
    # Team 1 scores 120 each week and goes 2-2 head to head in each window. The median is 105, so with the median
    # game team 1 is 6-2 in each window.
    weeks = {}
    for number, won in enumerate("WLWLWLWL", start=1):
        scores = {1: 120.0, 2: 110.0 if won == "W" else 130.0, 3: 90.0, 4: 80.0}
        weeks[number] = PastWeek(week=number, scores=scores, pairs=[(1, 2), (3, 4)], points={}, projections={},
                                 stats={}, moves=[])
    history = History(week=8, weeks=weeks)
    assert _arcs(history, median_game=True)[0][1] == ["Wire to wire"]
    assert _arcs(history, median_game=False)[0][1] == []


def test_a_tie_counts_half_a_win_in_a_window():
    # Team 1 is 2-1-1 in weeks 1 to 4, a rate of 62.5%, so the start is good. A tie as no win would give 50%.
    kinds, _ = _arcs(_season("WTLWLLWL"))
    assert kinds[1] == ["Collapse"]


def test_an_active_head_to_head_win_streak_of_4_is_a_heater_and_3_is_not():
    assert "Heater" in _arcs(_season("LWLWWWWW", other="LWLWLWLW"))[0][1]
    assert "Heater" not in _arcs(_season("LWLWLWWW"))[0][1]


def test_a_tie_ends_a_streak():
    assert "Heater" not in _arcs(_season("WLWLWWTW"))[0][1]


def test_two_head_to_head_streaks_of_3_in_opposite_directions_are_a_roller_coaster():
    kinds, _ = _arcs(_season("WWWLWLLL"))
    assert "Roller coaster" in kinds[1]
    assert "Roller coaster" in kinds[2]
    assert "Roller coaster" not in _arcs(_season("WWWLWLLW"))[0][1]


def test_schedule_luck_of_1_5_or_more_is_smoke_and_mirrors_and_of_minus_1_5_or_less_is_snakebit():
    kinds, _ = _arcs(_season("WLWLWLWL"), {1: 1.5, 2: -1.5, 3: 1.49, 4: -1.49})
    assert kinds[1] == ["Smoke and mirrors"]
    assert kinds[2] == ["Snakebit"]
    assert kinds[3] == [] and kinds[4] == []


def test_a_team_has_at_most_2_arcs_ordered_by_the_size_of_the_swing():
    # Team 1 is 0-4 then 4-0, with an active streak of 4 and two streaks of 4: Turnaround, Roller coaster, Heater.
    kinds, arcs = _arcs(_season("LLLLWWWW"))
    assert len(kinds[1]) == 2
    one = next(team for team in arcs.teams if team.roster_id == 1)
    assert [arc.swing for arc in one.arcs] == sorted((arc.swing for arc in one.arcs), reverse=True)
    # The Turnaround swings from 0% to 100%, and the Roller coaster holds all 8 games in its two streaks.
    assert kinds[1] == ["Turnaround", "Roller coaster"]


def test_each_swing_is_on_a_0_to_1_scale():
    _, arcs = _arcs(_season("LLLLWWWW"), {1: 9.0, 2: -9.0})
    assert all(0 <= arc.swing <= 1 for team in arcs.teams for arc in team.arcs)


def test_a_team_may_have_no_arc():
    kinds, _ = _arcs(_season("WLWLWLWL"))
    assert kinds[3] == [] and kinds[4] == []


def test_each_arc_cites_its_numbers():
    _, arcs = _arcs(_season("LWLLWWLW"), {1: 2.0})
    one = {arc.kind: arc for arc in next(team for team in arcs.teams if team.roster_id == 1).arcs}
    turnaround = one["Turnaround"]
    assert turnaround.start is not None and turnaround.now is not None
    assert (turnaround.start.wins, turnaround.start.losses, turnaround.now.wins, turnaround.now.losses) == (1, 3, 3, 1)
    assert one["Smoke and mirrors"].schedule_luck == 2.0


def test_the_now_window_is_the_last_4_weeks_through_the_week_of_the_report():
    # Through week 10, the now window is weeks 7 to 10.
    _, arcs = _arcs(_season("WWWWLLWWWW"))
    one = next(team for team in arcs.teams if team.roster_id == 1)
    wire = next(arc for arc in one.arcs if arc.kind == "Wire to wire")
    assert wire.now is not None and (wire.now.first_week, wire.now.last_week, wire.now.wins) == (7, 10, 4)
