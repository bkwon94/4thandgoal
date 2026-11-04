"""
The sneaky and stash buckets of the waiver board, each entry with the code of the rule that put him there.
The code is pure: it reads the scored pool, the depth charts, the injury report, and the returns file.
"""
from collections.abc import Callable
from typing import NamedTuple

from cornerstone.rank_score import rank_scores
from cornerstone.sheet.base import Nums, fact
from cornerstone.tunables import BUCKET_POSITIONS, SNEAKY_USAGE_FLOOR, TOP_HALF
from league.client import Client
from league.models import Fact, WaiverPlayer
from league.nflverse import gsis_id
from league.parse import player_name
from league.ranks import OUT_STATUSES, back_inside
from league.slow_sources import SlowSources

SNEAKY = "sneaky"
STASHES = "stashes"
# The bucket reasons. The site says which rule put a player in a bucket from these codes.
USAGE_RISE = "usage_rise"
BEHIND_INJURY = "behind_injury"
RETURN = "return"
HANDCUFF = "handcuff"

# The words of the story fact for each status of OUT_STATUSES: "{starter} is {word}".
STATUS_WORDS = {"Out": "out", "IR": "on IR", "PUP": "on the PUP list", "Sus": "suspended", "NA": "not active"}


class BucketInputs(NamedTuple):
    """The inputs of the sneaky and stash buckets. The engine builds them once per board."""
    # The Sleeper players file by Sleeper ID.
    sleeper_players: dict[str, dict]
    week: int
    # None leaves out every rule that needs the depth charts or the injury report.
    slow: SlowSources | None
    # The hand-kept return week by Sleeper ID.
    returns: dict[str, int]
    # The rest of season projection of any player, a rostered one too.
    ros_of: Callable[[str], float]
    # The league sizes. A stash must be back by the last season week.
    client: Client

    def gsis_of(self, player_id: str) -> str | None:
        """The gsis_id of the player. The id map fills the IDs that the Sleeper players file lacks."""
        id_map = (self.slow.id_map if self.slow is not None else None) or {}
        return gsis_id(player_id, self.sleeper_players, id_map)

    def return_week_of(self, player_id: str) -> int | None:
        """The return week of the player, from the returns file first and the injury report second."""
        injuries = self.slow.injuries if self.slow is not None else None
        return return_week(player_id, self.gsis_of(player_id), self.week, self.returns, injuries)


class PlayerAbove(NamedTuple):
    """The player one depth chart slot above a pool player, with his Sleeper injury status."""
    player_id: str
    name: str
    status: str | None
    # True when he is first on the chart, the starter.
    starter: bool


def sneaky_and_stashes(
    players: list[WaiverPlayer], best_adds: list[WaiverPlayer], inputs: BucketInputs,
) -> dict[str, list[WaiverPlayer]]:
    """The sneaky and the stash candidates in rank order, each with his reason. The engine applies the bucket cap.

    A player in best adds is not sneaky. With no depth chart, no player is behind an injury or a handcuff.
    """
    above_by_player = _players_above(players, inputs)
    return {SNEAKY: _sneaky(players, best_adds, above_by_player),
            STASHES: _stashes(players, inputs, above_by_player)}


def _sneaky(players: list[WaiverPlayer], best_adds: list[WaiverPlayer],
            above_by_player: dict[str, PlayerAbove]) -> list[WaiverPlayer]:
    """The pool players with a top-quarter usage score and a bottom-half projection, or behind an injured player.

    A player who is out himself is not sneaky.
    """
    taken = {p.player_id for p in best_adds}
    sneaky = []
    for p in players:
        if p.position not in BUCKET_POSITIONS or p.player_id in taken or p.injury_status in OUT_STATUSES:
            continue
        player_above = above_by_player.get(p.player_id)
        # The injury is the story of a usage rise too, so behind_injury wins when both rules hold.
        if player_above is not None and player_above.status in OUT_STATUSES:
            sneaky.append(_entry(p, BEHIND_INJURY, player_above))
        elif p.scores.usage >= SNEAKY_USAGE_FLOOR and p.scores.projection < TOP_HALF:
            sneaky.append(_entry(p, USAGE_RISE, player_above))
    return sorted(sneaky, key=_sneaky_key)


