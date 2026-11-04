"""
Builds the odds facts, the power facts, and the facts that explain each rank.
The rankings chapter reads them, and the chapter itself comes from here.
"""
from collections.abc import Callable

from cornerstone.client import Client
from cornerstone.facts_league import (
    head_to_head,
)
from cornerstone.models import (
    Chapter,
    Fact,
    History,
    OddsResult,
    PowerRow,
    Standing,
)
from cornerstone.numbers import round_half_up
from cornerstone.power_rankings import power_rankings
from cornerstone.sheet.base import RANKINGS_CHAPTER, Context, Nums, fact, sentence_range
from cornerstone.tunables import SWING_FLAT, TREND_WEEKS, WHY_MOVE_AT, WHY_ODDS_AT

# The form component is a streak, a record, and an all-play rate. The word "results" keeps the writer from
# reading it as scoring, which the .trend fact covers.
COMPONENT_WORDS = {
    "standing": "standing", "form": f"results over the last {TREND_WEEKS} weeks", "schedule_played": "schedule played",
    "scoring": "scoring",
}


def facts(context: Context, client: Client) -> list[Fact]:
    """The power ranks, the odds, the swing of each Must Watch game, and the reasons for the ranks and the odds.

    The rankings chapter reads them. The median chapter reads the odds, and the next week chapter reads the swings.
    """
    return (
        power_facts(context.power, context.team)
        + rank_why_facts(context.history, context.power, context.before, context.team)
        + odds_facts(context.odds, context.team)
        + swing_facts(context.odds, [(nx.a, nx.b) for nx in context.next if nx.must_watch], context.team)
        + odds_why_facts(context.odds, context.season_scores, context.projected, context.remaining, context.team)
    )


def odds_facts(odds: OddsResult | None, team: Callable[[int], str]) -> list[Fact]:
    """One fact per team: the playoff odds, the bye odds, and the most likely seed, or the clinch or the out.

    The numbers are the engine's as given. The sheet computes none of them.
    """
    if odds is None:
        return []
    out = []
    for rid, t in odds.teams.items():
        n = Nums()
        name = team(rid)
        if t.status == "in":
            text = f"{name} has clinched a playoff spot."
        elif t.status == "out":
            text = f"{name} is out of the playoff race."
        else:
            text = f"{name} makes the playoffs in about {n(t.playoff)}% of runs, with a bye in {n(t.bye)}%"
            # The engine gives no seed below SEED_SHOW_AT, so the clause drops there.
            text += f", most often as the {n.ord(t.seed)} seed." if t.seed is not None else "."
        out.append(fact(f"ODDS.{rid}", text, n, [name], []))
    return out


def odds_why_facts(
    odds: OddsResult | None,
    scores: dict[int, list[float]],
    projected: dict[int, dict[int, float]],
    remaining: dict[int, list[tuple[int, int]]],
    team: Callable[[int], str],
) -> list[Fact]:
    """One fact per team with projected totals: the projected pace, the season pace, and the remaining schedule.

    The inputs are the engine's own, so the why names what drives the odds. It exists only beside the odds facts.
    """
    if odds is None:
        return []
    # The schedule rank uses the exact paces. A rounded pace would tie teams that differ by a fraction.
    pace = {rid: sum(s) / len(s) for rid, s in scores.items() if s}
    faced: dict[int, list[float]] = {rid: [] for rid in scores}
    for pairs in remaining.values():
        for a, b in pairs:
            faced[a].append(pace[b])
            faced[b].append(pace[a])
    # Rank 1 is the easiest: the lowest mean pace of the opponents left. A tie goes to the lower roster ID.
    order = sorted((rid for rid in faced if faced[rid]), key=lambda rid: (sum(faced[rid]) / len(faced[rid]), rid))
    rank = {rid: i for i, rid in enumerate(order, 1)}
    out = []
    for rid in scores:
        ahead = list(projected.get(rid, {}).values())
        # A team with no projected totals has no projected pace, so the why has nothing to compare.
        if not ahead or rid not in pace or rid not in rank:
            continue
        n = Nums()
        name = team(rid)
        season = int(round_half_up(pace[rid]))
        # A pace read aloud as "eighty" or "eleven" takes "an", so the sentence reads right at any score.
        article = "an" if 80 <= season < 90 or season in (8, 11, 18) else "a"
        # The two ends read as words, so "1st easiest" and "12th easiest" never appear.
        if rank[rid] == 1:
            schedule = "the easiest"
        elif rank[rid] == len(order):
            schedule = "the hardest"
        else:
            schedule = f"the {n.ord(rank[rid])} easiest"
        text = (
            f"{name} projects {n(int(round_half_up(sum(ahead) / len(ahead))))} a week from here against "
            f"{article} {n(season)} pace, with {schedule} remaining schedule."
        )
        out.append(fact(f"ODDS.{rid}.why", text, n, [name], []))
    return out


