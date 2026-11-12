"""
The NFL game card of a free answer: the expected margin of one NFL game from the two Sleeper DEF projections, the 32
defenses against a position, and the pass share of each team, as a data tool result and as the block that code builds.
"""
import json
from collections import defaultdict

import httpx

from cornerstone_api.free_tools import WORD, SeasonData
from league.paths import history_week_dir
from league.provider.sleeper import UNOFFICIAL_URL

# The kind of the block. The site picks the view of the NFL game card from it.
NFL_GAME_KIND = "nfl_game"
TIMEOUT_SECONDS = 10
# The positions of the strip, by the suffix of the Sleeper stat `fan_pts_allow_<pos>`.
POSITIONS = ("QB", "RB", "WR", "TE")
# A team has at most one bye in a row, so the next game is in the live week or the week after.
WEEKS_AHEAD = 2

# What each field means, in the tool result, so Claude and the check read the same meaning.
GAME_MEANINGS = {
    "week": "The NFL week of the game: the live week, or the next week when the team has a bye in the live week.",
    "projected_points": "The NFL points that each team is projected to score. Each team scores the `pts_allow` of "
                        "the Sleeper DEF projection of the other team. It is a projection, not a betting line.",
    "expected_margin": "The projected points of `team` minus the projected points of `opponent`. Below 0, the "
                       "opponent is ahead.",
    "favorite": "The team with more projected points, or null for a tie.",
    "defense_against_position": "The fantasy points per game that the defense of `opponent` allows to `position` "
                                "this season, its place among the 32 defenses from 1, the fewest allowed, to 32, and "
                                "the league average. Null `position` means all positions together.",
    "pass_share": "The share of the plays of each NFL team this season that are passes: pass attempts over pass "
                  "attempts and carries. `league` is the share of all 32 teams.",
}


def fetch_def_projections(season: int, week: int) -> list[dict]:
    """The Sleeper projections of the 32 defenses for `week`, as JSON. A team on a bye has no row."""
    response = httpx.get(f"{UNOFFICIAL_URL}/projections/nfl/{season}/{week}",
                         params=[("season_type", "regular"), ("position[]", "DEF")], timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def _plain(text: str) -> str:
    return " ".join(WORD.findall(text.lower()))


def _names(row: dict) -> tuple[str, str]:
    """The full name and the nickname of the team of a DEF row, such as "Chicago Bears" and "Bears"."""
    entry = row.get("player") or {}
    city, nickname = entry.get("first_name") or "", entry.get("last_name") or row["player_id"]
    return f"{city} {nickname}".strip(), nickname


def _matches(row: dict, team: str) -> bool:
    full, nickname = _names(row)
    city = (row.get("player") or {}).get("first_name") or ""
    return _plain(team) in {_plain(row["player_id"]), _plain(full), _plain(nickname), _plain(city)}


def _saved_stats(data: SeasonData) -> list[dict]:
    """The Sleeper stat rows of each saved week, with the team of each row."""
    rows = []
    for week in data.saved():
        path = history_week_dir(data.history_root, week) / "stats.json"
        if path.exists():
            rows.extend(json.loads(path.read_text(encoding="utf-8")))
    return rows


def _strip(stats: list[dict], position: str | None) -> list[dict]:
    """The fantasy points per game that each defense allows to `position`, fewest first."""
    key = "fan_pts_allow" if position is None else f"fan_pts_allow_{position.lower()}"
    games: dict[str, list[float]] = defaultdict(list)
    for row in stats:
        line = row.get("stats") or {}
        if (row.get("player") or {}).get("position") == "DEF" and line.get("gp") and key in line:
            games[row["player_id"]].append(line[key])
    means = {team: round(sum(values) / len(values), 1) for team, values in games.items()}
    return [{"team": team, "allowed": means[team]} for team in sorted(means, key=lambda t: (means[t], t))]


def _share(stats: list[dict], team: str | None) -> float | None:
    passes = runs = 0.0
    for row in stats:
        if team is None or row.get("team") == team:
            line = row.get("stats") or {}
            passes += line.get("pass_att", 0.0)
            runs += line.get("rush_att", 0.0)
    return round(passes / (passes + runs), 3) if passes + runs else None


def _game(data: SeasonData, team: str) -> tuple[int, dict, dict] | dict:
    """The week, the DEF row of the team, and the DEF row of its opponent, or the error of the tool."""
    live = data.raw().state.display_week
    if data.fetch_def_projections is None:
        return {"error": "The NFL game projections are not available."}
    seen = False
    for week in range(live, live + WEEKS_AHEAD):
        try:
            rows = data.fetch_def_projections(data.season, week)
        except (httpx.HTTPError, ValueError):
            return {"error": "The NFL game projections did not load."}
        mine = next((row for row in rows if _matches(row, team)), None)
        if mine is None:
            continue
        theirs = next((row for row in rows if row["player_id"] == mine.get("opponent")), None)
        if theirs is not None:
            return week, mine, theirs
        seen = True
    if seen:
        return {"error": f"The {team} have no game with a projection in week {live} or week {live + 1}."}
    return {"error": f"No NFL team is named {team}."}


def nfl_game(data: SeasonData, team: str, position: str | None = None) -> dict:
    """The next game of the NFL team named `team`: the projected points and the expected margin from the two DEF
    projections, the defense of the opponent against `position`, the pass share of each team, and the NFL game card
    of the same facts under `block`."""
    if position is not None and position.upper() not in POSITIONS:
        return {"error": f"The position is one of {', '.join(POSITIONS)}, or none for all positions."}
    position = None if position is None else position.upper()
    found = _game(data, team)
    if isinstance(found, dict):
        return found
    week, mine, theirs = found
    (name, nickname), (other, other_nickname) = _names(mine), _names(theirs)
    # Each team scores what the DEF projection of the other team allows.
    points = theirs["stats"]["pts_allow"], mine["stats"]["pts_allow"]
    margin = round(points[0] - points[1], 2)
    stats = _saved_stats(data)
    strip = _strip(stats, position)
    lit = theirs["player_id"]
    place = next((i for i, row in enumerate(strip, start=1) if row["team"] == lit), None)
    shares = _share(stats, mine["player_id"]), _share(stats, lit), _share(stats, None)
    average = round(sum(row["allowed"] for row in strip) / len(strip), 1) if strip else None
    block = {
        "kind": NFL_GAME_KIND, "week": week, "title": f"Week {week}: {nickname} vs {other_nickname}",
        "sides": [{"code": mine["player_id"], "name": nickname, "projected": points[0]},
                  {"code": lit, "name": other_nickname, "projected": points[1]}],
        "margin": margin,
        "strip": {"position": position, "lit": lit, "average": average, "defenses": strip},
        "pass_share": {"league": shares[2], "sides": [{"code": mine["player_id"], "share": shares[0]},
                                                      {"code": lit, "share": shares[1]}]},
    }
    return {
        "week": week, "live_week": data.raw().state.display_week, "team": name, "opponent": other,
        "what_each_field_means": GAME_MEANINGS,
        "projected_points": {name: points[0], other: points[1]},
        "expected_margin": margin, "favorite": name if margin > 0 else other if margin < 0 else None,
        "defense_against_position": {
            "position": position, "defense": other,
            "allowed_per_game": next((row["allowed"] for row in strip if row["team"] == lit), None),
            "place": place, "of": len(strip), "league_average": average},
        "pass_share": {name: shares[0], other: shares[1], "league": shares[2]},
        "block": block,
    }
