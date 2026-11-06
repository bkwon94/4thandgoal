"""
The wire of two chapters of the midseason report: the injury toll and Position top 10. It
reads the saved raw week, the nflverse files, and the rosters now, and hands each chapter its ports as plain data.
It also gives the injury ports to the build, so the draft tags read the one download of the injury report.
"""
import json
import logging
from collections.abc import Mapping
from pathlib import Path

from pydantic import BaseModel

from league.client import Client
from league.models import History
from league.nflverse import (
    FFIDS_URL,
    INJURIES_URL,
    SCHEDULES_URL,
    cache_path,
    download,
    gsis_id,
    read_id_map,
    read_injuries,
    read_schedules,
)
from league.parse import player_name
from league.paths import history_root, nflverse_cache_dir, raw_dir
from league.provider.base import Provider
from league.provider.sleeper import load_raw
from midseason.injury import OUT_STATUSES, InjuryToll, injury_toll
from midseason.players import PlayerCard
from midseason.top10 import PositionTop10, position_top10

log = logging.getLogger(__name__)

# The nflverse files the two chapters read, by the name the stop line gives.
NFLVERSE_FILES = {"injuries": INJURIES_URL, "id map": FFIDS_URL, "schedules": SCHEDULES_URL}
# The Sleeper status of each week sits beside the history of that week. GLOSSARY.md, "Injury toll".
SAVED_STATUS_FILE = "injuries.json"


class ChaptersStopped(Exception):
    """A chapter input is missing. The message is the plain line for Brian."""


class InjuryPorts(BaseModel):
    """The ports of the missed-game rule of the injury toll, as `injury_toll` and `missed_games` take them."""
    # The weeks the nflverse injury report lists each player Out, by Sleeper ID.
    report_out: dict[str, set[int]]
    # The players with a Sleeper status of out, by week.
    roster_out: dict[int, set[str]]
    # The weeks each NFL team plays.
    team_weeks: dict[str, set[int]]


class ReportChapters(BaseModel):
    injuries: InjuryToll
    top10: PositionTop10
    injury_ports: InjuryPorts


def player_cards(entries: Mapping[str, dict]) -> dict[str, PlayerCard]:
    """The card of each player of the Sleeper players file `entries`, by Sleeper ID. A player with no position gets an
    empty one, so no chapter of a position counts him."""
    return {pid: PlayerCard(player_id=pid, name=player_name(pid, entry), position=entry.get("position") or "",
                            nfl_team=entry.get("team"))
            for pid, entry in entries.items()}


def _nflverse(client: Client, season: int) -> dict[str, Path]:
    """The path of each nflverse file, fetched when the cache is stale. A file with no cache and no fetch stops."""
    cache = nflverse_cache_dir(client.nfl_dir)
    paths = {}
    for name, url in NFLVERSE_FILES.items():
        # Some URLs hold the season field, so the fetch fills it in, as the cache name does.
        path = download(url.format(season=season), cache_path(cache, url, season))
        if path is None:
            raise ChaptersStopped(f"The nflverse {name} file is not in {cache} and the fetch failed. "
                                  "Check the network, then run the build again.")
        paths[name] = path
    return paths


def _roster_out(client: Client, season: int, week: int) -> dict[int, set[str]]:
    """The players with a Sleeper status of out in each saved week. A week with no saved status file has none."""
    out: dict[int, set[str]] = {}
    for number in range(1, week + 1):
        path = history_root(client.folder, season) / f"week-{number:02d}" / SAVED_STATUS_FILE
        if path.exists():
            statuses = json.loads(path.read_text(encoding="utf-8"))
            out[number] = {pid for pid, status in statuses.items() if status in OUT_STATUSES}
    return out


def report_chapters(
    season: int, week: int, history: History, names: dict[int, str], *, client: Client,
    provider: Provider | None = None,
) -> ReportChapters:
    """The facts of the two chapters of the report of `week`.

    The rosters now come from `provider`, so a player a manager dropped after the report week is a free agent. With
    no provider, the rosters of the saved raw week stand in.
    """
    folder = raw_dir(client.folder, season, week)
    if not folder.exists():
        raise ChaptersStopped(f"Week {week} has no saved raw files. Run make build CLIENT={client.slug} WEEK={week} "
                              "first.")
    raw = load_raw(folder)
    scoring = raw.league.scoring_settings
    rosters = provider.fetch_live(client.league_id(season))[0].rosters if provider is not None else raw.rosters
    owners = {pid: roster.roster_id for roster in rosters for pid in roster.players or []}
    cards = player_cards(raw.players)

    files = _nflverse(client, season)
    id_map = read_id_map(files["id map"])
    sleeper_of_gsis = {gsis: pid for pid, gsis in sorted(id_map.items())}
    # A Sleeper player with a gsis ID in the players file but none in the id map still joins the injury report.
    for pid in raw.players:
        gsis = gsis_id(pid, raw.players, id_map)
        if gsis is not None:
            sleeper_of_gsis.setdefault(gsis, pid)
    report = read_injuries(files["injuries"], week)
    if report is None:
        raise ChaptersStopped(f"The nflverse injury report has no row of week {week} yet. Run the build again later.")
    report_out = {sleeper_of_gsis[gsis]: {number for number, status in weeks.items() if status == "Out"}
                  for gsis, weeks in report.items() if gsis in sleeper_of_gsis}
    schedules = read_schedules(files["schedules"], season) or {}
    team_weeks = {team: set(schedule.games) for team, schedule in schedules.items()}
    roster_out = _roster_out(client, season, week)
    # The saved status file holds only rostered players. The players file of the report week holds the status of each
    # player, so a key starter that a team dropped while he is out still has an out status, such as De'Von Achane.
    roster_out.setdefault(week, set()).update(
        pid for pid, entry in raw.players.items() if entry.get("injury_status") in OUT_STATUSES)
    ports = InjuryPorts(report_out=report_out, roster_out=roster_out, team_weeks=team_weeks)
    injuries = injury_toll(history, week, names, cards, report_out=ports.report_out, roster_out=ports.roster_out,
                           team_weeks=ports.team_weeks)

    top10 = position_top10(history, week, cards, scoring, client.settings.positions, owners, names)
    return ReportChapters(injuries=injuries, top10=top10, injury_ports=ports)
