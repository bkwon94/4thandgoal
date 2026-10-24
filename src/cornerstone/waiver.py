"""
The waiver board engine: it ranks the waiver pool into buckets and builds the budget table of the league.
Pure code: no network and no Claude, so the same raw data gives the same board.
"""
from collections.abc import Sequence
from datetime import datetime
from typing import NamedTuple

from cornerstone.history import _round_half_up
from cornerstone.models import (
    BoardScores, BudgetRow, Fact, NflverseWeek, TeamWeek, UsageWeek, WaiverBoard, WaiverClaim, WaiverPlayer, r2,
)
from cornerstone.parse import player_name
from cornerstone.sheet import Nums, fact
from cornerstone.tunables import (
    BOARD_WEIGHTS, BUCKET_POSITIONS, BUCKET_SIZE, LAST_SEASON_WEEK, PER_POSITION, POOL_POSITIONS, USAGE_WEEKS,
)

# The positions of the pool are POOL_POSITIONS. The Sleeper fetch asks for the same positions. A player at
# another position, such as a linebacker, is never in the pool.
BEST_ADDS = "best_adds"
TRENDING = "trending"


def waiver_board(
    raw: dict[str, object], week: int, built: datetime, nfl: NflverseWeek | None = None,
    claims: Sequence[WaiverClaim] = (),
) -> WaiverBoard:
    """The board after week `week` from the raw files of the week. `built` is the build time the file shows.

    `nfl` gives the usage and the environment. None, or an extract with no usage, gives every player a usage
    score and an environment score of 0. `claims` is the bid history of the season, the input of the price
    floor and the last like him.
    """
    ahead = {entry["week"]: entry["projections"] for entry in raw.get("projections_ahead", [])}
    rostered = _rostered(raw)
    pool = {pid: entry for pid, entry in sorted(raw["players"].items()) if _in_pool(entry, rostered, pid)}
    # A week with no projection for the player, such as his bye, counts 0.
    ros = {pid: r2(sum(ahead.get(w, {}).get(pid, 0.0) for w in range(week + 1, LAST_SEASON_WEEK + 1)))
           for pid in pool}
    positions = {pid: entry["position"] for pid, entry in pool.items()}
    projection = _rank_scores(positions, ros)
    usage_rows = (nfl.usage if nfl else None) or {}
    usage = _usage_scores(positions, usage_rows, week)
    teams = _team_ranks(_team_rates((nfl.environment if nfl else None) or {}, week))
    players = [
        _pool_player(pid, entry, r2(ahead.get(week + 1, {}).get(pid, 0.0)), ros[pid],
                     BoardScores(usage=usage.get(pid, 0.0), environment=_environment_score(entry, teams),
                                 projection=projection[pid]))
        for pid, entry in pool.items()
    ]
    for p in players:
        if p.position in BUCKET_POSITIONS:
            p.facts = [*p.facts, *_player_facts(p, usage_rows.get(p.player_id, []), teams, week)]
    players = _with_trending(players, _trending_counts(raw))
    best_adds = _capped(sorted((p for p in players if p.position in BUCKET_POSITIONS), key=_rank_key))
    # The import waits for the call: waiver_price reads the history module, and the history module reaches this
    # module through the Sleeper fetch, so a top-level import is a cycle.
    from cornerstone.waiver_price import price_players

    buckets = {BEST_ADDS: best_adds, TRENDING: _trending_bucket(players)}
    # Every bucket but drops carries a price, so the drops bucket stays out of this step once it exists.
    buckets = {key: price_players(bucket, raw, list(claims)) for key, bucket in buckets.items()}
    return WaiverBoard(week=week, built=built, buckets=buckets, budgets=_budgets(raw))


def _budgets(raw: dict[str, object]) -> list[BudgetRow]:
    """One row per roster in roster order: the league budget minus the budget used, and the waiver position."""
    budget = raw["league"]["settings"]["waiver_budget"]
    return [
        BudgetRow(
            roster_id=roster["roster_id"],
            budget_left=budget - roster["settings"]["waiver_budget_used"],
            waiver_order=roster["settings"]["waiver_position"],
        )
        for roster in sorted(raw["rosters"], key=lambda r: r["roster_id"])
    ]


def _rostered(raw: dict[str, object]) -> set[str]:
    # A roster with no players has None in rosters.json.
    return {pid for roster in raw["rosters"] for pid in roster.get("players") or []}


def _in_pool(entry: dict, rostered: set[str], player_id: str) -> bool:
    """A player with a team, active, at a pool position, and on no roster in the league."""
    if player_id in rostered or not entry.get("team") or entry.get("position") not in POOL_POSITIONS:
        return False
    # Sleeper gives a defense no status, only the active flag.
    if entry["position"] == "DEF":
        return entry.get("active") is True
    return entry.get("status") == "Active"


