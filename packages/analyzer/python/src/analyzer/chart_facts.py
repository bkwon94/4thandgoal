"""
The chart facts of the sheet: the chart value of each traded player as one fact, and one fact when the week has no chart.
The chart is a market price that informs the read and never gates it.
"""
from analyzer.trade import ProposedTrade
from facts.tokens import Nums, fact
from league.models import Fact
from league.snapshot import Snapshot


def _value_fact(snapshot: Snapshot, pid: str) -> Fact:
    """The place and the chart value of a traded player, or the plain statement that he is not on the chart.

    A player off the chart stays in play: a waiver pickup can be traded, so the fact says so and nothing more.
    A tap on a Bullet shows this text on the page, so it says the place on the chart in plain words and never an
    inner word such as "trade value".
    """
    n = Nums()
    name = snapshot.players[pid].name
    values = snapshot.chart.values
    if pid in values:
        # The place counts every player on the chart, over all positions, with a higher value.
        place = 1 + sum(1 for v in values.values() if v > values[pid])
        text = f"{name} is {n.ord(place)} on the chart of week {n(snapshot.chart.week)}, at {n(values[pid])}."
    else:
        text = f"{name} is not on the chart of week {n(snapshot.chart.week)}."
    return fact(f"{pid}.value", text, n, [], [name])


def chart_facts(trade: ProposedTrade, snapshot: Snapshot) -> list[Fact]:
    """One fact for each traded player. With no chart for the week, one fact that says the chart is missing."""
    if snapshot.chart is None:
        n = Nums()
        text = f"The chart of week {n(snapshot.week)} is missing, so no player has a chart value."
        return [fact("trade.chart", text, n, [], [])]
    return [_value_fact(snapshot, pid) for pid in trade.player_ids]
