"""
Renders the week page and the home page from a bundle and its blurbs.
Templates get one plain context dict, so they hold layout and no logic.
"""
import hashlib
import html
import json
import logging
import re
import shutil
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlparse

import httpx
from jinja2 import Environment, FileSystemLoader
from pydantic import TypeAdapter

from cornerstone.facts_league import LEADER_POSITIONS
from cornerstone.models import Blurb, Bundle, MatchupFacts, PlayerLine
from cornerstone.sheet import AWARD_TITLES, fmt

PACKAGE_DIR = Path(__file__).parent
STATIC_DIR = PACKAGE_DIR / "static"
DEFAULT_AVATAR = "static/avatar-default.svg"
DEFAULT_HEADSHOT = "static/headshot-default.svg"
# The week page sits two folders below the site root, so it reaches the default silhouette with this path.
DEFAULT_HEADSHOT_PATH = f"../../{DEFAULT_HEADSHOT}"
AVATAR_TIMEOUT = 10
# The order of the four tiles on the page.
TILE_KEYS = ("top_scorer", "mvb", "underperformer", "overachiever")
# Bump this when a key in page.json changes meaning or leaves. A new key does not need a bump.
PAGE_SCHEMA_VERSION = 1
SUMMARY_META = re.compile(r'<meta name="cornerstone-summary" content="([^"]*)">')

log = logging.getLogger(__name__)

_env = Environment(loader=FileSystemLoader(PACKAGE_DIR / "templates"), autoescape=True)
_env.filters["num"] = fmt
_env.filters["gap"] = lambda x: f"+{fmt(x)}" if x >= 0 else f"−{fmt(-x)}"


def _short_name(line: PlayerLine) -> str:
    first, _, rest = line.name.partition(" ")
    return f"{first[0]}. {rest}" if rest else line.name


_env.filters["short_name"] = _short_name


def _sides(f: MatchupFacts, teams: dict) -> list[dict]:
    """The two sides of a matchup, winner first. A tie has neither flag set and keeps the roster order.
    The facts hold the top scorer of both rosters, so a tie still finds both teams."""
    if f.winner is not None:
        order = [(f.winner, f.score_w), (f.loser, f.score_l)]
    else:
        order = [(rid, f.score_w) for rid in sorted(f.top_scorer)]
    return [
        {"team": teams[rid], "score": score, "top": f.top_scorer.get(rid),
         "winner": rid == f.winner, "loser": rid == f.loser}
        for rid, score in order
    ]


def _tile(bundle: Bundle, key: str, teams: dict) -> dict:
    # A reader may not know the acronym, so the tile spells out MVB.
    title = "MVB · Most Valuable Benchwarmer" if key == "mvb" else AWARD_TITLES[key]
    award = next((a for a in bundle.data.awards if a.key == key), None)
    if award is None:
        return {"title": title, "missing": True}
    projection = award.line.projection if key in ("underperformer", "overachiever") else None
    tile = {
        "title": title, "missing": False, "player": award.line.name, "player_id": award.line.player_id,
        "points": award.line.points,
        "team": teams[award.roster_id].name, "projection": projection,
    }
    return tile


def _median(bundle: Bundle, teams: dict) -> dict:
    m = bundle.data.median
    scores = {}
    for f in bundle.data.matchups:
        for side in _sides(f, teams):
            scores[side["team"].roster_id] = side["score"]
    top = max(scores.values())
    bars = [
        {"team": teams[rid], "score": score, "above": rid in m.above, "pct": round(score / top * 100, 1)}
        for rid, score in sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    ]
    above_id, above_gap = m.closest_above
    below_id, below_gap = m.closest_below
    return {
        "value": m.median,
        "above": {"team": teams[above_id], "gap": above_gap},
        "below": {"team": teams[below_id], "gap": -below_gap},
        "bars": bars,
        "line_pct": round(m.median / top * 100, 1),
    }


def _trades(bundle: Bundle, teams: dict, headshots: dict[str, str]) -> list[dict]:
    """One card per trade, with a side per team. Each side holds a chip per player it got and a row per pick."""
    cards = []
    for trade in bundle.data.trades:
        sides = []
        for rid in trade.roster_ids:
            players = []
            for pid, owner in trade.adds.items():
                if owner != rid:
                    continue
                players.append({
                    # A player with no lineup line has no name in the week data, so he shows under a plain label.
                    "name": bundle.data.trade_players.get(pid, "An unlisted player"),
                    "headshot": headshots.get(pid, DEFAULT_HEADSHOT_PATH),
                })
            picks = [f"{p.season} round {p.round} pick" for p in trade.draft_picks if p.owner_id == rid]
            sides.append({"team": teams[rid], "players": players, "picks": picks})
        cards.append({"sides": sides})
    return cards


