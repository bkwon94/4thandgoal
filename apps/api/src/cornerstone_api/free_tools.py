"""
The data tools of a free answer: the standings, the results and the moves of any week, any roster, the game log of any
player, and the roster grade of each team. Each tool gives plain JSON with names, never a raw id.
"""
import re
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal
from functools import cached_property
from pathlib import Path
from zoneinfo import ZoneInfo

from cornerstone_api.personal_facts import PART_NAMES
from league.history import load_saved_weeks
from league.models import History, PastWeek
from league.numbers import r2
from league.parse import player_name
from league.provider.raw import RawWeek
from league.ranks import OUT_STATUSES, STATUS_WORDS
from league.standings_table import season_records, standings_order, week_median
from managers.grade import ManagerGrade

# The time zone of a season with no league time zone, such as in a test.
UTC_ZONE = ZoneInfo("UTC")
# The stat keys of a game log line, by the plain name that the tool shows. A key missing from a line is a zero.
GAME_STATS = {
    "pass_yards": "pass_yd", "pass_tds": "pass_td", "interceptions": "pass_int", "rush_attempts": "rush_att",
    "rush_yards": "rush_yd", "rush_tds": "rush_td", "targets": "rec_tgt", "receptions": "rec", "rec_yards": "rec_yd",
    "rec_tds": "rec_td", "fumbles_lost": "fum_lost",
}
# A player search lists at most this many names, so a short query gives a short pick.
PLAYER_MATCHES = 5
# A query word, such as "bijan" of "Bijan Robinson".
WORD = re.compile(r"[a-z0-9']+")
# What each field of the roster grades means. The meanings ride in the tool result, so Claude and the check of each
# sentence read the same meaning beside the same numbers. A meaning only in the instructions never reaches the check.
GRADE_MEANINGS = {
    "grade": "The roster grade letter of the team, the same grade as the managers page. A is the best letter, then B, "
             "C, and D. More than one team can hold the same letter.",
    "grade_rank": "The place of the roster in the league by the score behind its letter: 1 is the best roster of the "
                  "league and 12 is the weakest. No two teams share a place.",
    "parts": "The four parts of the roster grade, each with the rank of the team on that part, from 1, the best of "
             "the league, to 12. Projection Ahead reads the starters by the projections to the end of the regular "
             "season. Season Production reads the best lineup by the points per game so far. Trade Value reads the "
             "market value of the whole roster. Depth And Holes reads the spare starters and the empty starter slots.",
    "as_of": "`as_of` says every grade here is from the live league today, so say \"as of today\". The grade of the "
             "managers page is from the last week of the weekly build, so it can differ.",
}

# What the rank fields of the standings mean. A standings result holds two ranks, and the teams come in the order of
# the standings, so without these meanings a row of a list by points reads against the wrong rank (H29). The order by
# points rides as its own field too, so the check never sorts close totals by eye.
STANDINGS_MEANINGS = {
    "rank": "The place of the team in the standings, by record, from 1 to 12. The teams are in this order.",
    "points_for": "The fantasy points that the team scored this season, through `through_week`.",
    "points_for_rank": "The place of the team by `points_for`, from 1, the most points of the league, to 12. A list of "
                       "the highest scoring teams follows this field, not `rank`.",
    "teams_by_points_for": "The names of the teams in the order of `points_for_rank`, the most points first.",
}


# What the status fields of a player mean, in the tool result, so the check reads "cannot play now" beside the field.
STATUS_MEANINGS = {
    "status": "The status of the player on the injury report now, such as \"out\" or \"on IR\". \"healthy\" means "
              "the report lists no status.",
    "can_play_now": "False when the status keeps the player out now, such as out, on IR, or suspended. A player "
                    "listed as questionable can still play.",
}


def _status(entry: dict) -> dict:
    """The status of a player on the injury report of the live fetch, and whether he can play now."""
    reported = entry.get("injury_status") or ""
    return {"status": STATUS_WORDS.get(reported, reported.lower() or "healthy"),
            "can_play_now": reported not in OUT_STATUSES}


@dataclass(frozen=True)
class LeagueGrades:
    """The roster grade of each roster now, and its place in the league by the score of the grade, by roster id."""

    grades: dict[int, ManagerGrade]
    places: dict[int, int]


@dataclass
class SeasonData:
    """The data of one free answer: the season, the latest week that the site shows, the team name of each roster, the
    folder of the saved weeks, and the live Sleeper fetch for the rosters and the player names.

    The saved weeks load on the first read, and the live fetch runs only when a tool needs a roster or a name.
    """

    season: int
    week: int
    teams: dict[int, str]
    history_root: Path
    points_key: str
    median_game: bool
    fetch_raw: Callable[[], RawWeek]
    # The live roster grades, as stack_up reads them. They load only when a tool reads them, because the live league
    # costs a snapshot load.
    fetch_grades: Callable[[], LeagueGrades] | None = None
    # The time zone of the league, so a day of the moves reads as the managers read it.
    tz: ZoneInfo = UTC_ZONE
    _raw: RawWeek | None = field(default=None, init=False, repr=False)

    @cached_property
    def history(self) -> History:
        return History(week=self.week, weeks=load_saved_weeks(self.history_root, self.week, self.points_key))

    def raw(self) -> RawWeek:
        if self._raw is None:
            self._raw = self.fetch_raw()
        return self._raw

    def name(self, player_id: str) -> str:
        return player_name(player_id, self.raw().players.get(player_id))

    def saved(self) -> list[int]:
        return sorted(self.history.weeks)