def _rank_scores(positions: dict[str, str], values: dict[str, float]) -> dict[str, float]:
    """The rank score of each key: the rank of its value inside its group, from 1 for the highest to 0.

    The group is the position for a player and one group for every team. Keys with the same value share the
    better rank.
    """
    by_position: dict[str, list[float]] = {}
    for pid, position in positions.items():
        by_position.setdefault(position, []).append(values[pid])
    for ranked in by_position.values():
        ranked.sort(reverse=True)
    scores = {}
    for pid, position in positions.items():
        ranked = by_position[position]
        ahead_of = ranked.index(values[pid])
        scores[pid] = 1.0 if len(ranked) == 1 else round(1 - ahead_of / (len(ranked) - 1), 4)
    return scores


def _pool_player(player_id: str, entry: dict, week_projection: float, ros: float, scores: BoardScores) -> WaiverPlayer:
    return WaiverPlayer(
        player_id=player_id,
        name=player_name(player_id, entry),
        position=entry["position"],
        team=entry["team"],
        week_projection=week_projection,
        ros_projection=ros,
        scores=scores,
        board_score=round(sum(weight * getattr(scores, key) for key, weight in BOARD_WEIGHTS.items()), 4),
    )


def _capped(ranked: list[WaiverPlayer]) -> list[WaiverPlayer]:
    """The first BUCKET_SIZE players of `ranked`, with at most PER_POSITION of one position."""
    bucket: list[WaiverPlayer] = []
    taken: dict[str, int] = {}
    for p in ranked:
        if len(bucket) == BUCKET_SIZE:
            break
        if taken.get(p.position, 0) < PER_POSITION:
            bucket.append(p)
            taken[p.position] = taken.get(p.position, 0) + 1
    return bucket


def _rank_key(p: WaiverPlayer) -> tuple[float, float, str]:
    """Best board score first, then the higher rest of season projection, then the player ID, so a tie has one order."""
    return -p.board_score, -p.ros_projection, p.player_id


def _trending_counts(raw: dict[str, object]) -> dict[str, int]:
    """The trending count of each player in the trending file. A week with no file has no counts."""
    return {row["player_id"]: row["count"] for row in raw.get("trending", [])}


def _with_trending(players: list[WaiverPlayer], counts: dict[str, int]) -> list[WaiverPlayer]:
    """The players with the trending count of each. A player with no count keeps 0."""
    out = []
    for p in players:
        count = counts.get(p.player_id)
        out.append(p if count is None else
                   p.model_copy(update={"trending_count": count, "facts": [*p.facts, _trending_fact(p, count)]}))
    return out


def _trending_fact(p: WaiverPlayer, count: int) -> Fact:
    """The count fact of a trending player. The count is written plain, as a comma would split it into two numbers."""
    # The sheet module imports the Sleeper client, which imports this module, so the fact skips its Nums helper.
    # The one number goes into the text and the numbers from the same string.
    number = str(count)
    text = f"{p.name} was added in {number} Sleeper leagues in the last day."
    return Fact(id=f"WV.trending.{p.player_id}", text=text, numbers=[number], teams=[], players=[p.name])


def _trending_bucket(players: list[WaiverPlayer]) -> list[WaiverPlayer]:
    """The pool players at a bucket position with a trending count, in the order of _trending_key."""
    return _capped(sorted((p for p in players if p.trending_count and p.position in BUCKET_POSITIONS),
                          key=_trending_key))


def _trending_key(p: WaiverPlayer) -> tuple[int, str]:
    """The most adds first, then the player ID, so a tie has one order."""
    return -p.trending_count, p.player_id


def _usage_window(rows: list[UsageWeek], week: int) -> tuple[UsageWeek, UsageWeek] | None:
    """The usage of the first and the last week of the USAGE_WEEKS weeks up to `week`.

    None when either week has no row or no snap share, such as a rookie's first week or a bye.
    """
    by_week = {u.week: u for u in rows if u.snap_share is not None}
    before, last = by_week.get(week - USAGE_WEEKS + 1), by_week.get(week)
    return (before, last) if before and last else None


class PositionKinds(NamedTuple):
    """The touch and the second environment rank that count for one position. The first environment rank is pace."""
    # The UsageWeek count field. It is also the word of the usage fact.
    touch: str
    # The UsageWeek share field of the touch.
    touch_share: str
    # The TeamRanks field of the second environment rank, and the TeamRates field of the environment fact.
    environment: str
    rate: str


# A WR or a TE earns targets and gains from passes. An RB earns carries and gains from runs that work.
# A QB earns carries, as his targets are near none, and gains from passes.
POSITION_KINDS = {
    "QB": PositionKinds("carries", "carry_share", "neutral_pass", "neutral_pass_rate"),
    "RB": PositionKinds("carries", "carry_share", "rush_success", "rush_success"),
    "WR": PositionKinds("targets", "target_share", "neutral_pass", "neutral_pass_rate"),
    "TE": PositionKinds("targets", "target_share", "neutral_pass", "neutral_pass_rate"),
}


def _opportunities(position: str, u: UsageWeek) -> tuple[int, int, str]:
    """The count, the share, and the word of the touches that count for the position."""
    kinds = POSITION_KINDS[position]
    return getattr(u, kinds.touch), getattr(u, kinds.touch_share), kinds.touch


