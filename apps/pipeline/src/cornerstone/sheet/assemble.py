"""
Puts the facts into chapters and builds the bundle that the writer and the page read.
It also writes and reads the bundle file.
"""
from collections.abc import Callable
from datetime import date
from pathlib import Path

from cornerstone.client import Client
from cornerstone.models import (
    Bundle,
    Chapter,
    Fact,
    FactSheet,
    History,
    NflverseWeek,
    OddsResult,
    Trade,
    Week,
    WeekData,
)
from cornerstone.provider.sleeper import fetch_news
from cornerstone.sheet import awards, drops, leaders, matchups, next_week, rankings, standings, week
from cornerstone.sheet.base import BYE_FACT_PREFIX, Context, sentence_range, week_dates
from cornerstone.sheet.rankings import rankings_chapter
from cornerstone.snapshot import Snapshot

# The fact groups of the sheet, in the order the sheet lists their facts. This list alone sets that order.
# A group reads only the context and the client, so it needs no file and no clock. Every group takes the
# client, so the assembly calls each group the same way. A group reads a league number from it when it needs one.
FACT_GROUPS: tuple[Callable[[Context, Client], list[Fact]], ...] = (
    week.facts, standings.facts, matchups.facts, awards.facts, next_week.facts, leaders.facts, drops.facts,
    rankings.facts,
)
# A chapter cites at most this many facts with an ID that starts with "H." or "P.", so the writer
# stays focused. The cap does not cover the position-rank facts.
HISTORY_FACTS_MAX = 6
# Slots kept for player trends, so the team facts cannot crowd them out of a chapter.
PLAYER_TREND_MAX = 2
# Most telling first: a chapter over the cap keeps the front of this order.
HISTORY_KINDS = ("streak", "high", "trend", "avg")


def _history_ids(facts: dict[str, Fact], rosters, kinds, players=()) -> list[str]:
    """History and player trend fact IDs, most telling first, cut to the cap.

    The team facts keep the slots the player trends leave.
    """
    trends = [f"P.{p}.trend" for p in players if f"P.{p}.trend" in facts][:PLAYER_TREND_MAX]
    ids = [f"H.{r}.{k}" for k in kinds for r in rosters]
    teams = [i for i in ids if i in facts][: HISTORY_FACTS_MAX - len(trends)]
    return teams + trends


def _with_prefix(facts: dict[str, Fact], *prefixes: str) -> list[str]:
    return [fid for fid in facts if any(fid == p or fid.startswith(p) for p in prefixes)]


def _dedupe(ids: list[str]) -> list[str]:
    return list(dict.fromkeys(ids))


