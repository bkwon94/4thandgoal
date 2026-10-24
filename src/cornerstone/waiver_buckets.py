"""
The sneaky and stash buckets of the waiver board, each entry with the code of the rule that put him there.
Pure code over the scored pool, the depth charts, the injury report, and the returns file.
"""
from typing import NamedTuple

from cornerstone.adjusters import OUT_STATUSES
from cornerstone.models import Fact, WaiverPlayer
from cornerstone.nflverse import gsis_id
from cornerstone.parse import player_name
from cornerstone.sheet import Nums, fact
from cornerstone.slow_sources import SlowSources
from cornerstone.tunables import BUCKET_POSITIONS, SNEAKY_USAGE_FLOOR, TOP_HALF

SNEAKY = "sneaky"
STASHES = "stashes"
# The bucket reasons. The site says which rule put a player in a bucket from these codes.
USAGE_RISE = "usage_rise"
BEHIND_INJURY = "behind_injury"

# The words of the story fact for each status of OUT_STATUSES: "{starter} is {word}".
STATUS_WORDS = {"Out": "out", "IR": "on IR", "PUP": "on the PUP list", "Sus": "suspended", "NA": "not active"}


class Above(NamedTuple):
    """The player one depth chart slot above a pool player, with his Sleeper injury status."""
    player_id: str
    name: str
    status: str | None


def sneaky_and_stashes(
    players: list[WaiverPlayer], best_adds: list[WaiverPlayer], raw: dict[str, object], slow: SlowSources | None,
) -> dict[str, list[WaiverPlayer]]:
    """The sneaky and the stash candidates in rank order, each with his reason. The engine applies the bucket cap.

    A player in best adds is not sneaky. With no depth chart, no player is behind an injury.
    """
    above = _slots_above(players, raw, slow)
    taken = {p.player_id for p in best_adds}
    sneaky = []
    for p in players:
        if p.position not in BUCKET_POSITIONS or p.player_id in taken:
            continue
        up = above.get(p.player_id)
        # The injury is the story of a usage rise too, so behind_injury wins when both rules hold.
        if up is not None and up.status in OUT_STATUSES:
            sneaky.append(_entry(p, BEHIND_INJURY, up))
        elif p.scores.usage >= SNEAKY_USAGE_FLOOR and p.scores.projection < TOP_HALF:
            sneaky.append(_entry(p, USAGE_RISE, up))
    return {SNEAKY: sorted(sneaky, key=_sneaky_key), STASHES: []}


def _entry(p: WaiverPlayer, reason: str, up: Above | None) -> WaiverPlayer:
    """The bucket entry of `p` with his reason, and the story fact when the player above him is out."""
    facts = p.facts if up is None or up.status not in OUT_STATUSES else [*p.facts, _story_fact(p, up)]
    return p.model_copy(update={"reason": reason, "facts": facts})


def _story_fact(p: WaiverPlayer, up: Above) -> Fact:
    """The injury story of a player behind an injured starter. The text holds two names and no number."""
    text = f"{up.name} is {STATUS_WORDS[up.status]}, and {p.name} is next on the depth chart."
    return fact(f"WV.story.{p.player_id}", text, Nums(), [], [p.name, up.name])


def _slots_above(players: list[WaiverPlayer], raw: dict[str, object], slow: SlowSources | None) -> dict[str, Above]:
    """The player one slot above each pool player on his team's depth chart at his position.

    The chart lists gsis_ids, so the Sleeper blob and the id map join them to Sleeper IDs. A player first on
    his chart, or not on it, has no entry.
    """
    if slow is None or slow.depth_charts is None:
        return {}
    blob = raw["players"]
    id_map = slow.id_map or {}
    sleeper_of = {g: pid for pid in sorted(blob) if (g := gsis_id(pid, blob, id_map))}
    out = {}
    for p in players:
        chart = slow.depth_charts.get(p.team, {}).get(p.position, [])
        mine = gsis_id(p.player_id, blob, id_map)
        if mine not in chart or chart.index(mine) == 0:
            continue
        up_id = sleeper_of.get(chart[chart.index(mine) - 1])
        if up_id is not None:
            out[p.player_id] = Above(up_id, player_name(up_id, blob[up_id]), blob[up_id].get("injury_status"))
    return out


def _sneaky_key(p: WaiverPlayer) -> tuple[float, float, str]:
    """The best usage score first, then the higher rest of season projection, then the player ID, so a tie has one order."""
    return -p.scores.usage, -p.ros_projection, p.player_id