def _stashes(players: list[WaiverPlayer], inputs: BucketInputs,
             above_by_player: dict[str, PlayerAbove]) -> list[WaiverPlayer]:
    """The pool players out now with a return week inside the season and a top-half projection at the position.

    The handcuffs are stashes too. A handcuff is an RB one slot below a healthy starter whose rest of season
    projection is in the top half of every RB, rostered or not. A stash needs a rest of season projection above
    0, because a tie at 0 ranks every player at the top of his position.
    """
    starter_scores = _rb_scores(inputs) if inputs.slow is not None and inputs.slow.depth_charts else {}
    stashes = []
    for p in players:
        if p.position not in BUCKET_POSITIONS or p.ros_projection <= 0:
            continue
        player_above = above_by_player.get(p.player_id)
        if (p.injury_status in OUT_STATUSES and back_inside(p.return_week, inputs.week, inputs.client.settings.last_season_week)
                and p.scores.projection >= TOP_HALF):
            stashes.append(_entry(p, RETURN, player_above))
        elif (p.position == "RB" and player_above is not None and player_above.starter
              and player_above.status not in OUT_STATUSES
              and starter_scores.get(player_above.player_id, 0.0) >= TOP_HALF):
            stashes.append(_entry(p, HANDCUFF, player_above))
    return sorted(stashes, key=_stash_key)


def _rb_scores(inputs: BucketInputs) -> dict[str, float]:
    """The rank score of the rest of season projection of every RB with a team, rostered or not."""
    rbs = {pid: "RB" for pid, entry in inputs.sleeper_players.items()
           if (entry or {}).get("position") == "RB" and entry.get("team")}
    return rank_scores(rbs, {pid: inputs.ros_of(pid) for pid in rbs})


def return_week(player_id: str, gsis: str | None, week: int, returns: dict[str, int],
                injuries: dict[str, dict[int, str]] | None) -> int | None:
    """The week the player is back: the returns file first, the injury report second. None when neither knows.

    The injury report has no return field. Its first week after `week` with a status that does not keep him out
    is the return week, so it gives one only once the report of a later week is out.
    """
    if player_id in returns:
        return returns[player_id]
    reported = (injuries or {}).get(gsis or "", {})
    return next((w for w in sorted(reported) if w > week and reported[w] not in OUT_STATUSES), None)


def _entry(p: WaiverPlayer, reason: str, player_above: PlayerAbove | None) -> WaiverPlayer:
    """The bucket entry of `p` with his reason, and the story fact when the player above him is out."""
    facts = p.facts
    if player_above is not None and player_above.status in OUT_STATUSES:
        facts = [*facts, _story_fact(p, player_above)]
    return p.model_copy(update={"reason": reason, "facts": facts})


def _story_fact(p: WaiverPlayer, player_above: PlayerAbove) -> Fact:
    """The injury story of a player behind an injured starter. The text holds two names and no number."""
    text = f"{player_above.name} is {STATUS_WORDS[player_above.status]}, and {p.name} is next on the depth chart."
    return fact(f"WV.story.{p.player_id}", text, Nums(), [], [p.name, player_above.name])


def _players_above(players: list[WaiverPlayer], inputs: BucketInputs) -> dict[str, PlayerAbove]:
    """The player one slot above each pool player on his team's depth chart at his position.

    The chart lists gsis_ids, so the Sleeper players file and the id map join them to Sleeper IDs. A player first
    on his chart, or not on it, has no entry.
    """
    if inputs.slow is None or inputs.slow.depth_charts is None:
        return {}
    sleeper_players = inputs.sleeper_players
    sleeper_of = {g: pid for pid in sorted(sleeper_players) if (g := inputs.gsis_of(pid))}
    above_by_player = {}
    for p in players:
        chart = inputs.slow.depth_charts.get(p.team, {}).get(p.position, [])
        own_gsis = inputs.gsis_of(p.player_id)
        if own_gsis not in chart or chart.index(own_gsis) == 0:
            continue
        slot_above = chart.index(own_gsis) - 1
        above_id = sleeper_of.get(chart[slot_above])
        if above_id is not None:
            entry = sleeper_players[above_id]
            above_by_player[p.player_id] = PlayerAbove(above_id, player_name(above_id, entry),
                                                       entry.get("injury_status"), starter=slot_above == 0)
    return above_by_player


def _stash_key(p: WaiverPlayer) -> tuple[float, str]:
    """The higher rest of season projection first, then the player ID, so a tie has one order."""
    return -p.ros_projection, p.player_id


def _sneaky_key(p: WaiverPlayer) -> tuple[float, float, str]:
    """The best usage score first, then the higher rest of season projection, then the player ID, for one order."""
    return -p.scores.usage, -p.ros_projection, p.player_id
