"""
Builds the family of facts for each matchup: the result, the lines, the story, the context, and the impact.
The recap and Matchup of the Week chapters read them.
"""
from datetime import datetime
from decimal import Decimal

from cornerstone.facts_league import STREAK_ON_THE_LINE, streak
from cornerstone.odds import roster_status
from cornerstone.sheet.base import MOVE_WORDS, Context, Nums, fact
from league.client import Client
from league.models import (
    Fact,
    OddsResult,
    OddsStatus,
    PlayerLine,
    sub,
)
from league.numbers import r2
from league.standings_table import season_records

# The clause of the impact fact for a first clinch or a first out. The words follow the odds fact of the same status.
STATUS_CLAUSES = {"in": "clinched a playoff spot", "out": "is now out of the playoff race"}


def facts(context: Context, client: Client) -> list[Fact]:
    """The result, the lines, the story, the context, and the impact of each matchup.

    The Matchup of the Week, Game Changer, and recap chapters read them. The awards chapter reads each result.
    """
    return matchup_fact_family(context)


def matchup_fact_family(c: Context) -> list[Fact]:
    out = []
    new_statuses = _first_statuses(c)
    for f, m in zip(c.mfacts, c.week.matchups):
        out += _result_facts(c, f, m)
        out += _line_facts(c, f, m)
        out += _story_facts(c, f)
        out += _injury_facts(c, f, m)
        out += _hurt_facts(c, f, m)
        out += _lead_facts(c, f, m)
        out += _context_facts(c, f, m)
        out.append(_impact_fact(c, f, m, new_statuses))
    return out


def _result_facts(c, f, m) -> list[Fact]:
    n = Nums()
    mid = f"M{f.matchup_id}"
    a, b = c.team(m.a.roster_id), c.team(m.b.roster_id)
    if f.winner is None:
        text = f"{a} and {b} tied at {n(f.score_w)}."
        teams = [a, b]
    else:
        w, loser = c.team(f.winner), c.team(f.loser)
        text = f"{w} beat {loser} {n(f.score_w)} to {n(f.score_l)}, a margin of {n(f.margin)}."
        teams = [w, loser]
    out = [fact(f"{mid}.result", text, n, teams, [])]
    for rid, line in f.top_scorer.items():
        n = Nums()
        team = c.team(rid)
        text = f"{c.who(line)} was the top scorer for {team} with {n(line.points)}."
        out.append(fact(f"{mid}.top.{rid}", text, n, [team], [line.name]))
    return out


def _line_facts(c, f, m) -> list[Fact]:
    out = []
    for side in (m.a, m.b):
        team = c.team(side.roster_id)
        for line in side.lines:
            if not line.started:
                continue
            n = Nums()
            text = f"{c.who(line)} started for {team} and {c.against_projection(line, n)}."
            out.append(fact(f"M{f.matchup_id}.starter.{side.roster_id}.{line.player_id}", text, n, [team], [line.name]))
    return out


def _story_facts(c, f) -> list[Fact]:
    """Drivers, swing players, bench regret, and recent adds for one matchup."""
    mid = f"M{f.matchup_id}"
    out = []
    for line in f.drivers:
        n = Nums()
        team = c.team(c.line_owner[line.player_id])
        gap = abs(sub(line.points, line.projection))
        text = (
            f"{line.name} ({team}) is a margin driver: {n(line.points)} on a {n(line.projection)} "
            f"projection, a gap of {n(gap)} against a margin of {n(f.margin)}."
        )
        out.append(fact(f"{mid}.driver.{line.player_id}", text, n, [team], [line.name]))
    for line in f.swing:
        n = Nums()
        team = c.team(f.winner)
        text = f"{line.name} is a swing player for {team}: {n(line.points)} exceeded the margin of {n(f.margin)}."
        out.append(fact(f"{mid}.swing.{line.player_id}", text, n, [team], [line.name]))
    for bench, starter in f.bench_regret:
        n = Nums()
        team = c.team(f.loser)
        text = (
            f"{team} left {bench.name} ({n(bench.points)}) on the bench behind "
            f"{starter.name} ({n(starter.points)}); the swap would have flipped the result."
        )
        out.append(fact(f"{mid}.regret.{bench.player_id}", text, n, [team], [bench.name, starter.name]))
    for mv in f.recent_moves:
        n = Nums()
        line = c.lines[mv.player_id]
        team = c.team(mv.roster_id)
        text = (
            f"{line.name} is a recent add: {line.name} started for {team} after a "
            f"{MOVE_WORDS[mv.kind]} in week {n(mv.week)} "
            f"and {c.against_projection(line, n)}."
        )
        out.append(fact(f"{mid}.move.{mv.player_id}", text, n, [team], [line.name]))
    return out


