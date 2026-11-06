"""
The wire of three chapters of the midseason report: the injury toll, Position top 10, and the players to watch. It
reads the saved raw week, the nflverse files, and the rosters now, and hands each chapter its ports as plain data.
"""
import json
import logging
from pathlib import Path

from pydantic import BaseModel

from league.client import Client
from league.models import History
from league.nflverse import (
    FFIDS_URL,
    FFOPPORTUNITY_URL,
    INJURIES_URL,
    SCHEDULES_URL,
    cache_path,
    download,
    gsis_id,
    read_id_map,
    read_injuries,
    read_schedules,
)
from league.nflverse_expected import read_expected
from league.parse import player_name
from league.paths import history_root, nflverse_cache_dir, raw_dir
from league.provider.base import Provider
from league.provider.sleeper import load_raw
from midseason.injury import OUT_STATUSES, InjuryToll, injury_toll
from midseason.players import PlayerCard
from midseason.top10 import PositionTop10, position_top10
from midseason.watch import PlayersToWatch, players_to_watch

log = logging.getLogger(__name__)

# The nflverse files the three chapters read, by the name the stop line gives.
NFLVERSE_FILES = {"injuries": INJURIES_URL, "id map": FFIDS_URL, "expected points": FFOPPORTUNITY_URL,
                  "schedules": SCHEDULES_URL}
# The Sleeper status of each week sits beside the history of that week. GLOSSARY.md, "Injury toll".
SAVED_STATUS_FILE = "injuries.json"


class ChaptersStopped(Exception):
    """A chapter input is missing. The message is the plain line for Brian."""


class ReportChapters(BaseModel):
    injuries: InjuryToll
    top10: PositionTop10
    watch: PlayersToWatch


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
    """The facts of the three chapters of the report of `week`.

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
    cards = {pid: PlayerCard(player_id=pid, name=player_name(pid, entry), position=entry.get("position") or "?",
                             nfl_team=entry.get("team"))
             for pid, entry in raw.players.items()}

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
    injuries = injury_toll(history, week, names, cards, report_out=report_out,
                           roster_out=_roster_out(client, season, week), team_weeks=team_weeks)

    top10 = position_top10(history, week, cards, scoring, client.settings.positions, owners, names)

    expected = read_expected(files["expected points"], files["schedules"], season, week, scoring, sleeper_of_gsis,
                             window=None)
    if expected is None:
        raise ChaptersStopped(f"The nflverse schedules have no game of week {week}, so the expected points cannot "
                              "be read.")
    if expected.through_week < week:
        log.warning("The expected points file ends at week %s, so the players to watch read through it.",
                    expected.through_week)
    ahead = {entry.week: entry.projections for entry in raw.projections_ahead or []}
    watch = players_to_watch(history, week, cards, scoring, expected.players, owners, names, ahead=ahead,
                             last_regular_week=client.settings.last_regular_week, positions=client.settings.positions)
    return ReportChapters(injuries=injuries, top10=top10, watch=watch)
