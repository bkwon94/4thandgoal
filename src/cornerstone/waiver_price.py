"""
The waiver price: the bid to win of each player, the last like him, and the outbid counts per budget level.
Pure code over the raw files and the bid history of the season, so the same inputs give the same price.
"""
import json
from pathlib import Path

from cornerstone.history import history_dir
from cornerstone.models import WaiverClaim

# Sleeper marks a claim that won as complete and a claim that lost as failed.
CLAIM_RESULTS = {"complete": True, "failed": False}


def bid_history(root: Path, raw: dict[str, object], week: int) -> list[WaiverClaim]:
    """Every waiver claim of weeks 1 to `week`: the saved history before `week`, and the raw files of `week`."""
    positions = {pid: entry.get("position") for pid, entry in raw["players"].items()}
    claims = []
    for past in range(1, week):
        path = history_dir(root, past) / "transactions.json"
        # A week that is not saved has no claims, so a gap lowers the floor and never makes a claim wrong.
        if path.exists():
            claims += _claims(json.loads(path.read_text()), positions)
    return claims + _claims(raw["transactions"], positions)


def _claims(transactions: list[dict], positions: dict[str, str | None]) -> list[WaiverClaim]:
    return [
        WaiverClaim(
            player_id=player_id,
            roster_id=roster_id,
            position=positions.get(player_id),
            week=t["leg"],
            # A claim with no bid set is a $0 claim.
            bid=(t.get("settings") or {}).get("waiver_bid") or 0,
            won=CLAIM_RESULTS[t["status"]],
        )
        for t in transactions
        if t["type"] == "waiver" and t["status"] in CLAIM_RESULTS
        for player_id, roster_id in (t["adds"] or {}).items()
    ]
