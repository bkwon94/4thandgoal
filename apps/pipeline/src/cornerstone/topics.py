"""
Writes topics.json beside page.json: the Answer of each of the 7 league Topics of the front door for each team.
An Answer may carry one block, the data of its card, from topic_blocks.py. It reads the published files of the build, page.json, rankings.json, and managers.json, and writes no new prose.
"""
import json
import logging
from pathlib import Path

from pydantic import BaseModel

from cornerstone.topic_blocks import (
    TopicBlock,
    ladder_block,
    last_matchup_block,
    next_matchup_block,
    rank_movers_block,
    recap_block,
    schedule_block,
)
from league.files import write_bytes_atomic
from league.models import Week
from league.numbers import ordinal
from league.paths import site_week_dir

# The Topics file has its own version, so a change to it never breaks the reader of another file.
# Version 2 adds the optional `block` of each Answer. The site still reads version 1, with no block.
TOPICS_SCHEMA_VERSION = 2
TOPICS_FILE = "topics.json"

log = logging.getLogger(__name__)


class Stat(BaseModel):
    """One number of the data block of an Answer, such as Rank and 6th."""
    label: str
    value: str


class Row(BaseModel):
    """One line of the data block, such as one side of a game. The roster id gives the avatar, and `you` marks the
    line of the team of the Answer."""
    label: str
    value: str
    note: str | None = None
    roster_id: int | None = None
    you: bool = False


class TopicAnswer(BaseModel):
    """The Answer of one league Topic for one team. The fact is the line of its Suggestion. The text holds the
    blurbs of the week as they are, one paragraph each. The block is the data of the card of the Topic, or None for a
    Topic with no card. The stats and the rows stay beside it for a reader of version 1."""
    topic: str
    fact: str
    stats: list[Stat] = []
    rows: list[Row] = []
    text: list[str] = []
    block: TopicBlock | None = None


class TopicsFile(BaseModel):
    schema_version: int = TOPICS_SCHEMA_VERSION
    season: int
    week: int
    # The Answers of each team, keyed by roster id as text, as the other published files key their maps.
    teams: dict[str, list[TopicAnswer]]


def _read(path: Path) -> dict | None:
    """A published season file, or None when the build has not written it."""
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _points(value: float) -> str:
    """The points of a score as the week page shows them, such as 80.11 or 98.8."""
    return f"{value:g}"


def _week_recap(rid: int, page: dict) -> TopicAnswer:
    scores = sorted((side["score"] for m in page["matchups"] for side in m["sides"]), reverse=True)
    mine = next(side["score"] for m in page["matchups"] for side in m["sides"] if side["team"]["roster_id"] == rid)
    place = f"{ordinal(scores.index(mine) + 1)} of {len(scores)}"
    stats = [Stat(label="Your score", value=_points(mine)), Stat(label="Place", value=place)]
    if page.get("median"):
        stats.append(Stat(label="Median", value=_points(page["median"]["value"])))
    rows = [Row(label=a["title"], value=_points(a["points"]), note=f"{a['player']} · {a['team']}")
            for a in page["awards"] if not a["missing"]]
    blurbs = page["blurbs"]
    return TopicAnswer(topic="week_recap", fact=f"You scored {_points(mine)}, {place}", stats=stats, rows=rows,
                       # The awards show as rows, so the text is the matchup of the week alone and stays short.
                       text=[blurbs["motw"]] if blurbs.get("motw") else [], block=recap_block(rid, page))


def _last_matchup(rid: int, page: dict, league_week: Week | None) -> TopicAnswer | None:
    game = next((m for m in page["matchups"] if any(s["team"]["roster_id"] == rid for s in m["sides"])), None)
    if game is None:
        return None
    mine = next(s for s in game["sides"] if s["team"]["roster_id"] == rid)
    other = next(s for s in game["sides"] if s["team"]["roster_id"] != rid)
    word = "Won" if mine["score"] > other["score"] else "Lost" if mine["score"] < other["score"] else "Tied"
    rows = [Row(label=s["team"]["name"], value=_points(s["score"]),
                note=f"{s['top']['name']} {_points(s['top']['points'])}" if s.get("top") else None,
                roster_id=s["team"]["roster_id"], you=s is mine) for s in game["sides"]]
    return TopicAnswer(topic="last_matchup", fact=f"{word} {_points(mine['score'])} to {_points(other['score'])}",
                       rows=rows, text=[game["recap"]] if game.get("recap") else [],
                       block=last_matchup_block(rid, league_week) if league_week else None)


