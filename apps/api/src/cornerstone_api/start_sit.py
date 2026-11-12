"""
The Topic Start or sit: the live Sleeper week and its kickoffs for one request, and the facts of one roster from them,
the block of the lineup that the site shows and the Fact sheet of each player that Claude and the Jev checks read.
"""
import dataclasses
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from analyzer.trade_jev import YES_AT
from cornerstone_api.free_wording import plain_text, sentences
from cornerstone_api.game_lock import Kickoff, week_kickoffs
from cornerstone_api.personal_facts import PersonalFacts
from cornerstone_api.personal_wording import SWAP_MEANING, swap_question
from cornerstone_api.trade_wording import option_keys
from cornerstone_api.week_lineup import Player, Row, WeekLineup, week_lineup
from league.jev_port import Jev, JevError
from league.lineup import allowed_positions
from league.parse import team_name
from league.provider.raw import RawWeek

START_SIT = "start_sit"
# The kind of the data block of Start or sit. The site picks the view of the lineup block from it.
LINEUP_KIND = "lineup"


@dataclass(frozen=True)
class Swap:
    """A bench player who takes the slot at `index` of the lineup from its starter, and the probability of the Jev read
    that he scores more."""

    index: int
    bench: Player
    starter: Player
    probability: float


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
        """The facts of Start or sit for the roster, by projection, before the Jev read of the Swaps."""
        lineup = week_lineup(self.raw, roster_id, self.kickoffs, self.now)
        return PersonalFacts(slice=self._slice(roster_id, lineup, []), block=_block(roster_id, lineup, [], self.kickoffs))

    def judged(self, jev: Jev, roster_id: int) -> PersonalFacts:
        """The facts of Start or sit for the roster after the Jev read of the Swaps. Raises JevError when the read
        fails, because a failed read is never a "keep the starter"."""
        lineup = week_lineup(self.raw, roster_id, self.kickoffs, self.now)
        swaps = self.swaps(jev, roster_id, lineup)
        return PersonalFacts(slice=self._slice(roster_id, lineup, swaps), block=_block(roster_id, lineup, swaps, self.kickoffs))

    def swaps(self, jev: Jev, roster_id: int, lineup: WeekLineup) -> list[Swap]:
        """The Swaps of the lineup: one Jev request with one Choice per pair of a bench player and a starter whose slot
        he can fill, neither of them locked. A pair is a candidate at `YES_AT` or more. The candidate with the highest
        probability wins first, and each bench player and each slot takes one Swap at most."""
        pairs = [(index, bench, row.player) for index, row in enumerate(lineup.rows)
                 if row.player is not None and not row.locked
                 for bench in lineup.bench if bench.position in allowed_positions(row.slot)]
        if not pairs:
            return []
        team = self.team_name(roster_id)
        questions, keys = {}, {}
        for number, (index, bench, starter) in enumerate(pairs):
            option = option_keys({bench.player_id: bench.name, starter.player_id: starter.name})
            key = f"swap_{number}"
            keys[key] = option[bench.player_id]
            questions[key] = swap_question(lineup.rows[index].slot, team, lineup.week,
                                           (option[bench.player_id], bench.name),
                                           (option[starter.player_id], starter.name))
        players = [row.player for row in lineup.rows if row.player is not None] + lineup.bench
        state = {"scoring": self._scoring(), "week": lineup.week,
                 "players": {player.name: self.fact_sheet(player) for player in players}}
        response = jev.ask(state, questions)
        candidates = []
        for key, (index, bench, starter) in zip(questions, pairs, strict=True):
            probability = response.choices.get(key, {}).get(keys[key])
            if probability is None:
                raise JevError(f"the Jev read of the Swaps gave no answer for {key}")
            if probability >= YES_AT:
                candidates.append(Swap(index, bench, starter, probability))
        swaps, filled, moved = [], set(), set()
        for swap in sorted(candidates, key=lambda swap: (-swap.probability, swap.index)):
            if swap.index not in filled and swap.bench.player_id not in moved:
                swaps.append(swap)
                filled.add(swap.index)
                moved.add(swap.bench.player_id)
        return sorted(swaps, key=lambda swap: swap.index)

    def _scoring(self) -> str:
        rec = self.raw.league.scoring_settings.get("rec", 0.0)
        scoring = {0.5: "half PPR", 1.0: "full PPR"}.get(rec, f"{rec:g} points per reception")
        return f"The league scores {scoring}. Each projection is in the points of this league."

    def _slice(self, roster_id: int, lineup: WeekLineup, swaps: list[Swap]) -> dict:
        over = {swap.index: swap.starter.name for swap in swaps}
        swapped = with_swaps(lineup, swaps, self.kickoffs)
        facts = {"team": self.team_name(roster_id), "week": lineup.week, "scoring": self._scoring(),
                 "lineup": [{"slot": row.slot, **(self.fact_sheet(row.player) if row.player else {"player": None}),
                             "locked": row.locked,
                             **({"pivot": row.risk.pivot} if row.risk else {}),
                             **({"swap_over": over[index]} if index in over else {})}
                            for index, row in enumerate(swapped.rows)],
                 "bench": [self.fact_sheet(player) for player in swapped.bench],
                 "cannot_play": [{"player": absent.player.name, "status": absent.status,
                                  "body_part": absent.body_part} for absent in lineup.cannot_play],
                 "projected_total": lineup.shown_total}
        if swaps:
            facts |= {"projected_total_with_swaps": swapped.shown_total, "swap_means": SWAP_MEANING}
        return facts

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