def chapters(c: Context, facts: dict[str, Fact]) -> list[Chapter]:
    week = c.week
    roster_ids = {m.matchup_id: (m.a.roster_id, m.b.roster_id) for m in week.matchups}
    all_rosters = list(week.teams)

    def players_of(rosters) -> list[str]:
        return [
            line.name
            for m in week.matchups for s in (m.a, m.b) if s.roster_id in rosters for line in s.lines
        ]

    def started_ids(rosters) -> list[str]:
        return [
            line.player_id
            for m in week.matchups for s in (m.a, m.b) if s.roster_id in rosters
            for line in s.lines if line.started
        ]

    def make(key, title, ids, rosters, rng, players=None) -> Chapter:
        return Chapter(
            key=key,
            title=title,
            fact_ids=_dedupe([i for i in ids if i in facts]),
            scope_teams=[c.team(r) for r in rosters],
            scope_players=_dedupe(players_of(rosters) if players is None else players),
            min_sentences=sentence_range(rng, c.client)[0],
            max_sentences=sentence_range(rng, c.client)[1],
        )

    def drop_ids(keep) -> list[str]:
        return [fid for d in c.drops if keep(d) for fid in (f"D.{d.player_id}", f"D.{d.player_id}.value")]

    def injury_ids(pids) -> list[str]:
        return [fid for p in pids for fid in (f"I.{p}.pregame", f"I.{p}.history")]

    def standings_ids(rosters) -> list[str]:
        return [f"S.{c.by_rank[r].rank}" for r in rosters]

    out = []
    pair = roster_ids[c.pick.matchup_id]
    out.append(make(
        "motw", "Matchup of the Week",
        _with_prefix(facts, f"M{c.pick.matchup_id}.") + ["PICK"] + standings_ids(pair)
        + [f"RANK.{p}" for p in started_ids(pair)]
        + _history_ids(facts, pair, HISTORY_KINDS, started_ids(pair))
        + drop_ids(lambda d: d.matchup_id == c.pick.matchup_id) + injury_ids(started_ids(pair)),
        pair, "motw",
    ))
    gc = next((a for a in c.awards if a.key == "game_changer"), None)
    if gc:
        pair = roster_ids[gc.matchup_id]
        gc_pid = gc.line.player_id
        # The chapter is about one player and what his points did for his team. From the matchup it keeps the
        # result and the upset, plus each fact whose id ends in his player id: .starter.<rid>.<pid>,
        # .driver.<pid>, .swing.<pid>, .regret.<pid>, .move.<pid>, .inj.<pid>, .hurt.<pid>, and .snaps.<pid>.
        # Every other matchup fact names an opponent or a teammate, so the writer never sees those names. The scope
        # lists only him, so the code check fails a sentence that names any other player.
        matchup_ids = [
            fid for fid in _with_prefix(facts, f"M{gc.matchup_id}.")
            if fid in (f"M{gc.matchup_id}.result", f"M{gc.matchup_id}.upset") or fid.endswith(f".{gc_pid}")
        ]
        out.append(make(
            "game_changer", "Game Changer",
            ["AW.game_changer", "AW.game_changer.news"] + matchup_ids
            + [f"RANK.{gc.line.player_id}"] + _history_ids(facts, [], (), [gc.line.player_id])
            + drop_ids(lambda d: d.player_id == gc.line.player_id) + injury_ids([gc.line.player_id]),
            pair, "game_changer", players=[gc.line.name],
        ))
    out.append(make(
        "awards", "Awards",
        _with_prefix(facts, "AW.") + ["W.adds", "W.injured"] + [f"RANK.{a.line.player_id}" for a in c.awards]
        + [f"M{mid}.result" for mid in roster_ids]
        + _history_ids(facts, [], (), [a.line.player_id for a in c.awards])
        + ["W.drops"] + drop_ids(lambda d: d.player_id in {a.line.player_id for a in c.awards})
        + injury_ids([a.line.player_id for a in c.awards]),
        all_rosters, "awards",
    ))
    out.append(make(
        "position_leaders", "Position Leaders",
        _with_prefix(facts, "LEAD."),
        all_rosters, "position_leaders",
        players=[leader.line.name for leader in c.leaders],
    ))
    for mid, pair in roster_ids.items():
        title = " vs ".join(c.team(r) for r in pair)
        out.append(make(
            f"recap_{mid}", title,
            _with_prefix(facts, f"M{mid}.") + standings_ids(pair)
            + _history_ids(facts, pair, HISTORY_KINDS, started_ids(pair))
            + drop_ids(lambda d, mid=mid: d.matchup_id == mid) + injury_ids(started_ids(pair)),
            pair, "recap",
        ))
    out.append(make(
        "median", "The Median Game",
        # The odds why belongs to the rankings chapter alone, so the median lists only the odds.
        _with_prefix(facts, "MED.") + _with_prefix(facts, "S.")
        + [fid for fid in _with_prefix(facts, "ODDS.") if not fid.endswith(".why")]
        + _history_ids(facts, all_rosters, ("high",)),
        all_rosters, "median",
    ))
    # The bye facts name players on the rosters now, such as a bye cover, so the scope adds them to the lineup names.
    bye_players = [p for fid in _with_prefix(facts, BYE_FACT_PREFIX) for p in facts[fid].players]
    out.append(make(
        "next_week", "Next Week",
        _with_prefix(facts, "NX.", "S.", "SOS.", "SW.")
        + _history_ids(facts, [r for nx in c.next for r in (nx.a, nx.b)], ("streak", "trend")),
        all_rosters, "next_week", players=players_of(all_rosters) + bye_players,
    ))
    if c.power:
        out.append(rankings_chapter(facts, c.power, c.team, c.table, c.odds, client=c.client))
    return out


def build_bundle(
    week: Week,
    news: Callable[[str], list[dict]] = fetch_news,
    history: History | None = None,
    trades: list[Trade] | None = None,
    nfl: NflverseWeek | None = None,
    snapshot: Snapshot | None = None,
    today: date | None = None,
    odds_before: OddsResult | None = None,
    *,
    client: Client,
) -> Bundle:
    c = Context(week, news, history, trades, nfl, snapshot=snapshot, today=today, odds_before=odds_before,
                client=client)
    facts = {f.id: f for group in FACT_GROUPS for f in group(c, client)}
    data = WeekData(
        season=week.season,
        week=week.week,
        dates=week_dates(week.season_start, week.week),
        publish_date=c.today.strftime("%a %b %-d, %Y"),
        teams=week.teams,
        matchups=c.mfacts,
        median=c.median,
        table=c.table,
        awards=c.awards,
        pick=c.pick,
        next=c.next,
        history=c.season_history,
        ranks=c.ranks,
        leaders=c.leaders,
        trades=trades if trades is not None else [],
        trade_players={pid: c.lines[pid].name for t in c.trades for pid in t.adds if pid in c.lines},
        drops=c.drops,
        drop_source=("nflverse" if c.nfl_up else "sleeper") if c.drops else "none",
    )
    return Bundle(data=data, sheet=FactSheet(facts=facts, chapters=chapters(c, facts)), odds=c.odds)


def write_bundle(b: Bundle, path: Path) -> None:
    path.write_text(b.model_dump_json(indent=2), encoding="utf-8")


def read_bundle(path: Path) -> Bundle:
    return Bundle.model_validate_json(path.read_text(encoding="utf-8"))
