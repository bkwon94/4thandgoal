"""
The rules of the lineup choices, on a small hand-built league: Bench points are the best lineup's points minus the
real score, a flex slot takes the best player left, and a loss counts when the best lineup beats the opponent.
"""
from league.models import History, PastWeek
from midseason.lineups import lineup_choices

SLOTS = ["QB", "RB", "FLEX"]
NAMES = {1: "One", 2: "Two"}
POSITIONS = {"q1": "QB", "r1": "RB", "r2": "RB", "w1": "WR", "q2": "QB", "r3": "RB", "w2": "WR"}


def _week(number: int, points: dict[str, float], starters: dict[int, list[str]]) -> PastWeek:
    rosters = {1: ["q1", "r1", "r2", "w1"], 2: ["q2", "r3", "w2"]}
    scores = {rid: sum(points[pid] for pid in starters[rid]) for rid in rosters}
    return PastWeek(week=number, scores=scores, pairs=[(1, 2)], points=points, projections={}, stats={}, moves=[],
                    starters=starters, rosters=rosters)


HISTORY = History(week=2, weeks={
    # One starts r2 and w1 over r1: 10 + 5 + 4 = 19 against 20, but q1, r1, and w1 make 10 + 12 + 5 = 27.
    1: _week(1, {"q1": 10, "r1": 12, "r2": 4, "w1": 5, "q2": 8, "r3": 6, "w2": 6},
             {1: ["q1", "r2", "w1"], 2: ["q2", "r3", "w2"]}),
    # One starts its best lineup and wins, so the week has no Bench points.
    2: _week(2, {"q1": 10, "r1": 12, "r2": 4, "w1": 5, "q2": 8, "r3": 6, "w2": 6},
             {1: ["q1", "r1", "w1"], 2: ["q2", "r3", "w2"]}),
})


def _teams():
    # The history holds no positions, so the positions of the players file stand in.
    return {team.roster_id: team for team in lineup_choices(HISTORY, 2, NAMES, SLOTS, POSITIONS).teams}


def test_bench_points_are_the_best_lineup_minus_the_real_score_over_the_season():
    teams = _teams()
    assert teams[1].bench_points == 8
    assert teams[2].bench_points == 0
    assert [team.rank for team in lineup_choices(HISTORY, 2, NAMES, SLOTS, POSITIONS).teams] == [1, 2]


def test_a_loss_that_the_best_lineup_would_have_won_is_listed_with_its_margin():
    week = _teams()[1].lost_with_better
    assert len(week) == 1
    assert (week[0].week, week[0].score, week[0].best, week[0].bench_points, week[0].margin, week[0].opponent) == (
        1, 19, 27, 8, 1, "Two")
    assert _teams()[2].lost_with_better == []