def _team(data: SeasonData, roster_id: int) -> str:
    return data.teams.get(roster_id, f"roster {roster_id}")


def _no_week(data: SeasonData, week: int) -> dict:
    saved = data.saved()
    span = f"weeks {saved[0]} to {saved[-1]}" if saved else "no week"
    return {"error": f"Week {week} has no saved results. This season holds {span}."}


def standings(data: SeasonData) -> dict:
    """The record, the points for with its rank, and the points against of each team over the saved weeks, in the
    order of the standings."""
    # The records need every week from 1, so a gap in the saved weeks ends the table before it.
    through = 0
    while through + 1 in data.history.weeks:
        through += 1
    if through == 0:
        return {"error": "No week of this season is saved yet."}
    records = season_records(data.history, through, median_game=data.median_game)
    head = defaultdict(lambda: [0, 0])
    against: dict[int, Decimal] = defaultdict(Decimal)
    for number in range(1, through + 1):
        week = data.history.weeks[number]
        for a, b in week.pairs:
            for mine, theirs in ((a, b), (b, a)):
                against[mine] += Decimal(str(week.scores[theirs]))
                if week.scores[mine] > week.scores[theirs]:
                    head[mine][0] += 1
                elif week.scores[mine] < week.scores[theirs]:
                    head[mine][1] += 1
    order = standings_order(records)
    # The rank by points for is its own field, so "third in points" reads from the data and not from a sort by eye.
    by_points = {rid: rank for rank, rid in enumerate(sorted(records, key=lambda r: -records[r][2]), start=1)}
    return {
        "through_week": through,
        "how_records_count": (f"Each week is two games: the head-to-head game and a game against the league median "
                              f"score. So a record over {through} weeks has {2 * through} games.")
        if data.median_game else "Each week is one head-to-head game.",
        "what_each_field_means": STANDINGS_MEANINGS,
        "teams_by_points_for": [_team(data, rid) for rid in sorted(by_points, key=by_points.__getitem__)],
        "teams": [
            {"rank": rank, "team": _team(data, rid), "record": f"{records[rid][0]}-{records[rid][1]}",
             "head_to_head_record": f"{head[rid][0]}-{head[rid][1]}", "points_for": records[rid][2], "points_for_rank": by_points[rid],
             "points_against": r2(float(against[rid]))}
            for rank, rid in enumerate(order, start=1)
        ],
    }


def week_results(data: SeasonData, week: int) -> dict:
    """The score of each game of one week, its winner, and the median line of the week."""
    past = data.history.weeks.get(week)
    if past is None:
        return _no_week(data, week)
    median = r2(float(week_median(past)))
    games = []
    for a, b in past.pairs:
        sa, sb = past.scores[a], past.scores[b]
        winner = _team(data, a) if sa > sb else _team(data, b) if sb > sa else None
        games.append({"teams": [{"team": _team(data, a), "score": sa}, {"team": _team(data, b), "score": sb}],
                      "winner": winner})
    ranked = sorted(past.scores, key=lambda rid: -past.scores[rid])
    return {
        "week": week,
        "games": games,
        "median_score": median,
        "beat_the_median": [_team(data, rid) for rid in ranked if past.scores[rid] > median],
        "high_score": {"team": _team(data, ranked[0]), "score": past.scores[ranked[0]]},
        "low_score": {"team": _team(data, ranked[-1]), "score": past.scores[ranked[-1]]},
    }


def week_moves(data: SeasonData, week: int) -> dict:
    """The trades, the waiver claims with their FAAB bids, the free agent adds, and the drops of one week."""
    past = data.history.weeks.get(week)
    if past is None:
        return _no_week(data, week)
    trades = [
        {"teams": [_team(data, rid) for rid in trade.roster_ids],
         "players_moved": [{"player": data.name(pid), "to": _team(data, to), "from": _team(data, trade.drops.get(pid, to))}
                           for pid, to in trade.adds.items()],
         "draft_picks": [f"{pick.season} round {pick.round} to {_team(data, pick.roster_id)}" for pick in trade.draft_picks]}
        for trade in past.trades
    ]
    adds = [{"player": data.name(move.player_id), "team": _team(data, move.roster_id),
             "kind": "waiver claim" if move.kind == "waiver" else "free agent add",
             **({"faab_bid": move.bid} if move.kind == "waiver" and move.bid is not None else {})}
            for move in past.moves if move.kind != "trade"]
    drops = [{"player": data.name(drop.player_id), "team": _team(data, drop.roster_id)} for drop in past.drops]
    return {"week": week, "trades": trades, "adds": adds, "drops": drops}


