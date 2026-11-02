"""
Tests for the season so far of a manager entry: the points per week, the bench points, and the awards shelf.
Each test builds a small history in the test, so the known best lineup and the known awards are plain to read.
"""
import json

from cornerstone.manager_season import saved_awards
from cornerstone.managers import managers
from cornerstone.models import History, PastWeek, Team
from cornerstone.season_inputs import SeasonInputs

# One QB, two RB, two WR, and a FLEX start. The bench slots do not start.
SLOTS = ["QB", "RB", "WR", "FLEX", "BN", "BN"]
POSITIONS = {"q1": "QB", "r1": "RB", "r2": "RB", "w1": "WR", "w2": "WR"}
PLAYERS = {
    "q1": {"full_name": "Joe Burrow"}, "r1": {"full_name": "Bijan Robinson"},
    "r2": {"full_name": "Kyren Williams"}, "w1": {"full_name": "Puka Nacua"},
}


def _teams() -> dict[int, Team]:
    return {
        rid: Team(
            roster_id=rid, name=f"Team {rid}", owner=f"Owner {rid}", avatar_url=None,
            wins=0, losses=0, points_for=0.0, is_owner=False,
        )
        for rid in range(1, 13)
    }


def _week(number: int, points: dict[str, float], starters: list[str], score: float = 40.0) -> PastWeek:
    """A week of twelve rosters. Roster 1 holds the five players and plays roster 2. Every other score is set."""
    scores = {rid: 50.0 + rid for rid in range(2, 13)}
    scores[1] = score
    return PastWeek(
        week=number, scores=scores, pairs=[(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12)],
        points=points, projections={}, stats={}, moves=[], positions=POSITIONS,
        starters={1: starters}, rosters={1: list(POSITIONS)},
    )


def _entry(history: History, **season):
    return next(e for e in managers(SeasonInputs(history=history), _teams(), **season) if e.roster_id == 1)


def test_a_week_with_a_known_best_lineup_counts_the_bench_points():
    # The best FLEX is r2 with 12.0, but w2 with 3.0 started there, so the bench cost 9.0.
    points = {"q1": 20.0, "r1": 15.0, "r2": 12.0, "w1": 10.0, "w2": 3.0}
    history = History(week=1, weeks={1: _week(1, points, ["q1", "r1", "w1", "w2"])})
    entry = _entry(history, roster_slots=SLOTS, players=PLAYERS)
    assert entry.bench.model_dump() == {
        "total": 9.0, "worst": {"week": 1, "points": 9.0, "player_id": "r2", "name": "Kyren Williams"},
    }


def test_a_week_with_no_bench_gain_has_no_worst_week():
    points = {"q1": 20.0, "r1": 15.0, "r2": 2.0, "w1": 10.0, "w2": 3.0}
    history = History(week=1, weeks={1: _week(1, points, ["q1", "r1", "w1", "w2"])})
    entry = _entry(history, roster_slots=SLOTS, players=PLAYERS)
    assert entry.bench.model_dump() == {"total": 0.0, "worst": None}


def test_the_worst_week_is_the_week_the_bench_cost_most_and_a_missing_name_is_the_id():
    week_1 = _week(1, {"q1": 20.0, "r1": 15.0, "r2": 5.0, "w1": 10.0, "w2": 3.0}, ["q1", "r1", "w1", "w2"])
    # In week 2, w2 sat on the bench with 14.0 while r2 started the FLEX with 1.0.
    week_2 = _week(2, {"q1": 20.0, "r1": 15.0, "r2": 1.0, "w1": 10.0, "w2": 14.0}, ["q1", "r1", "w1", "r2"])
    history = History(week=2, weeks={1: week_1, 2: week_2})
    entry = _entry(history, roster_slots=SLOTS, players=PLAYERS)
    assert entry.bench.model_dump() == {
        "total": 15.0, "worst": {"week": 2, "points": 13.0, "player_id": "w2", "name": "w2"},
    }


def test_each_week_carries_the_points_the_median_and_the_head_to_head_result():
    points = {"q1": 20.0, "r1": 15.0, "r2": 12.0, "w1": 10.0, "w2": 3.0}
    week_1 = _week(1, points, ["q1", "r1", "w1", "w2"], score=40.0)
    week_2 = _week(2, points, ["q1", "r1", "w1", "w2"], score=99.5)
    entry = _entry(History(week=2, weeks={1: week_1, 2: week_2}))
    # The sorted scores put 57.0 and 56.0 at 6th and 7th in week 1, and 58.0 and 57.0 in week 2.
    assert [w.model_dump() for w in entry.weeks] == [
        {"week": 1, "points": 40.0, "median": 56.5, "won": False},
        {"week": 2, "points": 99.5, "median": 57.5, "won": True},
    ]


def test_the_history_and_the_teams_alone_give_no_bench_and_zero_awards():
    points = {"q1": 20.0, "r1": 15.0, "r2": 12.0, "w1": 10.0, "w2": 3.0}
    entry = _entry(History(week=1, weeks={1: _week(1, points, ["q1", "r1", "w1", "w2"])}))
    assert entry.bench is None
    assert len(entry.weeks) == 1
    assert entry.awards.model_dump() == {"top_scorer": 0, "mvb": 0, "game_changer": 0, "underperformer": 0}


def test_a_season_with_no_awards_counts_zero(tmp_path):
    points = {"q1": 20.0, "r1": 15.0, "r2": 12.0, "w1": 10.0, "w2": 3.0}
    history = History(week=1, weeks={1: _week(1, points, ["q1", "r1", "w1", "w2"])})
    # Week 1 had no report, so no facts file exists.
    entry = _entry(history, week_awards=saved_awards({1: tmp_path / "week-01" / "facts.json"}))
    assert entry.awards.model_dump() == {"top_scorer": 0, "mvb": 0, "game_changer": 0, "underperformer": 0}


def test_the_awards_count_from_the_saved_facts_of_two_weeks(tmp_path):
    def facts(name: str, awards: list[tuple[str, int]]):
        path = tmp_path / name / "facts.json"
        path.parent.mkdir()
        body = {"data": {"awards": [{"key": key, "roster_id": rid} for key, rid in awards]}}
        path.write_text(json.dumps(body), encoding="utf-8")
        return path

    week_1 = facts("week-01", [("top_scorer", 1), ("mvb", 2), ("game_changer", 1), ("overachiever", 1)])
    week_2 = facts("week-02", [("top_scorer", 1), ("underperformer", 3)])
    points = {"q1": 20.0, "r1": 15.0, "r2": 12.0, "w1": 10.0, "w2": 3.0}
    weeks = {n: _week(n, points, ["q1", "r1", "w1", "w2"]) for n in (1, 2)}
    inputs = SeasonInputs(history=History(week=2, weeks=weeks))
    entries = managers(inputs, _teams(), week_awards=saved_awards({1: week_1, 2: week_2}))
    by_roster = {e.roster_id: e.awards.model_dump() for e in entries}
    assert by_roster[1] == {"top_scorer": 2, "mvb": 0, "game_changer": 1, "underperformer": 0}
    assert by_roster[2] == {"top_scorer": 0, "mvb": 1, "game_changer": 0, "underperformer": 0}
    assert by_roster[3] == {"top_scorer": 0, "mvb": 0, "game_changer": 0, "underperformer": 1}