def _injury_facts(c, f, m) -> list[Fact]:
    """One fact per started line with a Sleeper injury status in one matchup."""
    out = []
    for side in (m.a, m.b):
        team = c.team(side.roster_id)
        for line in side.lines:
            if not line.started or not line.injury_status:
                continue
            # The status comes from the players file fetched after the games, so it is post-game.
            # The fact must not imply that the player was hurt at kickoff.
            status = f"listed {line.injury_status}"
            if line.injury_body_part:
                status += f" ({line.injury_body_part})"
            text = (
                f"{line.name} is now {status} on Sleeper as of the Tuesday after this week's games. "
                "The status may have come from this game."
            )
            out.append(fact(f"M{f.matchup_id}.inj.{line.player_id}", text, Nums(), [team], [line.name]))
    return out


def _hurt_facts(c, f, m) -> list[Fact]:
    """The injury play and the snaps of each started line, so a recap can tell when a starter was hurt.

    The play comes from the nflverse play by play, through `NflverseWeek.injury_plays`. The snaps come from the
    Sleeper stats of the week. With no play by play, the play fact is absent, and the recap says nothing about it.
    """
    plays = c.nfl.injury_plays if c.nfl is not None and c.nfl.injury_plays is not None else {}
    out = []
    for side in (m.a, m.b):
        team = c.team(side.roster_id)
        for line in side.lines:
            if not line.started:
                continue
            play = plays.get(line.player_id)
            if play is not None:
                n = Nums()
                when = "overtime" if play.quarter == 5 else f"the {n.ord(play.quarter)} quarter"
                # The play by play writes "00:32" for a clock under a minute. The page reads "0:32".
                clock = n.text(play.clock.removeprefix("0"))
                text = f"{line.name} was hurt on a play in {when} of {play.away} at {play.home}, with {clock} left."
                out.append(fact(f"M{f.matchup_id}.hurt.{line.player_id}", text, n, [team], [line.name]))
            # A starter with a Sleeper status but no injury play still gets his snaps, so the recap can say he left
            # early or played through it.
            stats = c.week.stats.get(line.player_id, {})
            if (play is not None or line.injury_status) and "off_snp" in stats and "tm_off_snp" in stats:
                n = Nums()
                text = (f"{line.name} played {n(int(stats['off_snp']))} of {n(int(stats['tm_off_snp']))} "
                        f"offensive snaps for {line.nfl_team}.")
                out.append(fact(f"M{f.matchup_id}.snaps.{line.player_id}", text, n, [team], [line.name]))
    return out


# Each Sunday game time has three parts: the kickoff hour it ends before, the words that follow "after" in the lead
# fact, and the words that say when a play happened. The hours are Eastern time, as the kickoffs are.
SUNDAY_GAME_TIMES = (
    (16, "the early Sunday games", "in the early Sunday games"),
    (19, "the late Sunday games", "in the late Sunday games"),
    (24, "Sunday night", "on Sunday night"),
)
SUNDAY = 6


def _game_time(kickoff: datetime) -> tuple[str, str]:
    """The game time of a kickoff, as the words after "after" and the words of when. Each day but Sunday is one."""
    if kickoff.weekday() != SUNDAY:
        day = kickoff.strftime("%A")
        return day, f"on {day}"
    return next((after, during) for hour, after, during in SUNDAY_GAME_TIMES if kickoff.hour < hour)


def _game_time_lines(c, m) -> list[tuple[tuple[str, str], list[tuple[int, PlayerLine]]]] | None:
    """The started lines of both sides by game time, in kickoff order, each with its roster ID.

    None when the week has no kickoffs, or when a starter with points has no kickoff. Then the sums would not
    reach the final score, so the lead facts are absent, and the recap says nothing about the lead.
    """
    kickoffs = c.nfl.kickoffs if c.nfl is not None else None
    if not kickoffs:
        return None
    times: dict[tuple[str, str], list[tuple[int, PlayerLine]]] = {}
    first: dict[tuple[str, str], datetime] = {}
    for side in (m.a, m.b):
        for line in side.lines:
            if not line.started:
                continue
            kickoff = kickoffs.get(line.nfl_team or "")
            if kickoff is None:
                # A starter on a bye or with no team scores 0, so he moves no lead.
                if line.points:
                    return None
                continue
            time = _game_time(kickoff)
            times.setdefault(time, []).append((side.roster_id, line))
            first[time] = min(first.get(time, kickoff), kickoff)
    return sorted(times.items(), key=lambda item: first[item[0]])