def swing_facts(odds: OddsResult | None, pairs: list[tuple[int, int]], team: Callable[[int], str]) -> list[Fact]:
    """One fact per given next-week pair: each side's odds after a win and after a loss, in the pair order."""
    if odds is None:
        return []
    swings = {(s.a, s.b): s for s in odds.swings}

    def side(rid: int, win: int, loss: int, n: Nums) -> str:
        t = odds.teams[rid]
        # A clinched or out side cannot move, so its sentence holds no digit.
        if t.status != "open":
            return f"{team(rid)} is {t.status} either way."
        # A gap under SWING_FLAT is noise, so the side reads as flat.
        if abs(win - loss) < SWING_FLAT:
            return f"The playoff odds of {team(rid)} stay near {n(t.playoff)}% either way."
        # No possessive: a team name that ends in s, such as Bo Girds, breaks the "'s" form.
        return f"A win puts the playoff odds of {team(rid)} at {n(win)}%, a loss at {n(loss)}%."

    out = []
    for a, b in pairs:
        s = swings[(a, b)]
        n = Nums()
        text = f"{side(a, s.a_win, s.a_loss, n)} {side(b, s.b_win, s.b_loss, n)}"
        out.append(fact(f"SW.{a}v{b}", text, n, [team(a), team(b)], []))
    return out


def power_facts(rows: list[PowerRow], team: Callable[[int], str]) -> list[Fact]:
    """One fact per team: the power rank, the movement, the four component ranks as ordinals, and the form records.

    It takes the rows and a name lookup, not a Context, so a saved week can get the facts from its history.
    """
    out = []
    for row in rows:
        n = Nums()
        name = team(row.roster_id)
        rank = n.ord(row.power_rank)
        if row.movement is None:
            move = "the first week of the power rankings"
        elif row.movement == 0:
            move = "no move from last week"
        else:
            places = "place" if abs(row.movement) == 1 else "places"
            side = "up" if row.movement > 0 else "down"
            move = f"{side} {n(abs(row.movement))} {places} from last week"
        # A component word may hold a number, such as the 3 of "the last 3 weeks", so Nums records it too.
        components = ", ".join(
            f"{n.ord(row.ranks[key])} in {n.text(word)}" for key, word in COMPONENT_WORDS.items()
        )
        # The form component weighs both games of a week, so the fact names both records for the writer to quote.
        # Nums records each number in text order, so the records come before the count of weeks.
        head_to_head, median = n.record(*row.head_to_head), n.record(*row.median)
        window = "the last week" if row.form_weeks == 1 else f"the last {n(row.form_weeks)} weeks"
        records = f"{head_to_head} head-to-head and {median} at the median over {window}"
        text = f"{name} is {rank} in the power rankings, {move}: {components}; {records}."
        out.append(fact(f"PR.{row.roster_id}", text, n, [name], []))
    return out


