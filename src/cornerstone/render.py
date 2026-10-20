"""
Renders the week page and the home page from a bundle and its blurbs.
Templates get one plain context dict, so they hold layout and no logic.
"""
import html
import re
import shutil
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urlparse

import httpx
from jinja2 import Environment, FileSystemLoader

from cornerstone.models import Blurb, Bundle, MatchupFacts, PlayerLine
from cornerstone.sheet import AWARD_TITLES, fmt

PACKAGE_DIR = Path(__file__).parent
STATIC_DIR = PACKAGE_DIR / "static"
DEFAULT_AVATAR = "static/avatar-default.svg"
AVATAR_TIMEOUT = 10
# The order of the four tiles on the page.
TILE_KEYS = ("top_scorer", "mvb", "underperformer", "overachiever")
SUMMARY_META = re.compile(r'<meta name="cornerstone-summary" content="([^"]*)">')

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
    title = AWARD_TITLES[key]
    award = next((a for a in bundle.data.awards if a.key == key), None)
    if award is None:
        return {"title": title, "missing": True}
    projection = award.line.projection if key in ("underperformer", "overachiever") else None
    return {
        "title": title, "missing": False, "player": award.line.name, "points": award.line.points,
        "team": teams[award.roster_id].name, "projection": projection,
    }


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


def build_context(bundle: Bundle, blurbs: dict[str, Blurb], avatars: dict[int, str]) -> dict:
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
        "season": data.season,
        "week": data.week,
        "dates": data.dates,
        "publish_date": data.publish_date,
        "teams": teams,
        "pick": {"reason": data.pick.reason, "sides": pick_sides},
        "motw": pick_facts,
        "game_changer": {"award": game_changer, "team": teams[game_changer.roster_id].name} if game_changer else None,
        "awards": [_tile(bundle, key, teams) for key in TILE_KEYS],
        "matchups": matchups,
        "median": _median(bundle, teams),
        "table": [{"standing": s, "team": teams[s.roster_id]} for s in data.table],
        "next": [
            {"a": teams[n.a], "b": teams[n.b], "must_watch": n.must_watch, "reason": n.reason}
            for n in data.next
        ],
        "blurbs": text,
        "avatars": avatars,
        "summary": f"Week {data.week} · {data.dates} · {pick_sides[0]['team'].name} vs {pick_sides[1]['team'].name}",
        "root": "../../",
    }


def _download_bytes(url: str) -> bytes | None:
    """Fetch one image. Return None on any failure, so a build never stops on one avatar."""
    try:
        resp = httpx.get(url, timeout=AVATAR_TIMEOUT, follow_redirects=True)
    except Exception:
        return None
    return resp.content if resp.status_code == 200 else None


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


def _copy_static(site_dir: Path) -> None:
    shutil.copytree(STATIC_DIR, site_dir / "static", dirs_exist_ok=True)


def render_week(
    bundle: Bundle,
    blurbs: dict[str, Blurb],
    site_dir: Path,
    fetch_bytes: Callable[[str], bytes | None] = _download_bytes,
) -> Path:
    """Write the week page and copy the static files. Return the page path."""
    week_dir = site_dir / str(bundle.data.season) / f"week-{bundle.data.week:02d}"
    week_dir.mkdir(parents=True, exist_ok=True)
    avatars = _download_avatars(bundle, week_dir / "avatars", fetch_bytes)
    page = week_dir / "index.html"
    page.write_text(_env.get_template("week.html").render(build_context(bundle, blurbs, avatars)))
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
    out.write_text(_env.get_template("index.html").render(weeks=weeks, root=""))
    _copy_static(site_dir)
    return out