def _next_matchup(rid: int, page: dict, league_week: Week | None) -> TopicAnswer | None:
    pair = next((p for p in page["next"] if rid in (p["a"]["roster_id"], p["b"]["roster_id"])), None)
    if pair is None:
        return None
    mine, other = (pair["a"], pair["b"]) if pair["a"]["roster_id"] == rid else (pair["b"], pair["a"])
    rows = [Row(label=t["name"], value=f"{t['wins']}-{t['losses']}",
                note=("Bye: " + ", ".join(b["name"] for b in t["byes"])) if t.get("byes") else None,
                roster_id=t["roster_id"], you=t is mine) for t in (mine, other)]
    blurb = page["blurbs"].get("next_week")
    return TopicAnswer(topic="next_matchup", fact=f"Next: {other['name']}, {other['wins']}-{other['losses']}",
                       rows=rows, text=[blurb] if blurb else [],
                       block=next_matchup_block(rid, league_week) if league_week else None)


def _rankings_week(rankings: dict | None, week: int) -> dict | None:
    """The rankings of the built week. The file can run past the built week, so the week is picked by its number."""
    if rankings is None:
        return None
    return next((w for w in rankings["weeks"] if w["week"] == week), None)


def _movement(move: int) -> str:
    return f"up {move}" if move > 0 else f"down {-move}" if move < 0 else "no change"


def _power_rankings(rid: int, ranked: dict | None) -> TopicAnswer | None:
    if ranked is None:
        return None
    rows_by_rank = sorted(ranked["rows"], key=lambda r: r["rank"])
    row = next((r for r in rows_by_rank if r["roster_id"] == rid), None)
    if row is None:
        return None
    # The team and the team on each side of it, so the Answer shows the gap above and below.
    at = rows_by_rank.index(row)
    near = rows_by_rank[max(at - 1, 0):at + 2]
    rows = [Row(label=r["name"], value=ordinal(r["rank"]), note=f"{r['wins']}-{r['losses']}",
                roster_id=r["roster_id"], you=r is row) for r in near]
    stats = [Stat(label="Rank", value=ordinal(row["rank"])),
             Stat(label="Move", value=_movement(row["movement"]).capitalize()),
             Stat(label="Record", value=f"{row['wins']}-{row['losses']}")]
    text = " ".join(sentence["text"] for sentence in row["blurb"])
    return TopicAnswer(topic="power_rankings", fact=f"{ordinal(row['rank'])}, {_movement(row['movement'])}",
                       stats=stats, rows=rows, text=[text] if text else [], block=rank_movers_block(rid, ranked))


def _playoff_race(rid: int, ranked: dict | None, page: dict) -> TopicAnswer | None:
    if ranked is None:
        return None
    with_odds = sorted((r for r in ranked["rows"] if r.get("odds")), key=lambda r: -r["odds"]["playoff"])
    row = next((r for r in with_odds if r["roster_id"] == rid), None)
    if row is None:
        return None
    odds = row["odds"]
    fact = {"in": f"Clinched, seed {odds['seed']}", "out": f"Out, {odds['playoff']}% playoff odds"}.get(
        odds["status"], f"{odds['playoff']}% playoff odds")
    stats = [Stat(label="Playoff odds", value=f"{odds['playoff']}%"), Stat(label="Bye odds", value=f"{odds['bye']}%"),
             Stat(label="Seed", value=str(odds["seed"]))]
    standing = next((t["standing"] for t in page["table"] if t["team"]["roster_id"] == rid), None)
    if standing is not None:
        stats.append(Stat(label="Games from the cut", value=f"{standing['games_from_cut']:+d}"))
    at = with_odds.index(row)
    near = with_odds[max(at - 1, 0):at + 2]
    rows = [Row(label=r["name"], value=f"{r['odds']['playoff']}%", note=f"Seed {r['odds']['seed']}",
                roster_id=r["roster_id"], you=r is row) for r in near]
    return TopicAnswer(topic="playoff_race", fact=fact, stats=stats, rows=rows, block=ladder_block(rid, page, ranked))


