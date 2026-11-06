"""
The rules of the injury toll and of the missed games of one player, on small hand-built leagues: a missed game, the
key starter at the start of an absence, the fallback for a missing injury row, and the order of the teams.
"""
from collections.abc import Collection

from league.models import History, PastWeek
from midseason.injury import injury_toll, missed_games
from midseason.players import PlayerCard

NAMES = {1: "One", 2: "Two"}
PLAYERS = {
    "rb": PlayerCard(player_id="rb", name="Run Back", position="RB", nfl_team="CHI"),
    "wr": PlayerCard(player_id="wr", name="Wide Out", position="WR", nfl_team="SF"),
    "k": PlayerCard(player_id="k", name="Kick Er", position="K", nfl_team="CHI"),
    "bench": PlayerCard(player_id="bench", name="Bench Guy", position="RB", nfl_team="CHI"),
}
# Each NFL team plays every week of 1 to 8, except SF has its bye in week 6.
TEAM_WEEKS = {"CHI": set(range(1, 9)), "SF": {1, 2, 3, 4, 5, 7, 8}}


def _week(number: int, starters: dict[int, list[str]], snaps: set[str], off: Collection[str] = ()) -> PastWeek:
    rosters = {1: [pid for pid in ["rb", "wr", "k", "bench"] if pid not in off], 2: []}
    stats = {pid: {"off_snp": 50.0} for pid in snaps}
    return PastWeek(week=number, scores={1: 100.0, 2: 90.0}, pairs=[(1, 2)], points={}, projections={}, stats=stats,
                    moves=[], starters=starters, rosters=rosters)


def _history(missed: dict[str, set[int]], started: dict[str, set[int]], through: int = 8,
             dropped: dict[str, set[int]] | None = None) -> History:
    # `dropped` holds the weeks that each player is on no roster.
    weeks = {}
    for number in range(1, through + 1):
        snaps = {pid for pid in PLAYERS if number not in missed.get(pid, set())}
        starters = {1: [pid for pid in PLAYERS if number in started.get(pid, set())], 2: []}
        off = {pid for pid, gone in (dropped or {}).items() if number in gone}
        weeks[number] = _week(number, starters, snaps, off)
    return History(week=through, weeks=weeks)


def _games(toll, roster_id: int) -> int:
    return next(team.games for team in toll.teams if team.roster_id == roster_id)


def test_a_key_starter_out_on_the_injury_report_loses_each_game_of_his_absence():
    # The RB starts weeks 1 to 4, then misses weeks 5 to 8. He is a key starter when the absence starts.
    history = _history({"rb": {5, 6, 7, 8}}, {"rb": {1, 2, 3, 4}})
    toll = injury_toll(history, 8, NAMES, PLAYERS, report_out={"rb": {5, 6, 7, 8}}, roster_out={},
                       team_weeks=TEAM_WEEKS)
    assert _games(toll, 1) == 4
    team = toll.teams[0]
    assert [(p.name, p.games, p.weeks) for p in team.players] == [("Run Back", 4, [5, 6, 7, 8])]


def test_a_player_who_was_no_key_starter_when_the_absence_started_costs_nothing():
    # The bench RB never started, so his missed games are no starter games.
    history = _history({"bench": {5, 6}}, {})
    toll = injury_toll(history, 8, NAMES, PLAYERS, report_out={"bench": {5, 6}}, roster_out={},
                       team_weeks=TEAM_WEEKS)
    assert _games(toll, 1) == 0


def test_the_key_starter_rule_reads_the_weeks_before_the_absence_not_the_weeks_of_it():
    # The RB starts weeks 1 to 4. By week 7 he has started 2 of the last 4 weeks, but the absence started in week 5.
    history = _history({"rb": {5, 6, 7}}, {"rb": {1, 2, 3, 4}})
    toll = injury_toll(history, 8, NAMES, PLAYERS, report_out={"rb": {5, 6, 7}}, roster_out={},
                       team_weeks=TEAM_WEEKS)
    assert _games(toll, 1) == 3


def test_the_key_status_at_the_start_of_an_absence_holds_for_each_week_of_it_with_no_out_row():
    # The RB starts weeks 1 to 3. He is Out in week 4 and has no snap from week 4 to 8, with no more Out rows.
    history = _history({"rb": {4, 5, 6, 7, 8}}, {"rb": {1, 2, 3}})
    toll = injury_toll(history, 8, NAMES, PLAYERS, report_out={"rb": {4}}, roster_out={}, team_weeks=TEAM_WEEKS)
    assert toll.teams[0].players[0].weeks == [4, 5, 6, 7, 8]


def test_a_key_starter_that_the_team_drops_while_he_is_out_counts_until_he_plays_again():
    # The RB starts weeks 1 to 3, gets hurt, and the team drops him from week 4. He plays again in week 8.
    # Only week 7 has an out status, so the absence of weeks 4 to 7 counts as one injury.
    history = _history({"rb": {4, 5, 6, 7}}, {"rb": {1, 2, 3}}, dropped={"rb": {4, 5, 6, 7, 8}})
    toll = injury_toll(history, 8, NAMES, PLAYERS, report_out={}, roster_out={7: {"rb"}}, team_weeks=TEAM_WEEKS)
    assert [(p.name, p.weeks) for p in toll.teams[0].players] == [("Run Back", [4, 5, 6, 7])]


