"""
The NFL team facts of the sheet: the offense of the NFL team of each traded player, from the nflverse team stats.
A player on a bad offense is not a safe start, so the Advisor reads this fact beside his own numbers.
"""
from analyzer.trade import ProposedTrade
from facts.tokens import Nums, fact
from league.models import Fact
from league.nfl_teams import team_name
from league.numbers import plural
from league.snapshot import Snapshot

# The positions that start on an offense. A defense or a kicker does not rise or fall with its offense.
OFFENSE_POSITIONS = ("QB", "RB", "WR", "TE")
# The text shows expected points per 100 plays, because per play the number is a hundredth and reads as zero.
PLAYS = 100


def _team_fact(snapshot: Snapshot, pid: str) -> Fact | None:
    """The offense of the NFL team of a player, or None when he has no team or the team has no stats."""
    player = snapshot.players[pid]
    offense = (snapshot.team_stats or {}).get(player.nfl_team or "")
    if player.position not in OFFENSE_POSITIONS or offense is None:
        return None
    n = Nums()
    text = (f"{player.name}'s NFL team, the {team_name(player.nfl_team)}, ranks {n.ord(offense.rank)} of "
            f"{n(len(snapshot.team_stats))} on offense: {n(PLAYS * offense.epa_per_play)} expected points added per "
            f"{n(PLAYS)} plays over {n(offense.games)} {plural(offense.games, 'game', 'games')} before the trade.")
    return fact(f"{pid}.nfl_team", text, n, [], [player.name])


def nfl_team_facts(trade: ProposedTrade, snapshot: Snapshot) -> list[Fact]:
    """One fact for each traded player on an offense team that the team stats file lists."""
    return [f for pid in trade.player_ids if (f := _team_fact(snapshot, pid)) is not None]