def rank_why_facts(
    history: History | None, rows: list[PowerRow], before: dict[int, int], team: Callable[[int], str],
) -> list[Fact]:
    """One fact per team on why its power rank moved or held, from the second week of the rankings on.

    A mover names this week's head-to-head game and the component whose rank changed most since last week.
    A held team names its best and its worst component. Week 1 of the rankings has no last week, so no fact.
    `before` is the standing rank of each roster before this week. Like power_facts, it takes no Context,
    so a saved week can get the facts from its history.
    """
    if history is None or not rows or history.week < 2:
        return []
    w = history.week
    played = history.weeks[w]
    # Context keeps only week N of the rankings, so week N-1 comes from a second call on the same history.
    last = {row.roster_id: row for row in power_rankings(history, w - 1)[w - 1]}
    out = []
    for row in rows:
        n = Nums()
        name = team(row.roster_id)
        teams = [name]
        if not row.movement:
            # max and min keep the first of equal ranks, so a tie goes to the first in component order.
            best = min(COMPONENT_WORDS, key=lambda k: row.ranks[k])
            worst = max(COMPONENT_WORDS, key=lambda k: row.ranks[k])
            text = (
                f"{name} held {n.ord(row.power_rank)}: {n.text(COMPONENT_WORDS[best])} sits "
                f"{n.ord(row.ranks[best])}, {n.text(COMPONENT_WORDS[worst])} {n.ord(row.ranks[worst])}."
            )
        else:
            side = "up" if row.movement > 0 else "down"
            places = "place" if abs(row.movement) == 1 else "places"
            text = f"{name} moved {side} {n(abs(row.movement))} {places}"
            game = head_to_head(played, row.roster_id)
            # A bye week has no head-to-head game, so the text names no game.
            if game is not None:
                opponent_id, result = game
                opponent = team(opponent_id)
                teams.append(opponent)
                margin = round(abs(played.scores[row.roster_id] - played.scores[opponent_id]))
                # A margin under half a point rounds to 0, and "a 0-point win" reads as a tie.
                size = f"{n(margin)}-point" if margin else "narrow"
                if result == 0:
                    game_text = f"a tie with {opponent}"
                elif result > 0:
                    game_text = f"a {size} win over {opponent}"
                else:
                    game_text = f"a {size} loss to {opponent}"
                text += f" after {game_text}, the {n.ord(before[opponent_id])}-place team"
            last_ranks = last[row.roster_id].ranks
            key = max(COMPONENT_WORDS, key=lambda k: abs(last_ranks[k] - row.ranks[k]))
            # The power score can move while every component rank holds. The text then names no component.
            if last_ranks[key] != row.ranks[key]:
                verb = "rose" if row.ranks[key] < last_ranks[key] else "fell"
                text += (
                    f": {n.text(COMPONENT_WORDS[key])} {verb} from {n.ord(last_ranks[key])} "
                    f"to {n.ord(row.ranks[key])}"
                )
            text += "."
        out.append(fact(f"PR.{row.roster_id}.why", text, n, teams, []))
    return out


def standing_ranks(table: list[Standing]) -> dict[int, int]:
    """The standing rank of each roster, by roster ID. The sheet and a saved week both read it from here."""
    return {s.roster_id: s.rank for s in table}


def required_why_ids(
    facts: dict[str, Fact], rows: list[PowerRow], table: list[Standing], odds: OddsResult | None,
) -> list[str]:
    """The why facts the rankings writer must cite, in power rank order.

    A team that moved `WHY_MOVE_AT` or more places either way needs its rank why. A team whose record and odds
    disagree needs its odds why: under .500 with odds at or above `WHY_ODDS_AT`, or over .500 with odds under it.
    A team at .500 is neither under nor over. Only IDs in the facts go in.
    """
    record = {s.roster_id: (s.wins, s.losses) for s in table}
    ids = []
    for row in rows:
        rid = row.roster_id
        if row.movement is not None and abs(row.movement) >= WHY_MOVE_AT:
            ids.append(f"PR.{rid}.why")
        t = odds.teams.get(rid) if odds is not None else None
        wins, losses = record[rid]
        if t is not None and (
            (wins < losses and t.playoff >= WHY_ODDS_AT) or (wins > losses and t.playoff < WHY_ODDS_AT)
        ):
            ids.append(f"ODDS.{rid}.why")
    return [fid for fid in ids if fid in facts]


def rankings_chapter(
    facts: dict[str, Fact], rows: list[PowerRow], team: Callable[[int], str], table: list[Standing],
    odds: OddsResult | None, *, client: Client,
) -> Chapter:
    """The rankings chapter: every team in power rank order, each with its PR, standing, streak, and trend facts.

    The history cap does not apply here: the spec gives each team its own streak and trend facts.
    """
    standing_rank = standing_ranks(table)
    ids = [
        fid
        for row in rows
        for fid in (f"PR.{row.roster_id}", f"PR.{row.roster_id}.why", f"S.{standing_rank[row.roster_id]}",
                    f"H.{row.roster_id}.streak", f"H.{row.roster_id}.trend", f"ODDS.{row.roster_id}",
                    f"ODDS.{row.roster_id}.why")
    ]
    low, high = sentence_range(RANKINGS_CHAPTER, client)
    return Chapter(
        key=RANKINGS_CHAPTER,
        title="Power rankings",
        fact_ids=[fid for fid in ids if fid in facts],
        scope_teams=[team(row.roster_id) for row in rows],
        # No fact in the chapter names a player, so a player name in the blurb is an unsupported claim.
        scope_players=[],
        min_sentences=low,
        max_sentences=high,
        required=required_why_ids(facts, rows, table, odds),
    )
