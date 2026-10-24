"""
The sneaky and stash buckets of the waiver board, each entry with the code of the rule that put him there.
Pure code over the scored pool, the depth charts, the injury report, and the returns file.
"""
from cornerstone.models import WaiverPlayer
from cornerstone.tunables import BUCKET_POSITIONS, SNEAKY_USAGE_FLOOR, TOP_HALF

SNEAKY = "sneaky"
STASHES = "stashes"
# The bucket reasons. The site says which rule put a player in a bucket from these codes.
USAGE_RISE = "usage_rise"


def sneaky_and_stashes(players: list[WaiverPlayer], best_adds: list[WaiverPlayer]) -> dict[str, list[WaiverPlayer]]:
    """The sneaky and the stash candidates in rank order, each with his reason. The engine applies the bucket cap.

    A player in best adds is not sneaky.
    """
    taken = {p.player_id for p in best_adds}
    sneaky = []
    for p in players:
        if p.position not in BUCKET_POSITIONS or p.player_id in taken:
            continue
        if p.scores.usage >= SNEAKY_USAGE_FLOOR and p.scores.projection < TOP_HALF:
            sneaky.append(p.model_copy(update={"reason": USAGE_RISE}))
    return {SNEAKY: sorted(sneaky, key=_sneaky_key), STASHES: []}


def _sneaky_key(p: WaiverPlayer) -> tuple[float, float, str]:
    """The best usage score first, then the higher rest of season projection, then the player ID, so a tie has one order."""
    return -p.scores.usage, -p.ros_projection, p.player_id