def test_the_key_starter_window_skips_the_injured_weeks_and_the_byes_of_the_player():
    # The WR starts weeks 1 and 2, is Out weeks 3 and 4, starts weeks 5 and 7, has the SF bye in week 6, and is Out in
    # week 8. His last 4 weeks that he could play are 1, 2, 5, and 7, and he started each one.
    history = _history({"wr": {3, 4, 8}}, {"wr": {1, 2, 5, 7}})
    toll = injury_toll(history, 8, NAMES, PLAYERS, report_out={"wr": {3, 4, 8}}, roster_out={},
                       team_weeks=TEAM_WEEKS)
    assert toll.teams[0].players[0].weeks == [3, 4, 8]


def test_a_bye_week_is_no_missed_game_and_does_not_end_the_absence():
    # The WR starts weeks 1 to 4 and is out weeks 5 to 8. SF has its bye in week 6.
    history = _history({"wr": {5, 6, 7, 8}}, {"wr": {1, 2, 3, 4}})
    toll = injury_toll(history, 8, NAMES, PLAYERS, report_out={"wr": {5, 7, 8}}, roster_out={},
                       team_weeks=TEAM_WEEKS)
    assert toll.teams[0].players[0].weeks == [5, 7, 8]


def test_a_week_with_no_snaps_and_a_roster_status_of_out_is_a_missed_game_with_no_injury_row():
    # The injury report has no Out row for the RB in week 5. He has no snaps, and his roster status is out.
    history = _history({"rb": {5}}, {"rb": {1, 2, 3, 4}})
    toll = injury_toll(history, 8, NAMES, PLAYERS, report_out={}, roster_out={5: {"rb"}}, team_weeks=TEAM_WEEKS)
    assert _games(toll, 1) == 1


def test_a_week_with_no_snaps_and_no_out_status_is_no_missed_game():
    # A healthy scratch is not an injury.
    history = _history({"rb": {5}}, {"rb": {1, 2, 3, 4}})
    toll = injury_toll(history, 8, NAMES, PLAYERS, report_out={}, roster_out={}, team_weeks=TEAM_WEEKS)
    assert _games(toll, 1) == 0


def test_a_week_with_snaps_is_no_missed_game_whatever_the_status():
    history = _history({}, {"rb": {1, 2, 3, 4}})
    toll = injury_toll(history, 8, NAMES, PLAYERS, report_out={"rb": {5}}, roster_out={5: {"rb"}},
                       team_weeks=TEAM_WEEKS)
    assert _games(toll, 1) == 0


def test_a_kicker_is_never_a_starter_of_the_toll():
    history = _history({"k": {5, 6}}, {"k": {1, 2, 3, 4}})
    toll = injury_toll(history, 8, NAMES, PLAYERS, report_out={"k": {5, 6}}, roster_out={}, team_weeks=TEAM_WEEKS)
    assert _games(toll, 1) == 0


def test_the_toll_counts_only_the_weeks_through_the_week_of_the_report():
    history = _history({"rb": {5, 6, 7, 8}}, {"rb": {1, 2, 3, 4}})
    toll = injury_toll(history, 6, NAMES, PLAYERS, report_out={"rb": {5, 6, 7, 8}}, roster_out={},
                       team_weeks=TEAM_WEEKS)
    assert _games(toll, 1) == 2


def test_the_teams_are_in_order_of_the_most_starter_games_lost_and_each_team_has_a_row():
    history = _history({"rb": {5, 6}}, {"rb": {1, 2, 3, 4}})
    toll = injury_toll(history, 8, NAMES, PLAYERS, report_out={"rb": {5, 6}}, roster_out={}, team_weeks=TEAM_WEEKS)
    assert [(team.name, team.games, team.rank) for team in toll.teams] == [("One", 2, 1), ("Two", 0, 2)]


def test_the_missed_games_of_a_player_count_each_week_out_with_no_snaps_and_no_bye_on_any_roster_or_none():
    # The draft tag reads this count. The WR is out weeks 5 to 8 by the injury report, and SF has its bye in week 6.
    # The RB misses week 5 with only a roster status of out. The bench RB plays week 7 with an Out row: no missed game.
    history = _history({"wr": {5, 6, 7, 8}, "rb": {5}}, {})
    missed = missed_games(["wr", "rb", "bench", "nobody"], history, 8, PLAYERS,
                          report_out={"wr": {5, 6, 7, 8}, "bench": {7}}, roster_out={5: {"rb"}},
                          team_weeks=TEAM_WEEKS)
    assert missed == {"wr": 3, "rb": 1, "bench": 0, "nobody": 0}


def test_a_player_with_no_snaps_and_no_out_status_misses_no_game():
    # A healthy scratch is no injury, so the bust of a benched player is "just bad".
    history = _history({"rb": {5, 6}}, {})
    assert missed_games(["rb"], history, 8, PLAYERS, report_out={}, roster_out={}, team_weeks=TEAM_WEEKS) == {"rb": 0}