def _lead_facts(c, f, m) -> list[Fact]:
    """The lead after each game time, and the turn when the leader before the last game time lost.

    The game time of a starter comes from the kickoff of his NFL team, from the nflverse schedule through
    `NflverseWeek.kickoffs`. The points come from the Sleeper matchups. A game time with no starter of this matchup is not
    in the list, so a matchup with no Monday starter ends after Sunday night.
    """
    times = _game_time_lines(c, m)
    if times is None or len(times) < 2:
        return []
    mid = f"M{f.matchup_id}"
    a, b = m.a.roster_id, m.b.roster_id
    margin = Decimal(0)
    margins = []
    for time, lines in times:
        # Decimal sums keep the last margin equal to the final margin.
        margin += sum((Decimal(str(line.points)) * (1 if rid == a else -1) for rid, line in lines), Decimal(0))
        margins.append((time, r2(float(margin))))
    n = Nums()
    parts, leaders = [], []
    for (after, _), x in margins:
        if x == 0:
            parts.append(f"after {after}, the teams were level")
            continue
        leader = a if x > 0 else b
        parts.append(f"after {after}, {c.team(leader)} led by {n(abs(x))}")
        if not leaders or leaders[-1] != leader:
            leaders.append(leader)
    changes = len(leaders) - 1
    if changes == 0:
        tail = "The lead never changed."
    else:
        tail = f"The lead changed {n(changes)} time{'' if changes == 1 else 's'}."
    text = "The lead by game time: " + "; ".join(parts) + ". " + tail
    out = [fact(f"{mid}.lead", text, n, [c.team(a), c.team(b)], [])]
    (prev_after, _), prev = margins[-2]
    if f.winner is None or prev == 0 or (a if prev > 0 else b) == f.winner:
        return out
    n = Nums()
    leader, winner = c.team(f.loser), c.team(f.winner)
    (_, during), last_lines = times[-1]
    # The winner's starters come first, so the line reads as the turn.
    ordered = sorted(last_lines, key=lambda item: (item[0] != f.winner, -item[1].points))
    scored = "; ".join(f"{line.name} scored {n(line.points)} for {c.team(rid)}" for rid, line in ordered)
    text = (f"{leader} led {winner} by {n(abs(prev))} after {prev_after}, and {winner} took the lead {during} "
            f"and won. {during[0].upper()}{during[1:]}, {scored}.")
    out.append(fact(f"{mid}.turn", text, n, [leader, winner], [line.name for _, line in ordered]))
    return out


def _context_facts(c, f, m) -> list[Fact]:
    mid = f"M{f.matchup_id}"
    out = []
    if f.winner is not None and c.before[f.winner] > c.before[f.loser]:
        n = Nums()
        w, loser = c.team(f.winner), c.team(f.loser)
        text = (
            f"This was an upset: {w} was {n.ord(c.before[f.winner])} before this week "
            f"and {loser} was {n.ord(c.before[f.loser])}."
        )
        out.append(fact(f"{mid}.upset", text, n, [w, loser], []))
    n = Nums()
    parts = []
    for rid in (m.a.roster_id, m.b.roster_id):
        s = c.by_rank[rid]
        parts.append(f"{c.team(rid)} is now {n.record(s.wins, s.losses)} ({n.ord(s.rank)}).")
    teams = [c.team(m.a.roster_id), c.team(m.b.roster_id)]
    out.append(fact(f"{mid}.records", " ".join(parts), n, teams, []))
    return out


def _impact_fact(c, f, m, new_statuses: dict[int, OddsStatus]) -> Fact:
    """What this week did to each team of one matchup. GLOSSARY.md, "Impact fact".

    Each team gets one sentence of the parts that apply this week.
    """
    n = Nums()
    sentences = []
    for rid in (m.a.roster_id, m.b.roster_id):
        place_before, place_after = c.before[rid], c.by_rank[rid].rank
        clauses = [
            _place_clause(place_before, place_after, n),
            *_cut_clause(place_before, place_after, c.client.settings.playoff_spots),
        ]
        clauses += _odds_clause(c.odds_before, c.odds, rid, n)
        clauses.append(_median_clause(c, f, rid, n))
        clauses += _streak_clause(c, rid, n)
        if rid in new_statuses:
            clauses.append(STATUS_CLAUSES[new_statuses[rid]])
        sentences.append(f"{c.team(rid)} {_join(clauses)}.")
    teams = [c.team(m.a.roster_id), c.team(m.b.roster_id)]
    return fact(f"M{f.matchup_id}.impact", " ".join(sentences), n, teams, [])


