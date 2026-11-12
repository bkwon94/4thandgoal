"""
The transaction feed of a free answer: the moves of one week from the Sleeper transactions, newest first, with the
count of the moves of each day, as a data tool result and as the block that code builds from the same moves.
"""
import json
from collections import Counter
from datetime import UTC, datetime, timedelta

from cornerstone_api.free_tools import SeasonData, _team
from league.paths import history_raw_dir, history_week_dir
from league.provider.raw import RawTransaction
from league.provider.sleeper import read_prev_transactions

# The Sleeper kinds of a move. A commissioner edit is not a move, and a failed claim never happened.
MOVE_KINDS = ("trade", "waiver", "free_agent")
# The rows of the block. A busy week holds about 40 moves, and a phone card shows the newest; the strip counts them all.
ROWS_MAX = 20

# What each field of a move means, in the tool result, so Claude and the check read the same meaning.
FEED_MEANINGS = {
    "week": "The fantasy week of the moves. The live week is the week now in play, which \"this week\" means.",
    "moves_per_day": "The count of the moves on each day of the week, oldest day first, in the time zone of the league.",
    "moves": "Each move of the week, newest first. `kind` is \"trade\", \"waiver\" for a waiver claim with its FAAB "
             "`bid`, or \"free_agent\" for a free agent add or a drop with no claim. A trade gives each team in "
             "`sides` with the players and the picks that it `got`. Another move gives its `team`, the players it "
             "`added`, and the players it `dropped`.",
}


def _when(transaction: RawTransaction, data: SeasonData) -> datetime:
    """The time the move went through: Sleeper sets `status_updated` when a claim runs, else the time it was made."""
    epoch_ms = (transaction.model_extra or {}).get("status_updated") or transaction.created
    return datetime.fromtimestamp(epoch_ms / 1000, tz=UTC).astimezone(data.tz)


def _day(moment: datetime) -> str:
    return moment.strftime("%a %b ") + str(moment.day)


def _row(transaction: RawTransaction, data: SeasonData) -> dict:
    """One move as one row of the feed."""
    day = _day(_when(transaction, data))
    adds, drops = transaction.adds or {}, transaction.drops or {}
    if transaction.type == "trade":
        picks = transaction.draft_picks or []
        return {"kind": "trade", "day": day, "sides": [
            {"team": _team(data, rid),
             "got": [data.name(pid) for pid, to in adds.items() if to == rid]
                    + [f"{pick['season']} round {pick['round']} pick" for pick in picks if pick.get("owner_id") == rid]}
            for rid in transaction.roster_ids]}
    row = {"kind": transaction.type, "day": day, "team": _team(data, transaction.roster_ids[0]),
           "added": [data.name(pid) for pid in adds], "dropped": [data.name(pid) for pid in drops]}
    if transaction.type == "waiver":
        row["bid"] = transaction.settings.waiver_bid if transaction.settings else None
    return row


def _saved_transactions(data: SeasonData, week: int) -> list[RawTransaction] | None:
    """The saved transactions of a past week: the full leg that the fetch of the next week saved, else the copy of the
    week. None when neither is saved."""
    fresh = read_prev_transactions(history_raw_dir(data.history_root, week + 1))
    if fresh is not None:
        return fresh
    path = history_week_dir(data.history_root, week) / "transactions.json"
    if not path.exists():
        return None
    return [RawTransaction.model_validate(t) for t in json.loads(path.read_text(encoding="utf-8"))]


def moves_feed(data: SeasonData, week: int | None = None) -> dict:
    """The moves of `week`, or of the live week for None, newest first with the count of each day, and the feed block
    of the same moves under `block`."""
    raw = data.raw()
    live = raw.state.display_week
    week = live if week is None else week
    transactions = raw.transactions if week == live else _saved_transactions(data, week)
    if transactions is None:
        return {"error": f"Week {week} has no saved moves. The live week is week {live}."}
    moves = sorted((t for t in transactions if t.status == "complete" and t.type in MOVE_KINDS),
                   key=lambda t: _when(t, data), reverse=True)
    rows = [_row(t, data) for t in moves]
    days = _days([_when(t, data) for t in moves])
    block = {"kind": "feed", "title": f"Week {week} moves", "days": days, "rows": rows[:ROWS_MAX],
             "more": max(0, len(rows) - ROWS_MAX)}
    return {"week": week, "live_week": week == live, "what_each_field_means": FEED_MEANINGS,
            "moves_per_day": days, "moves": rows, "block": block}


def _days(moments: list[datetime]) -> list[dict]:
    """The count of the moves of each day from the first move to the last, oldest first. A day with no move counts 0,
    so the strip keeps the gaps of the week."""
    if not moments:
        return []
    counts = Counter(moment.date() for moment in moments)
    first, last = min(counts), max(counts)
    span = [first + timedelta(days=offset) for offset in range((last - first).days + 1)]
    return [{"day": _day(datetime(d.year, d.month, d.day)), "moves": counts[d]} for d in span]