def _your_season(rid: int, page: dict, managers: dict | None, league_week: Week | None) -> TopicAnswer | None:
    entry = next((t for t in page["table"] if t["team"]["roster_id"] == rid), None)
    if entry is None:
        return None
    standing, count = entry["standing"], len(page["table"])
    record = f"{standing['wins']}-{standing['losses']}"
    stats = [Stat(label="Record", value=record), Stat(label="Standing", value=f"{ordinal(standing['rank'])} of {count}"),
             Stat(label="Points", value=_points(standing["points_for"]))]
    rows: list[Row] = []
    text: list[str] = []
    manager = next((m for m in (managers or {}).get("managers", []) if m["roster_id"] == rid), None)
    if manager is not None:
        if manager.get("grade"):
            stats.append(Stat(label="Roster grade", value=manager["grade"]["letter"]))
            if manager["grade"].get("read"):
                text.append(manager["grade"]["read"])
        rows = [Row(label=p["name"], value=_points(p["points"]), note=f"{p['position']} · {p['per_game']:g} a game")
                for p in manager["top_performers"][:3]]
    return TopicAnswer(topic="your_season", fact=f"{record}, {ordinal(standing['rank'])} of {count}", stats=stats,
                       rows=rows, text=text, block=schedule_block(rid, page, league_week) if league_week else None)


def _leaders_trades(rid: int, page: dict) -> TopicAnswer:
    name = page["teams"][str(rid)]["name"]
    trades = page["trades"]
    mine = sorted(((row, group["position"]) for group in page["leaders"] for row in group["rows"]
                   if row["team"] == name), key=lambda pair: pair[0]["rank"])
    # A leader of Your team makes the fact. With none, the count of trades does.
    fact = (f"{mine[0][0]['player']}, {ordinal(mine[0][0]['rank'])} at {mine[0][1]}" if mine
            else f"{len(trades)} {'trade' if len(trades) == 1 else 'trades'} this week")
    # The Topic has no block. Its text opens with a markdown list of the top scorer at each position, which the text
    # block of the site draws as a list, so the list takes the place of the rows and the leaders show once.
    leaders = "\n".join(f"- **{group['position']}** {group['rows'][0]['player']}, "
                         f"{_points(group['rows'][0]['points'])}, {group['rows'][0]['team']}"
                         for group in page["leaders"] if group["rows"])
    stats = [Stat(label="Trades", value=str(len(trades))),
             Stat(label="Your leaders", value=str(len(mine)))]
    blurb = page["blurbs"].get("position_leaders")
    text = [part for part in (leaders, blurb) if part]
    return TopicAnswer(topic="leaders_trades", fact=fact, stats=stats, text=text)


def team_answers(rid: int, page: dict, rankings: dict | None, managers: dict | None,
                 league_week: Week | None = None) -> list[TopicAnswer]:
    """The league Answers of one team. A Topic with no data in the build, such as no next game, has no Answer.
    The matchup cards and the schedule strip read the parsed raw `league_week`. With None, those Topics have no block."""
    ranked = _rankings_week(rankings, page["week"])
    answers = [_week_recap(rid, page), _last_matchup(rid, page, league_week), _next_matchup(rid, page, league_week),
               _power_rankings(rid, ranked), _playoff_race(rid, ranked, page), _your_season(rid, page, managers, league_week),
               _leaders_trades(rid, page)]
    return [answer for answer in answers if answer is not None]


def write_topics(site_dir: Path, season: int, week: int, league_week: Week | None = None) -> Path | None:
    """Write topics.json beside the page.json of the week from the files of the build folder `site_dir` and the
    parsed raw week `league_week`, which holds the lineups. None when the week has no page.json."""
    folder = site_week_dir(site_dir, season, week)
    page = _read(folder / "page.json")
    if page is None:
        return None
    rankings = _read(site_dir / str(season) / "rankings.json")
    managers = _read(site_dir / str(season) / "managers.json")
    body = TopicsFile(season=season, week=week, teams={
        key: team_answers(int(key), page, rankings, managers, league_week) for key in sorted(page["teams"], key=int)})
    out = folder / TOPICS_FILE
    write_bytes_atomic(out, (body.model_dump_json(indent=2) + "\n").encode("utf-8"))
    return out


def write_topics_or_warn(site_dir: Path, season: int, week: int, league_week: Week | None = None) -> None:
    """Write topics.json. The page is built by now, so a bad input only logs a warning."""
    try:
        write_topics(site_dir, season, week, league_week)
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as err:
        log.warning("%s not written for week %d: %s", TOPICS_FILE, week, err)