def _first_statuses(c) -> dict[int, OddsStatus]:
    """Each roster that the plain check of the odds first gives `in` or `out` this week. GLOSSARY.md, "Clinched", "Out".

    The check runs on the records after this week and after the week before, each with its weeks left. A roster
    that had the status last week is not in the result, so a clinch or an out shows only in its first week.
    """
    h, week, client = c.history, c.week.week, c.client
    if h is None or not h.complete() or week > client.settings.last_regular_week:
        return {}
    spots, left = client.settings.playoff_spots, client.settings.last_regular_week - week
    now, before = season_records(h, week), season_records(h, week - 1)
    out = {}
    # The saved odds start at ODDS_FROM_WEEK and the odds of the week before can be missing.
    # The plain check on the records works for every week.
    for rid in now:
        status = roster_status(rid, now, left, spots)
        # A roster with no record before this week has no earlier status.
        earlier = roster_status(rid, before, left + 1, spots) if len(before) == len(now) else "open"
        if status != "open" and status != earlier:
            out[rid] = status
    return out


def _place_clause(before: int, after: int, n: Nums) -> str:
    """The standings place before and after. GLOSSARY.md, "Standings place": "rose" or "fell", never "moved"."""
    if before == after:
        return f"stayed {n.ord(after)} in the standings"
    verb = "rose" if after < before else "fell"
    return f"{verb} from {n.ord(before)} to {n.ord(after)} in the standings"


def _cut_clause(before: int, after: int, spots: int) -> list[str]:
    """The cut, only when the team crossed into the playoff spots or fell out of them this week."""
    if before > spots >= after:
        return ["crossed into the playoff spots"]
    if before <= spots < after:
        return ["fell out of the playoff spots"]
    return []


def _odds_clause(before: OddsResult | None, after: OddsResult | None, rid: int, n: Nums) -> list[str]:
    """The playoff odds of last week's saved odds and of this week. GLOSSARY.md, "Playoff odds", "Impact fact".

    The other games and the median game move the odds too, so the clause says "this week", not the game.
    With no saved odds before this week, or no odds after it, no odds part shows.
    """
    if before is None or after is None or rid not in before.teams or rid not in after.teams:
        return []
    old, new = before.teams[rid].playoff, after.teams[rid].playoff
    # Brian chose one "about" per clause, because two read heavy: "from about 99% to 86%".
    # It goes before the first engine number. A clinched 100 or an out 0 is sure, so it takes none.
    first = next((i for i, p in enumerate((old, new)) if p not in (0, 100)), None)
    words = [f"about {n(p)}%" if i == first else f"{n(p)}%" for i, p in enumerate((old, new))]
    return [f"saw its playoff odds go from {words[0]} to {words[1]} this week"]


def _median_clause(c, f, rid: int, n: Nums) -> str:
    """The median result and the record of the week: the head-to-head game and the median game."""
    wins = (f.winner == rid) + (rid in c.median.above)
    losses = (f.loser == rid) + (rid in c.median.below)
    # A score equal to the median is in neither list, so it is neither a win nor a loss.
    word = "beat" if rid in c.median.above else "missed" if rid in c.median.below else "matched"
    return f"{word} the median to go {n.record(wins, losses)} this week"


def _streak_clause(c, rid: int, n: Nums) -> list[str]:
    """A head-to-head streak of 3 or more that this game started, extended, or ended. The median game does not count.

    The length uses the rule of "Streak on the line" in GLOSSARY.md. With no complete history, no streak shows.
    """
    h = c.history
    if h is None or not h.complete():
        return []
    now, before = streak(h, rid, c.week.week), streak(h, rid, c.week.week - 1)
    if abs(now) >= STREAK_ON_THE_LINE:
        return [f"has now {'won' if now > 0 else 'lost'} {n(abs(now))} straight"]
    # A streak ends when the sign of the run changes, or when a tie sets it to 0.
    if abs(before) >= STREAK_ON_THE_LINE and (now == 0 or (now > 0) != (before > 0)):
        return [f"ended a {n(abs(before))}-game {'winning' if before > 0 else 'losing'} streak"]
    return []


def _join(clauses: list[str]) -> str:
    """The clauses as one list: "a", "a and b", or "a, b, and c"."""
    if len(clauses) < 3:
        return " and ".join(clauses)
    return ", ".join(clauses[:-1]) + ", and " + clauses[-1]