def season_moves(data: SeasonData) -> dict:
    """The moves of each saved week, so a question about the whole season takes one call and not one per week."""
    return {"weeks": [week_moves(data, week) for week in data.saved()]}


def find_team(data: SeasonData, team: str) -> int | None:
    """The roster of the team whose name is `team`, with case and signs ignored. A name of no team gives None."""
    wanted = _plain(team)
    return next((rid for rid, name in data.teams.items() if _plain(name) == wanted), None)


def _plain(text: str) -> str:
    return " ".join(WORD.findall(text.lower()))


def _season_points(data: SeasonData, player_id: str) -> float:
    return r2(sum(week.stats.get(player_id, {}).get(data.points_key, 0.0) for week in data.history.weeks.values()))


def team_roster(data: SeasonData, team: str) -> dict:
    """The players on one team now, with the position, the NFL team, the fantasy points of this season, and the status
    of the injury report."""
    roster_id = find_team(data, team)
    if roster_id is None:
        return {"error": f"No team is named {team}.", "teams": sorted(data.teams.values())}
    raw = data.raw()
    players = next((r.players or [] for r in raw.rosters if r.roster_id == roster_id), [])
    rows = [{"player": data.name(pid), "position": (raw.players.get(pid) or {}).get("position"),
             "nfl_team": (raw.players.get(pid) or {}).get("team"), "season_points": _season_points(data, pid),
             **_status(raw.players.get(pid) or {})}
            for pid in players]
    return {"team": _team(data, roster_id), "what_each_field_means": STATUS_MEANINGS,
            "players": sorted(rows, key=lambda row: -row["season_points"])}


def _matches(data: SeasonData, player: str) -> list[str]:
    """The ids of the players named `player`: the exact name, else each player whose name holds every query word."""
    wanted = _plain(player)
    entries = data.raw().players
    exact = [pid for pid, entry in entries.items() if _plain(player_name(pid, entry)) == wanted]
    if exact:
        return exact
    words = set(wanted.split())
    return [pid for pid, entry in entries.items() if words and words <= set(_plain(player_name(pid, entry)).split())]


def _holder(past: PastWeek, player_id: str) -> int | None:
    return next((rid for rid, players in past.rosters.items() if player_id in players), None)


def player_log(data: SeasonData, player: str) -> dict:
    """The game log of one NFL player over the saved weeks: the fantasy points and the main stats of each week, and the
    team of the league that held him each week."""
    found = _matches(data, player)
    # A player with a stat line this season comes first, so "Josh Allen" finds the quarterback who plays.
    found.sort(key=lambda pid: -_season_points(data, pid))
    if not found:
        return {"error": f"No NFL player is named {player}."}
    if len(found) > 1 and _season_points(data, found[1]) > 0:
        return {"error": f"More than one player matches {player}. Ask for one of these names.",
                "players": [data.name(pid) for pid in found[:PLAYER_MATCHES]]}
    pid = found[0]
    entry = data.raw().players.get(pid) or {}
    weeks = []
    for number in data.saved():
        past = data.history.weeks[number]
        line = past.stats.get(pid)
        holder = _holder(past, pid)
        row: dict = {"week": number, "league_team": _team(data, holder) if holder is not None else "free agent"}
        if holder is not None:
            row["started"] = pid in past.starters.get(holder, [])
        if line is None or not line.get("gp"):
            row["played"] = False
        else:
            row["fantasy_points"] = line.get(data.points_key, 0.0)
            row.update({name: line[key] for name, key in GAME_STATS.items() if line.get(key)})
        weeks.append(row)
    return {"player": data.name(pid), "position": entry.get("position"), "nfl_team": entry.get("team"),
            "season_points": _season_points(data, pid), **_status(entry), "what_each_field_means": STATUS_MEANINGS,
            "weeks": weeks}


def roster_grades(data: SeasonData) -> dict:
    """The roster grade of each team now, best first: the letter, the place in the league, and the rank of each part,
    with the meaning of each field."""
    if data.fetch_grades is None:
        return {"error": "The roster grades are not available."}
    try:
        league = data.fetch_grades()
    except ValueError:
        return {"error": "The roster grades did not load."}
    order = sorted(league.places, key=lambda rid: league.places[rid])
    return {
        "as_of": "today",
        "what_each_field_means": GRADE_MEANINGS,
        "teams": [
            {"grade_rank": league.places[rid], "team": _team(data, rid), "grade": league.grades[rid].letter,
             "parts": [{"part": PART_NAMES[part.key], "rank": part.rank} for part in league.grades[rid].parts]}
            for rid in order
        ],
    }