def with_swaps(lineup: WeekLineup, swaps: list[Swap], kickoffs: list[Kickoff]) -> WeekLineup:
    """The lineup with each Swap: the bench player in the slot with his own game, and the starter on the bench."""
    games = {team: game for game in kickoffs for team in (game.home, game.away)}
    rows = list(lineup.rows)
    for swap in swaps:
        game = games.get(swap.bench.nfl_team or "")
        opponent = None if game is None else (game.away if game.home == swap.bench.nfl_team else game.home)
        rows[swap.index] = dataclasses.replace(rows[swap.index], player=swap.bench, opponent=opponent,
                                               kickoff=None if game is None else game.start, locked=False, risk=None)
    moved = {swap.bench.player_id for swap in swaps}
    bench = [player for player in lineup.bench if player.player_id not in moved] + [swap.starter for swap in swaps]
    return dataclasses.replace(lineup, rows=rows, bench=bench)


def _row(row: Row, swap: Swap | None) -> dict:
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
                                                   "practice": row.risk.practice, "pivot": row.risk.pivot},
            # The starter that a Swap benches, with his projection. Claude writes the reason, so it comes with the
            # checked text.
            "swap": None if swap is None else {"over": swap.starter.short_name,
                                               "over_projection": round(swap.starter.projection or 0.0, 1),
                                               "reason": None}}


def _block(roster_id: int, lineup: WeekLineup, swaps: list[Swap], kickoffs: list[Kickoff]) -> dict:
    """The lineup block: each row with its kickoff in epoch ms, so the site shows it in the time zone of the browser.
    `total` is the total by projection, and `swap_total` the total with the Swaps."""
    by_index = {swap.index: swap for swap in swaps}
    swapped = with_swaps(lineup, swaps, kickoffs)
    return {"kind": LINEUP_KIND, "topic": START_SIT, "team": roster_id, "week": lineup.week,
            "total": lineup.shown_total, "swap_total": swapped.shown_total,
            "rows": [_row(row, by_index.get(index)) for index, row in enumerate(swapped.rows)],
            "cannot_play": [{"name": absent.player.short_name, "status": absent.status, "body_part": absent.body_part}
                            for absent in lineup.cannot_play]}


# The suffixes after a last name, such as "Jr." in "Harold Fannin Jr.". A reason names the player by his last name.
NAME_SUFFIXES = frozenset({"Jr.", "Sr.", "II", "III", "IV", "V"})


def _last_name(name: str) -> str:
    """The last name of a full or a short name: "Kenneth Walker III" and "K. Walker III" both give "Walker"."""
    words = [word for word in name.split() if word not in NAME_SUFFIXES]
    return words[-1] if words else name


def _whole_sentences(text: str) -> list[str]:
    """The sentences of `text`, with a fragment that ends on a name suffix or an initial, such as "Jr." or "K.", joined
    to the next one, because a name does not end a sentence."""
    whole: list[str] = []
    for part in sentences(text):
        last = whole[-1].split()[-1] if whole else ""
        if last in NAME_SUFFIXES or (len(last) == 2 and last[0].isupper() and last.endswith(".")):
            whole[-1] = f"{whole[-1]} {part}"
        else:
            whole.append(part)
    return whole


def with_reasons(block: dict, text: str) -> dict:
    """The lineup block with the reason of each Swap: the first sentence of the checked `text` that names both players
    of the Swap by their last names. Claude writes the reasons, and the check passed each sentence, so a Swap with no
    such sentence keeps no reason."""
    said = _whole_sentences(plain_text(text))
    rows = []
    for row in block["rows"]:
        swap = row.get("swap")
        if swap is not None and row["player"] is not None:
            names = (_last_name(row["player"]), _last_name(swap["over"]))
            reason = next((sentence for sentence in said if all(name in sentence for name in names)), None)
            row = {**row, "swap": {**swap, "reason": reason}}
        rows.append(row)
    return {**block, "rows": rows}


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
