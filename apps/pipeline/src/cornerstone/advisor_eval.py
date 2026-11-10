"""
The live eval of the Advisor: it reads each trade of a test set as of its week and saves the sheet and the read.
The test set and the output name league managers, so both stay outside the repo.
"""
import json
import re
import threading
import time
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import BaseModel

from analyzer.advisor import (
    AdvisorFailed,
    AdvisorOut,
    AdvisorSide,
    Bullet,
    TradeRead,
    advisor_sheet,
    check_read,
    read_trade_on_sheet,
)
from analyzer.trade import GivenPlayer, ProposedTrade, TradeSide
from analyzer.trade_news import NewsFeed
from facts.writer import ClaudeCall
from league.jev_port import Jev, JevResponse, NoulQuestion
from league.numbers import plural
from league.provider.raw import RawTransaction
from league.snapshot import Snapshot

# Dollars per million tokens. Claude Opus 5.5 is $4 for input, $20 for output, and $0.20 for a cache read, from the
# pricing page of Anthropic. The Advisor call keeps the one-hour cache, which writes at twice the input price.
# Jev is $0.042 per million input tokens and gives its output free, from docs.typesafe.ai/models.md.
CLAUDE_INPUT, CLAUDE_OUTPUT, CLAUDE_CACHE_READ, CLAUDE_CACHE_WRITE = 4.0, 20.0, 0.20, 8.0
JEV_INPUT = 0.042
# The words that AT-20 forbids in a read. The guards of the Advisor hold more inner words, and this count is the
# second look at the final text.
FORBIDDEN = ("trade value", "return bet")
LEAN_ORDER = ("Send it", "Lean yes", "Gut call", "Lean no", "Pass")


class TradeNotFound(Exception):
    """A team or a player of the test set is not on the roster the trade says. The eval records it and goes on."""


class EvalTrade(BaseModel):
    """One trade of the test set, by team name and player name. The other fields of the entry are not read."""

    id: int
    week: int
    asker: str
    other: str
    asker_gives: list[str]
    asker_gets: list[str]


def load_test_set(path: Path) -> list[EvalTrade]:
    """The trades of the test set file, in file order."""
    return [EvalTrade.model_validate(item) for item in json.loads(path.read_text(encoding="utf-8"))["trades"]]


# A player name matches in lower case, with no punctuation and no suffix, because the test set and the saved raw data
# of a week can spell a name two ways, such as "Brian Robinson Jr." and "Brian Robinson".
NAME_SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}


def _same_name(name: str) -> str:
    words = re.sub(r"[^a-z0-9 ]", "", name.lower()).split()
    return " ".join(words[:-1] if len(words) > 1 and words[-1] in NAME_SUFFIXES else words)


def _roster_of(snapshot: Snapshot, team: str) -> int:
    for roster_id, each in snapshot.teams.items():
        if each.name == team:
            return roster_id
    raise TradeNotFound(f"No team named {team}.")


def roster_ids_by_name(snapshots: Iterable[Snapshot]) -> dict[str, int]:
    """The roster id of each team name in the snapshots. Give them oldest first, so the newest name of a team wins.

    A manager renames a team in mid season, and the test set holds the name from the day it was made.
    """
    return {team.name: roster_id for snapshot in snapshots for roster_id, team in snapshot.teams.items()}


def named_in_week(trade: EvalTrade, snapshot: Snapshot, known: dict[str, int]) -> EvalTrade:
    """The trade with the team names the week has. A name that the week lacks comes from `known` by its roster id."""
    def in_week(team: str) -> str:
        if team in {each.name for each in snapshot.teams.values()} or team not in known:
            return team
        return snapshot.teams[known[team]].name

    return trade.model_copy(update={"asker": in_week(trade.asker), "other": in_week(trade.other)})


def _player_of(snapshot: Snapshot, roster_id: int, name: str) -> str:
    for pid in snapshot.rosters[roster_id]:
        if _same_name(snapshot.players[pid].name) == _same_name(name):
            return pid
    raise TradeNotFound(f"{name} is not on the roster of {snapshot.teams[roster_id].name}.")


def proposed_trade(trade: EvalTrade, snapshot: Snapshot) -> ProposedTrade:
    """The proposed trade of an entry. The asker gives `asker_gives` and the other team gives `asker_gets`."""
    asker, other = _roster_of(snapshot, trade.asker), _roster_of(snapshot, trade.other)
    return ProposedTrade(season=snapshot.season, asker=asker, sides=[
        TradeSide(roster_id=asker, gives=[GivenPlayer(player_id=_player_of(snapshot, asker, name), to=other)
                                          for name in trade.asker_gives]),
        TradeSide(roster_id=other, gives=[GivenPlayer(player_id=_player_of(snapshot, other, name), to=asker)
                                          for name in trade.asker_gets])])


