"""
The Topic Start or sit: the live Sleeper week and its kickoffs for one request, and the facts of one roster from them,
the block of the lineup that the site shows and the Fact sheet of each player that Claude and the Jev check read.
"""
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from cornerstone_api.game_lock import Kickoff, week_kickoffs
from cornerstone_api.personal_facts import PersonalFacts
from cornerstone_api.week_lineup import Player, Row, WeekLineup, week_lineup
from league.parse import team_name
from league.provider.raw import RawWeek

START_SIT = "start_sit"
# The kind of the data block of Start or sit. The site picks the view of the lineup block from it.
LINEUP_KIND = "lineup"


@dataclass(frozen=True)
class LiveWeek:
    """The live week of one request: the raw Sleeper data, the kickoffs of the week, the clock, and the league time
    zone. Start or sit reads only Sleeper and the kickoffs, so it fetches no slow source and no news (AT-53)."""

    raw: RawWeek
    kickoffs: list[Kickoff]
    now: datetime
    tz: ZoneInfo

    @property
    def rosters(self) -> dict[int, list[str]]:
        return {roster.roster_id: list(roster.players or []) for roster in self.raw.rosters}

    def team_name(self, roster_id: int) -> str:
        """The team name of the roster, as the snapshot names it: the team name of its manager, or his user name."""
        owner = next(r.owner_id for r in self.raw.rosters if r.roster_id == roster_id)
        user = next((u for u in self.raw.users if u.user_id == owner), None)
        return f"Team {roster_id}" if user is None else team_name(user)

    def facts(self, roster_id: int) -> PersonalFacts:
        """The facts of Start or sit for the roster."""
        lineup = week_lineup(self.raw, roster_id, self.kickoffs, self.now)
        return PersonalFacts(slice=self._slice(roster_id, lineup), block=_block(roster_id, lineup))

    def _slice(self, roster_id: int, lineup: WeekLineup) -> dict:
        rec = self.raw.league.scoring_settings.get("rec", 0.0)
        scoring = {0.5: "half PPR", 1.0: "full PPR"}.get(rec, f"{rec:g} points per reception")
        return {"team": self.team_name(roster_id), "week": lineup.week,
                "scoring": f"The league scores {scoring}. Each projection is in the points of this league.",
                "lineup": [{"slot": row.slot, **(self.fact_sheet(row.player) if row.player else {"player": None}),
                            "locked": row.locked,
                            **({"pivot": row.risk.pivot} if row.risk else {})} for row in lineup.rows],
                "bench": [self.fact_sheet(player) for player in lineup.bench],
                "cannot_play": [{"player": absent.player.name, "status": absent.status,
                                 "body_part": absent.body_part} for absent in lineup.cannot_play],
                "projected_total": round(lineup.total, 1)}

    def fact_sheet(self, player: Player) -> dict:
        """The Fact sheet of one player: his team, his game, his projection and its stat line, and his status. The
        state of a Jev read keys each sheet by the player name."""
        games = {team: game for game in self.kickoffs for team in (game.home, game.away)}
        game = games.get(player.nfl_team or "")
        opponent = None if game is None else (game.away if game.home == player.nfl_team else game.home)
        return {"player": player.name, "position": player.position, "nfl_team": player.nfl_team,
                "opponent": opponent,
                "kickoff": None if game is None else game.start.astimezone(self.tz).strftime("%a %-I:%M %p %Z"),
                "projection": None if player.projection is None else round(player.projection, 1),
                "projected_stat_line": player.stat_line, "injury_status": player.injury_status,
                "body_part": player.body_part, "practice_participation": player.practice}


def _row(row: Row) -> dict:
    player = row.player
    return {"slot": row.slot, "player": None if player is None else player.name,
            "player_id": None if player is None else player.player_id,
            "position": None if player is None else player.position,
            "nfl_team": None if player is None else player.nfl_team,
            "opponent": row.opponent,
            "kickoff": None if row.kickoff is None else int(row.kickoff.timestamp() * 1000),
            "projection": None if player is None or player.projection is None else round(player.projection, 1),
            "locked": row.locked,
            "risk": None if row.risk is None else {"tag": "Q", "body_part": row.risk.body_part,
                                                   "practice": row.risk.practice, "pivot": row.risk.pivot}}


def _block(roster_id: int, lineup: WeekLineup) -> dict:
    """The lineup block: each row with its kickoff in epoch ms, so the site shows it in the time zone of the browser."""
    return {"kind": LINEUP_KIND, "topic": START_SIT, "team": roster_id, "week": lineup.week,
            "total": round(lineup.total, 1), "rows": [_row(row) for row in lineup.rows],
            "cannot_play": [{"name": absent.player.short_name, "status": absent.status, "body_part": absent.body_part}
                            for absent in lineup.cannot_play]}


def load_live_week(sources, season: int) -> LiveWeek:
    """The live week for the client of `sources`: one fetch of the Sleeper week, then its kickoffs, both fresh.

    Raises ValueError when Sleeper is not in `season`, and KickoffsError, a ValueError, when no source gives the
    kickoffs, because no lineup can respect the game lock without them.
    """
    raw, _ = sources.fetch_sleeper(sources.client.current_league_id)
    if int(raw.state.season) != season:
        raise ValueError(f"Sleeper is in season {raw.state.season}, not {season}")
    week = raw.state.display_week
    kickoffs = week_kickoffs(season, week, sources.fetch_sleeper_scores, sources.fetch_espn_scoreboard)
    return LiveWeek(raw=raw, kickoffs=kickoffs, now=sources.clock(), tz=sources.client.tz)
