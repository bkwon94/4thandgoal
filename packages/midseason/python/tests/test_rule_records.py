"""
The rules of the record book and the seven awards, on a small hand-built league: the high and the low, the closest
loss and the biggest margin as Heartbreak and Beatdown, the MVP by Points over the line, and the count of moves.
"""
from league.models import History, PastWeek
from league.provider.raw import RawTransaction
from midseason.lineups import LineupChoices, LostWeek, TeamLineup
from midseason.players import PlayerCard
from midseason.records import record_book
from midseason.state import league_state
from midseason.waivers import Streamer, WaiverFacts

NAMES = {1: "One", 2: "Two", 3: "Three", 4: "Four"}
LINES = {"RB": 2}
PLAYERS = {f"p{rid}": PlayerCard(player_id=f"p{rid}", name=f"Back {rid}", position="RB") for rid in NAMES}


def _week(number: int, scores: dict[int, float], pairs: list[tuple[int, int]]) -> PastWeek:
    # Each team starts one back, who scores the team's points.
    return PastWeek(week=number, scores=scores, pairs=pairs, points={f"p{rid}": s for rid, s in scores.items()},
                    projections={}, stats={}, moves=[], positions={f"p{rid}": "RB" for rid in scores},
                    starters={rid: [f"p{rid}"] for rid in scores}, rosters={rid: [f"p{rid}"] for rid in scores})


HISTORY = History(week=2, weeks={
    # The line is the 2nd back, 100. Back 3 scores 50 over it.
    1: _week(1, {1: 100.0, 2: 99.5, 3: 150.0, 4: 60.0}, [(1, 2), (3, 4)]),
    # The line is 80. Back 3 scores 10.2 over it. Two and Four tie, so the tie is no loss and no margin.
    2: _week(2, {1: 80.0, 2: 70.0, 3: 90.2, 4: 70.0}, [(1, 3), (2, 4)]),
})


def _move(kind: str, roster_ids: list[int], *, status: str = "complete", leg: int = 1) -> RawTransaction:
    adds = {f"x{len(roster_ids)}{roster_ids[0]}{kind}": roster_ids[0]} if kind != "trade" else {}
    return RawTransaction.model_validate({
        "transaction_id": f"{kind}-{roster_ids}-{status}", "type": kind, "status": status, "leg": leg, "created": 0,
        "roster_ids": roster_ids, "adds": adds or None, "drops": None})


TRANSACTIONS = {1: [_move("waiver", [1]), _move("free_agent", [1]), _move("trade", [1, 2]), _move("free_agent", [2]),
                    _move("waiver", [3], status="failed")]}
LINEUPS = LineupChoices(teams=[
    TeamLineup(roster_id=1, name="One", rank=1, bench_points=30.0, lost_with_better=[
        LostWeek(week=2, opponent_roster_id=3, opponent="Three", score=80.0, best=95.0, bench_points=15.0,
                 margin=10.2)]),
    TeamLineup(roster_id=2, name="Two", rank=2, bench_points=20.0, lost_with_better=[
        LostWeek(week=1, opponent_roster_id=1, opponent="One", score=99.5, best=120.0, bench_points=20.5,
                 margin=0.5)]),
])
WAIVERS = WaiverFacts(hits=[], misses=[], outbid=[], streamers=[
    Streamer(roster_id=4, team="Four", players=2, starts=2, points=30.0)])


def _book():
    state = league_state(HISTORY, 2, NAMES, playoff_odds={})
    return record_book(HISTORY, 2, NAMES, players=PLAYERS, lines=LINES, transactions=TRANSACTIONS, waivers=WAIVERS,
                       lineups=LINEUPS, state=state)


def _awards():
    return {award.key: award for award in _book().awards}


def test_the_high_and_the_low_are_single_team_scores_of_the_season():
    book = _book()
    assert (book.high.team, book.high.score, book.high.week) == ("Three", 150.0, 1)
    assert (book.low.team, book.low.score, book.low.week) == ("Four", 60.0, 1)


def test_heartbreak_is_the_closest_loss_and_beatdown_the_biggest_margin_each_the_game_of_the_record_book():
    book, awards = _book(), _awards()
    assert (book.closest.loser, book.closest.winner, book.closest.margin, book.closest.week) == ("Two", "One", 0.5, 1)
    assert (book.biggest_margin.winner, book.biggest_margin.margin) == ("Three", 90.0)
    assert (awards["heartbreak"].team, awards["beatdown"].team) == ("Two", "Three")
    assert awards["heartbreak"].in_record_book and awards["beatdown"].in_record_book
    assert not awards["mvp"].in_record_book


def test_the_mvp_is_the_started_player_with_the_most_points_over_the_line():
    mvp = _awards()["mvp"]
    assert (mvp.player, mvp.team, mvp.value) == ("Back 3", "Three", 60.2)


def test_most_active_counts_adds_and_trades_and_set_and_forget_has_the_fewest_moves():
    awards = _awards()
    assert (awards["most-active"].team, awards["most-active"].value) == ("One", 3)
    # A failed claim is no move, so Three and Four tie at 0, and the name breaks the tie.
    assert (awards["set-and-forget"].team, awards["set-and-forget"].value) == ("Four", 0)


def test_bench_crime_is_the_loss_with_the_most_bench_points_and_the_streaming_king_is_the_first_streamer():
    awards = _awards()
    assert (awards["bench-crime"].team, awards["bench-crime"].value, awards["bench-crime"].week) == ("Two", 20.5, 1)
    assert awards["streaming-king"].team == "Four"


def test_each_of_the_seven_awards_has_a_winner_and_its_fact():
    awards = _book().awards
    assert [award.key for award in awards] == ["mvp", "streaming-king", "bench-crime", "heartbreak", "beatdown",
                                               "most-active", "set-and-forget"]
    assert all(award.fact for award in awards)
    assert _awards()["set-and-forget"].fact == "Four made 0 moves, the fewest in the league, and is 0-3-1."
