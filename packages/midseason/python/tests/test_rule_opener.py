"""
The rules of the opener, the title race, on a small hand-built league: the leaders by title odds, the record leader
with its title odds, and the facts that name them.
"""
from league.models import History, PastWeek
from midseason.opener import LEADERS, title_race, title_race_facts
from midseason.state import league_state


def _week(number: int, scores: dict[int, float], pairs: list[tuple[int, int]]) -> PastWeek:
    return PastWeek(week=number, scores=scores, pairs=pairs, points={}, projections={}, stats={}, moves=[])


# Five teams over one week with no median game. Team 1 leads the standings, team 5 has a bye.
HISTORY = History(week=1, weeks={1: _week(1, {1: 100.0, 2: 90.0, 3: 80.0, 4: 70.0, 5: 60.0}, [(1, 2), (3, 4)])})
NAMES = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five"}
STATE = league_state(HISTORY, 1, NAMES, playoff_odds={}, median_game=False)
# The record leader has low title odds, and team 4 has the best.
TITLE_ODDS = {1: 12.5, 2: 20.0, 3: 30.0, 4: 31.5, 5: 6.0}


def test_the_leaders_are_the_teams_with_the_best_title_odds_best_first():
    race = title_race(STATE, TITLE_ODDS)
    assert LEADERS == 3
    assert [(leader.roster_id, leader.title_odds) for leader in race.leaders] == [(4, 31.5), (3, 30.0), (2, 20.0)]


def test_the_record_leader_is_first_in_the_standings_with_its_record_and_its_title_odds():
    leader = title_race(STATE, TITLE_ODDS).record_leader
    assert (leader.roster_id, leader.name, leader.wins, leader.losses, leader.title_odds) == (1, "One", 1, 0, 12.5)
    assert leader.title_rank == 4


def test_with_no_title_odds_the_race_has_no_leaders_and_the_record_leader_has_no_odds():
    race = title_race(STATE, {})
    assert race.leaders == []
    assert race.record_leader.title_odds is None and race.record_leader.title_rank is None


def test_the_facts_name_each_leader_s_title_odds_and_the_record_leader_s():
    facts = {f.id: f for f in title_race_facts(title_race(STATE, TITLE_ODDS))}
    assert facts["OP.4.title"].text == "Four has 31.5% title odds, the best in the league."
    assert facts["OP.3.title"].text == "Three has 30% title odds, 2nd best in the league."
    assert facts["OP.record"].text == "One leads the standings at 1-0 and has 12.5% title odds, 4th best in the league."