def _leaders(bundle: Bundle, teams: dict) -> list[dict]:
    """One board per position, in lineup order, each with its leaders from first to third."""
    # All five boards show, even when no one started at a position.
    boards = {position: {"position": position, "rows": []} for position in LEADER_POSITIONS}
    for lead in bundle.data.leaders:
        boards[lead.position]["rows"].append({
            "rank": lead.rank,
            "player": lead.line.name,
            "player_id": lead.line.player_id,
            "nfl_team": lead.line.nfl_team,
            "points": lead.line.points,
            "team": teams[lead.roster_id].name,
        })
    return list(boards.values())


def _asset_version() -> str:
    """Return a short content hash of the stylesheet and the script."""
    # A browser cache keeps a stylesheet past a publish because the path never changes.
    # The stamp changes with the file, so the browser fetches a fresh copy.
    digest = hashlib.sha256()
    for name in ("style.css", "app.js"):
        digest.update((STATIC_DIR / name).read_bytes())
    return digest.hexdigest()[:8]


def build_context(
    bundle: Bundle, blurbs: dict[str, Blurb], avatars: dict[int, str], headshots: dict[str, str],
) -> dict:
    """Turn the bundle into the values the templates read."""
    data = bundle.data
    teams = data.teams
    text = {key: " ".join(s.text for s in b.sentences) for key, b in blurbs.items()}
    pick_facts = next(f for f in data.matchups if f.matchup_id == data.pick.matchup_id)
    pick_sides = _sides(pick_facts, teams)
    game_changer = next((a for a in data.awards if a.key == "game_changer"), None)

    matchups = [
        {
            "id": f.matchup_id,
            "sides": _sides(f, teams),
            "is_pick": f.matchup_id == data.pick.matchup_id,
            "recap": text.get(f"recap_{f.matchup_id}", ""),
        }
        for f in sorted(data.matchups, key=lambda f: f.matchup_id)
    ]
    return {
        "asset_version": _asset_version(),
        "season": data.season,
        "week": data.week,
        "dates": data.dates,
        "publish_date": data.publish_date,
        "teams": teams,
        "pick": {"reason": data.pick.reason, "sides": pick_sides},
        "motw": pick_facts,
        "game_changer": {"award": game_changer, "team": teams[game_changer.roster_id].name} if game_changer else None,
        "awards": [_tile(bundle, key, teams) for key in TILE_KEYS],
        "leaders": _leaders(bundle, teams),
        "trades": _trades(bundle, teams, headshots),
        "matchups": matchups,
        "median": _median(bundle, teams),
        "table": [{"standing": s, "team": teams[s.roster_id]} for s in data.table],
        "next": [
            {"a": teams[n.a], "b": teams[n.b], "must_watch": n.must_watch, "reason": n.reason}
            for n in data.next
        ],
        "blurbs": text,
        "avatars": avatars,
        "headshots": headshots,
        "summary": f"Week {data.week} · {data.dates} · {pick_sides[0]['team'].name} vs {pick_sides[1]['team'].name}",
        "root": "../../",
    }


def _download_bytes(url: str) -> bytes | None:
    """Fetch one image. Return None on any failure, so a build never stops on one avatar."""
    try:
        resp = httpx.get(url, timeout=AVATAR_TIMEOUT, follow_redirects=True)
    except Exception as exc:
        log.warning("Image fetch failed for %s: %s", url, exc)
        return None
    if resp.status_code != 200:
        log.warning("Image fetch failed for %s: status %s", url, resp.status_code)
        return None
    return resp.content


def _download_avatars(bundle: Bundle, avatar_dir: Path, fetch_bytes: Callable[[str], bytes | None]) -> dict[int, str]:
    """Save each avatar. A missing or failed download falls back to the default image."""
    paths = {}
    for rid, team in bundle.data.teams.items():
        paths[rid] = f"../../{DEFAULT_AVATAR}"
        if team.avatar_url is None:
            continue
        content = fetch_bytes(team.avatar_url)
        if content is None:
            continue
        ext = Path(urlparse(team.avatar_url).path).suffix.lstrip(".") or "jpg"
        avatar_dir.mkdir(parents=True, exist_ok=True)
        (avatar_dir / f"{rid}.{ext}").write_bytes(content)
        paths[rid] = f"avatars/{rid}.{ext}"
    return paths


def is_def(player_id: str) -> bool:
    """Whether a player ID is a DEF.
    Sleeper gives a DEF the team abbreviation as its player ID, and a player a numeric ID."""
    return not player_id.isdigit()


def headshot_url(player_id: str, is_def: bool) -> str:
    """The Sleeper CDN URL for a player's headshot.
    A DEF has no headshot, and its player ID is the team abbreviation, so it maps to the team logo."""
    if is_def:
        return f"https://sleepercdn.com/images/team_logos/nfl/{player_id.lower()}.png"
    return f"https://sleepercdn.com/content/nfl/players/{player_id}.jpg"


def _headshot_players(bundle: Bundle) -> list[tuple[str, bool]]:
    """The player ID and the DEF flag of each player who shows a headshot on the page."""
    data = bundle.data
    lines = [a.line for a in data.awards if a.key == "game_changer" or a.key in TILE_KEYS]
    lines += [lead.line for lead in data.leaders]
    players = [(line.player_id, is_def(line.player_id)) for line in lines]
    # A trade holds player IDs and no lineup lines, so the ID alone tells a DEF apart.
    players += [(pid, is_def(pid)) for trade in data.trades for pid in trade.adds]
    return players