def _missing_player(snapshot: Snapshot, rosters: dict[int, list[str]], trade: EvalTrade) -> str | None:
    """The first player of the trade who is not on the roster of his giver, or None when each one is."""
    asker, other = _roster_of(snapshot, trade.asker), _roster_of(snapshot, trade.other)
    for roster_id, names in ((asker, trade.asker_gives), (other, trade.asker_gets)):
        on_roster = {_same_name(snapshot.players[pid].name) for pid in rosters[roster_id]}
        for name in names:
            if _same_name(name) not in on_roster:
                return name
    return None


def _reversed(rosters: dict[int, list[str]], move: RawTransaction) -> dict[int, list[str]]:
    """The rosters before one trade: each player he added goes back to the roster that dropped him.

    A player who is not on his receiver is left alone, because the saved rosters were fetched before that trade.
    """
    back = {roster_id: list(pids) for roster_id, pids in rosters.items()}
    for pid, receiver in (move.adds or {}).items():
        if pid in back[receiver]:
            back[receiver].remove(pid)
            back[(move.drops or {})[pid]].append(pid)
    return back


def rosters_before(
        trade: EvalTrade, snapshot: Snapshot, transactions: list[RawTransaction],
) -> tuple[dict[int, list[str]], str | None]:
    """The rosters as they stood before the trade, and a note that says how many trades it took to get there.

    The saved week holds the rosters after the trades of the week, so a trade that already happened has its players on
    the wrong teams. The walk reverses the completed trades on file, newest first, until each player sits with his giver.
    The note is None when the saved rosters were right at the start.
    """
    rosters = snapshot.rosters
    missing = _missing_player(snapshot, rosters, trade)
    if missing is None:
        return rosters, None
    done = sorted((move for move in transactions if move.type == "trade" and move.status == "complete"),
                  key=lambda move: move.created, reverse=True)
    for count, move in enumerate(done, start=1):
        rosters = _reversed(rosters, move)
        if _missing_player(snapshot, rosters, trade) is None:
            return rosters, f"reversed {count} trade(s) of week {trade.week} on file, newest first"
    raise TradeNotFound(f"{missing} is not on the roster of his giver, and no trade on file puts him there.")


def claude_cost(usage) -> float:
    """The dollars of one Claude response, from its usage."""
    def tokens(name: str) -> int:
        return getattr(usage, name, 0) or 0

    return (tokens("input_tokens") * CLAUDE_INPUT + tokens("output_tokens") * CLAUDE_OUTPUT
            + tokens("cache_read_input_tokens") * CLAUDE_CACHE_READ
            + tokens("cache_creation_input_tokens") * CLAUDE_CACHE_WRITE) / 1_000_000


class Meter:
    """The dollars and the calls of one run. Claude calls reach it through the usage hook of the writer, Jev through
    MeteredJev. The reads run in threads, so a lock guards the sums."""

    def __init__(self) -> None:
        self.claude_usd = 0.0
        self.jev_usd = 0.0
        self.claude_calls = 0
        self.jev_requests = 0
        self._lock = threading.Lock()

    def add_claude(self, usage) -> None:
        with self._lock:
            self.claude_usd += claude_cost(usage)
            self.claude_calls += 1

    def add_jev(self, input_tokens: int | None) -> None:
        with self._lock:
            self.jev_usd += (input_tokens or 0) * JEV_INPUT / 1_000_000
            self.jev_requests += 1


class MeteredJev:
    """A Jev that counts the tokens of each answer on the meter and passes every request on."""

    def __init__(self, inner: Jev, meter: Meter) -> None:
        self._inner, self._meter = inner, meter

    def ask(self, state: dict, questions: dict[str, NoulQuestion]) -> JevResponse:
        response = self._inner.ask(state, questions)
        self._meter.add_jev(response.input_tokens)
        return response


# The saved snapshot of a week, with the transactions of that week on file.
SnapshotOfWeek = Callable[[int], tuple[Snapshot, list[RawTransaction]]]


def _as_out(read: TradeRead) -> AdvisorOut:
    """The final read in the shape of the output of the Advisor, so check_read can look at it a second time."""
    gains = {side.roster_id: side.reason for side in read.fairness.sides}
    return AdvisorOut(
        lean=read.lean, case=read.case, fairness="lopsided" if read.fairness.state == "lopsided" else "fair",
        gives_more=read.fairness.gives_more,
        sides=[AdvisorSide(roster_id=side.roster_id, gains=gains[side.roster_id],
                           bullets=[Bullet(text=b.text, mark=b.mark, fact_id=b.fact_id) for b in side.bullets])
               for side in read.sides])


def _texts(read: TradeRead) -> list[str]:
    return [read.case, *(side.reason for side in read.fairness.sides),
            *(bullet.text for side in read.sides for bullet in side.bullets)]