def _usage_scores(positions: dict[str, str], usage: dict[str, list[UsageWeek]], week: int) -> dict[str, float]:
    """The usage score of each player whose usage rose: his rise ranked inside the position, from 1 to 0.

    The rise is the change in snap share plus the change in the share of his touches over the window. A
    player with a flat or a falling usage, or with no window, is not in the result, so his score stays 0.
    """
    rises = {}
    for pid, position in positions.items():
        window = _usage_window(usage.get(pid, []), week)
        if window is None or position not in BUCKET_POSITIONS:
            continue
        before, last = window
        rise = (last.snap_share - before.snap_share
                + _opportunities(position, last)[1] - _opportunities(position, before)[1])
        if rise > 0:
            rises[pid] = rise
    return _rank_scores({pid: positions[pid] for pid in rises}, rises)


class TeamRates(NamedTuple):
    """The season rates of one offense, from week 1 to the board's week. A rate is a fraction."""
    plays_per_game: float
    neutral_pass_rate: float
    rush_success: float


class TeamRanks(NamedTuple):
    """The rates of one offense and its rank score in each, from 1 for the best offense to 0, plus its pace place."""
    rates: TeamRates
    pace: float
    neutral_pass: float
    rush_success: float
    # 1 for the offense with the most plays per game. The environment fact names it.
    pace_place: int


def _team_rates(environment: dict[str, list[TeamWeek]], week: int) -> dict[str, TeamRates]:
    """The season rates of each team with a game up to `week`. A bye week has no row, so it is not a game."""
    rates = {}
    for team, weeks in environment.items():
        played = [w for w in weeks if w.week <= week]
        if not played:
            continue
        neutral = sum(w.neutral_plays for w in played)
        rushes = sum(w.rushes for w in played)
        rates[team] = TeamRates(
            plays_per_game=sum(w.plays for w in played) / len(played),
            neutral_pass_rate=sum(w.neutral_passes for w in played) / neutral if neutral else 0.0,
            rush_success=sum(w.rush_successes for w in played) / rushes if rushes else 0.0)
    return rates


def _team_ranks(rates: dict[str, TeamRates]) -> dict[str, TeamRanks]:
    every = dict.fromkeys(rates, "NFL")
    pace = _rank_scores(every, {t: r.plays_per_game for t, r in rates.items()})
    neutral = _rank_scores(every, {t: r.neutral_pass_rate for t, r in rates.items()})
    rush = _rank_scores(every, {t: r.rush_success for t, r in rates.items()})
    faster = sorted((r.plays_per_game for r in rates.values()), reverse=True)
    return {t: TeamRanks(rates=r, pace=pace[t], neutral_pass=neutral[t], rush_success=rush[t],
                         pace_place=faster.index(r.plays_per_game) + 1)
            for t, r in rates.items()}


def _environment_score(entry: dict, teams: dict[str, TeamRanks]) -> float:
    """The mean of two team rank scores: pace and the second rank of POSITION_KINDS for the position.

    A kicker, a defense, or a team with no environment gets 0.
    """
    ranks = teams.get(entry["team"])
    if ranks is None or entry["position"] not in BUCKET_POSITIONS:
        return 0.0
    return round((ranks.pace + getattr(ranks, POSITION_KINDS[entry["position"]].environment)) / 2, 4)


def _percent(fraction: float) -> int:
    """The fraction as a whole percent, rounded half up as every number on the page."""
    return int(_round_half_up(100 * fraction))


def _player_facts(p: WaiverPlayer, rows: list[UsageWeek], teams: dict[str, TeamRanks], week: int) -> list[Fact]:
    """The usage fact and the environment fact of a QB, RB, WR, or TE. Each one drops when its input is missing."""
    facts = []
    window = _usage_window(rows, week)
    if window is not None:
        before, last = window
        n = Nums()
        count, _, word = _opportunities(p.position, last)
        before_count = _opportunities(p.position, before)[0]
        if last.snap_share == before.snap_share:
            direction = "level with"
        else:
            direction = "up from" if last.snap_share > before.snap_share else "down from"
        text = (f"{p.name} played {n(last.snap_share)}% of snaps and took {n(count)} {word} last week, "
                f"{direction} {n(before.snap_share)}% and {n(before_count)}.")
        facts.append(fact(f"W.usage.{p.player_id}", text, n, [], [p.name]))
    ranks = teams.get(p.team)
    if ranks is not None:
        n = Nums()
        kinds = POSITION_KINDS[p.position]
        rate = n(_percent(getattr(ranks.rates, kinds.rate)))
        text = f"{p.team} runs the {n.ord(ranks.pace_place)} fastest offense and "
        if kinds.environment == "rush_success":
            text += f"succeeds on {rate}% of runs."
        else:
            text += f"passes on {rate}% of neutral downs."
        facts.append(fact(f"W.env.{p.player_id}", text, n, [], [p.name]))
    return facts
