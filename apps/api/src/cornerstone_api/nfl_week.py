"""
The NFL facts that the NFL game card of a free answer and the Fact sheet of Start or sit both read: the Sleeper DEF
projections of a week, the saved Sleeper stat rows, the defenses against a position, the pass share, and the usage.
"""
import json
from collections import defaultdict
from pathlib import Path

import httpx

from league.paths import history_week_dir
from league.provider.sleeper import UNOFFICIAL_URL

TIMEOUT_SECONDS = 10


def fetch_def_projections(season: int, week: int) -> list[dict]:
    """The Sleeper projections of the 32 defenses for `week`, as JSON. A team on a bye has no row."""
    response = httpx.get(f"{UNOFFICIAL_URL}/projections/nfl/{season}/{week}",
                         params=[("season_type", "regular"), ("position[]", "DEF")], timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def saved_stats(history_root: Path, weeks: list[int]) -> dict[int, list[dict]]:
    """The Sleeper stat rows of each saved week of `weeks`, by week. A week with no saved stats has no entry."""
    rows = {}
    for week in weeks:
        path = history_week_dir(history_root, week) / "stats.json"
        if path.exists():
            rows[week] = json.loads(path.read_text(encoding="utf-8"))
    return rows


def defense_strip(stats: list[dict], position: str | None) -> list[dict]:
    """The fantasy points per game that each defense allows to `position`, fewest first. None reads all positions."""
    key = "fan_pts_allow" if position is None else f"fan_pts_allow_{position.lower()}"
    games: dict[str, list[float]] = defaultdict(list)
    for row in stats:
        line = row.get("stats") or {}
        if (row.get("player") or {}).get("position") == "DEF" and line.get("gp") and key in line:
            games[row["player_id"]].append(line[key])
    means = {team: round(sum(values) / len(values), 1) for team, values in games.items()}
    return [{"team": team, "allowed": means[team]} for team in sorted(means, key=lambda t: (means[t], t))]


def pass_share(stats: list[dict], team: str | None) -> float | None:
    """The share of the plays of `team` that are passes: pass attempts over pass attempts and carries. None reads the
    plays of all teams."""
    passes = runs = 0.0
    for row in stats:
        if team is None or row.get("team") == team:
            line = row.get("stats") or {}
            passes += line.get("pass_att", 0.0)
            runs += line.get("rush_att", 0.0)
    return round(passes / (passes + runs), 3) if passes + runs else None


def usage_shares(weeks: dict[int, list[dict]], player_id: str) -> dict[str, float | None]:
    """The share of the targets, the carries, and the offensive snaps of his NFL team that the player had, over the
    games that he played in `weeks`. Each share is None when he played no game, or his team had none of that stat."""
    mine = {"rec_tgt": 0.0, "rush_att": 0.0, "off_snp": 0.0}
    team_totals = {"rec_tgt": 0.0, "rush_att": 0.0, "off_snp": 0.0}
    for rows in weeks.values():
        row = next((row for row in rows if row["player_id"] == player_id and (row.get("stats") or {}).get("gp")), None)
        if row is None:
            continue
        line = row["stats"]
        for key in mine:
            mine[key] += line.get(key, 0.0)
        team_rows = [other.get("stats") or {} for other in rows if other.get("team") == row.get("team")]
        team_totals["rec_tgt"] += sum(other.get("rec_tgt", 0.0) for other in team_rows)
        team_totals["rush_att"] += sum(other.get("rush_att", 0.0) for other in team_rows)
        # Each player row of a game carries the offensive snaps of his team, so the row of the player gives them.
        team_totals["off_snp"] += line.get("tm_off_snp", 0.0)

    def share(key: str) -> float | None:
        return round(mine[key] / team_totals[key], 3) if team_totals[key] else None

    return {"target_share": share("rec_tgt"), "carry_share": share("rush_att"), "snap_share": share("off_snp")}