def _read_one(
        trade: EvalTrade, snapshot_of_week: dict[int, tuple[Snapshot, list[RawTransaction]]], known: dict[str, int],
        jev: Jev, call: ClaudeCall,
) -> dict:
    """The record of one trade: the sheet and the read, or the error that stopped it."""
    started = time.monotonic()
    claude_calls = 0
    record: dict = {"id": trade.id, "week": trade.week, "asker": trade.asker, "other": trade.other, "roster_note": None,
                    "sheet": None, "lean": None, "case": None, "fairness": None, "sides": None,
                    "check_failures": [], "inner_word_hits": 0, "error": None}

    def counted(system: str, user: str, output_model):
        nonlocal claude_calls
        claude_calls += 1
        return call(system, user, output_model)

    try:
        base, transactions = snapshot_of_week[trade.week]
        trade = named_in_week(trade, base, known)
        rosters, record["roster_note"] = rosters_before(trade, base, transactions)
        # A copy per trade, so each trade has its own rank table and the threads share no cache.
        snapshot = base.model_copy(update={"rosters": rosters})
        proposed = proposed_trade(trade, snapshot)
        # The Sleeper feed holds only the news of now, so a past week gets no news, not news from after its trade.
        facts = advisor_sheet(proposed, snapshot, jev, NewsFeed(fetch=lambda _player_id: []))
        read = read_trade_on_sheet(proposed, snapshot, facts, jev=jev, call=counted)
        record["sheet"] = {fid: fact.text for fid, fact in facts.items()}
        record |= {"lean": read.lean, "case": read.case,
                   "fairness": {"state": read.fairness.state, "gives_more": read.fairness.gives_more},
                   "sides": [{"roster_id": side.roster_id,
                              "gains": next(f.reason for f in read.fairness.sides if f.roster_id == side.roster_id),
                              "bullets": [b.model_dump() for b in side.bullets]} for side in read.sides]}
        # The read passed the guards inside read_trade_on_sheet. This second look checks the final text on the same sheet.
        record["check_failures"] = check_read(_as_out(read), proposed, snapshot, facts)
        record["inner_word_hits"] = sum(len(re.findall(word, text, re.IGNORECASE))
                                        for text in _texts(read) for word in FORBIDDEN)
    except (TradeNotFound, AdvisorFailed, ValueError) as error:
        record["error"] = str(error)
    record["claude_calls"] = claude_calls
    record["seconds"] = round(time.monotonic() - started, 2)
    return record


def run_eval(
        trades: list[EvalTrade], snapshot_of: SnapshotOfWeek, *, jev: Jev, call: ClaudeCall, out_dir: Path, meter: Meter,
        workers: int = 1,
) -> dict:
    """Read each trade as of its week, save trade-<id>.json for each and summary.json, and give the summary.

    A trade that fails is an error in its record and in the summary, and the other trades go on.
    """
    started = time.monotonic()
    out_dir.mkdir(parents=True, exist_ok=True)
    # One snapshot per week, built before the threads start, so no two threads build the same one.
    weeks = {week: snapshot_of(week) for week in sorted({trade.week for trade in trades})}
    known = roster_ids_by_name(snapshot for _, (snapshot, _) in sorted(weeks.items()))
    metered = MeteredJev(jev, meter)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        records = list(pool.map(lambda trade: _read_one(trade, weeks, known, metered, call), trades))
    for record in records:
        (out_dir / f"trade-{record['id']}.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    reads = [r for r in records if r["error"] is None]
    summary = {
        "trades": len(records),
        "reads": len(reads),
        "leans": {str(r["id"]): r["lean"] for r in reads},
        "errors": {str(r["id"]): r["error"] for r in records if r["error"] is not None},
        "check_failures": sum(len(r["check_failures"]) for r in reads),
        "inner_word_hits": sum(r["inner_word_hits"] for r in reads),
        "claude_calls": meter.claude_calls,
        "cost": {"claude": meter.claude_usd, "jev": meter.jev_usd, "total": meter.claude_usd + meter.jev_usd},
        "seconds": round(time.monotonic() - started, 1),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    return summary


def summary_lines(summary: dict) -> list[str]:
    """The lines the command prints: the counts, the Lean of each trade, the checks, the cost, and the time."""
    counts = {lean: sum(1 for each in summary["leans"].values() if each == lean) for lean in LEAN_ORDER}
    errors = len(summary["errors"])
    cost = summary["cost"]
    lines = [
        (f"{summary['trades']} {plural(summary['trades'], 'trade', 'trades')}: "
         f"{summary['reads']} {plural(summary['reads'], 'read', 'reads')}, "
         f"{errors} {plural(errors, 'error', 'errors')}."),
        "Leans: " + ", ".join(f"{lean} {count}" for lean, count in counts.items() if count) + ".",
    ]
    ids = sorted({*summary["leans"], *summary["errors"]}, key=int)
    lines += [f"trade {each}: {summary['leans'].get(each) or 'error, ' + summary['errors'][each]}" for each in ids]
    lines += [
        f"Checks: {summary['check_failures']} failed after the retry, {summary['inner_word_hits']} forbidden words.",
        (f"Cost: ${cost['total']:.2f} (Claude ${cost['claude']:.2f}, Jev ${cost['jev']:.3f}) "
         f"over {summary['claude_calls']} Claude calls."),
        f"Time: {summary['seconds']:.0f} s.",
    ]
    return lines