def _download_headshots(bundle: Bundle, headshot_dir: Path, fetch_bytes: Callable[[str], bytes | None]) -> dict[str, str]:
    """Save the headshot of each player on the Game Changer hero, the award tiles, the leader rows, and the trade cards.
    A failed download falls back to the default silhouette."""
    paths = {}
    for player_id, is_defense in _headshot_players(bundle):
        # A player can hold an award, a leader row, and a trade chip, so each player is fetched once.
        if player_id in paths:
            continue
        paths[player_id] = DEFAULT_HEADSHOT_PATH
        content = fetch_bytes(headshot_url(player_id, is_defense))
        if content is None:
            continue
        # The CDN serves PNG bytes, even under the .jpg name of a player URL.
        headshot_dir.mkdir(parents=True, exist_ok=True)
        (headshot_dir / f"{player_id}.png").write_bytes(content)
        paths[player_id] = f"headshots/{player_id}.png"
    return paths


def _saved_avatars(bundle: Bundle, week_dir: Path) -> dict[int, str]:
    """The avatar path of each team from the files that a past build saved. A missing file gets the default."""
    paths = {}
    for rid in bundle.data.teams:
        saved = next((week_dir / "avatars").glob(f"{rid}.*"), None)
        paths[rid] = f"avatars/{saved.name}" if saved else f"../../{DEFAULT_AVATAR}"
    return paths


def _saved_headshots(bundle: Bundle, week_dir: Path) -> dict[str, str]:
    """The headshot path of each player from the files that a past build saved. A missing file gets the default."""
    return {
        pid: f"headshots/{pid}.png" if (week_dir / "headshots" / f"{pid}.png").exists() else DEFAULT_HEADSHOT_PATH
        for pid, _ in _headshot_players(bundle)
    }


def _week_dir(site_dir: Path, bundle: Bundle) -> Path:
    """Return the week folder under the site folder. Make it if it is missing."""
    week_dir = site_dir / str(bundle.data.season) / f"week-{bundle.data.week:02d}"
    week_dir.mkdir(parents=True, exist_ok=True)
    return week_dir


def _write_page_json(context: dict, week_dir: Path) -> Path:
    """Write the render context as page.json, with the schema version first."""
    # The context holds Pydantic models and dates. TypeAdapter(dict) turns them into plain values.
    # The int keys of the teams and avatars become strings, as JSON needs.
    plain = TypeAdapter(dict).dump_python(context, mode="json")
    body = {"schema_version": PAGE_SCHEMA_VERSION, **plain}
    out = week_dir / "page.json"
    out.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def render_page_json(bundle: Bundle, blurbs: dict[str, Blurb], site_dir: Path) -> Path:
    """Write page.json for a week that a past build saved. It fetches nothing and keeps the page and images."""
    week_dir = _week_dir(site_dir, bundle)
    context = build_context(bundle, blurbs, _saved_avatars(bundle, week_dir), _saved_headshots(bundle, week_dir))
    return _write_page_json(context, week_dir)


def _copy_static(site_dir: Path) -> None:
    shutil.copytree(STATIC_DIR, site_dir / "static", dirs_exist_ok=True)


def render_week(
    bundle: Bundle,
    blurbs: dict[str, Blurb],
    site_dir: Path,
    fetch_bytes: Callable[[str], bytes | None] = _download_bytes,
) -> Path:
    """Write the week page and its page.json, and copy the static files. Return the page path."""
    week_dir = _week_dir(site_dir, bundle)
    avatars = _download_avatars(bundle, week_dir / "avatars", fetch_bytes)
    headshots = _download_headshots(bundle, week_dir / "headshots", fetch_bytes)
    page = week_dir / "index.html"
    context = build_context(bundle, blurbs, avatars, headshots)
    page.write_text(_env.get_template("week.html").render(context))
    _write_page_json(context, week_dir)
    _copy_static(site_dir)
    return page


def render_index(site_dir: Path) -> Path:
    """Write the home page. It lists every published week, newest first."""
    weeks = []
    for page in site_dir.glob("*/week-*/index.html"):
        found = SUMMARY_META.search(page.read_text())
        if not found:
            continue
        season, week = int(page.parent.parent.name), int(page.parent.name.removeprefix("week-"))
        label, dates, teams = html.unescape(found.group(1)).split(" · ", 2)
        weeks.append({"key": (season, week), "href": f"{season}/week-{week:02d}/",
                      "label": label, "dates": dates, "teams": teams})
    weeks.sort(key=lambda w: w["key"], reverse=True)
    out = site_dir / "index.html"
    out.write_text(_env.get_template("index.html").render(weeks=weeks, root="", asset_version=_asset_version()))
    _copy_static(site_dir)
    return out
