"""
Fetch the weekly trade value chart image, read it with Claude, and match its rows to players.
The parsed read is cached per week, so the image read runs once.
"""
import base64
import io
import json
import logging
import os
import re
import tempfile
from collections.abc import Callable, Iterable
from datetime import date, datetime, timedelta
from pathlib import Path

import anthropic
import httpx
from PIL import Image
from pydantic import BaseModel, ValidationError

from cornerstone.models import ChartRead, ChartValues, PlayerLine
from cornerstone.nflverse import download
from cornerstone.trades import default_cutoff
from cornerstone.writer import MODEL, RefusalError, WriterError, _get_client

logger = logging.getLogger(__name__)

# The WordPress media API lists every weekly file of the half PPR redraft chart.
MEDIA_URL = "https://peakedinhighskool.com/wp-json/wp/v2/media?search=1QB0.5PPR4pt&_fields=date,source_url&per_page=100"
FILE_DATE = re.compile(r"1QB0\.5PPR4pt_(\d{8})\.png$")
# WordPress.com turns away a client with no browser User-Agent.
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
TIMEOUT_SECONDS = 60
CHART_PROMPT = (
    "These images are consecutive strips of one trade value chart, from top to bottom. Each strip repeats "
    "about 80 pixels of the one before. Give the week number and the date from the header. Then give every "
    "player row in order, from the top of the first strip to the bottom of the last: the trade value, the "
    "name, and the position (RB, WR, TE, or QB) of the column that holds the name. Go row by row, and left "
    "to right inside a row. Copy each name as it is written."
)
# A chart older than this is not a stand-in for the week: the market moved.
STALE_DAYS = 14

_SUFFIXES = {"jr", "sr", "ii", "iii", "iv"}
POSITIONS = {"RB", "WR", "TE", "QB"}

# Claude downsizes an image to 1568 pixels on its long edge, so the 4700 pixel sheet would blur.
# Strips of this height stay sharp. The overlap keeps a row that sits on a cut whole in one strip.
STRIP_HEIGHT = 1000
STRIP_OVERLAP = 80

# (strips, output_model) -> parsed output. Tests pass a fake in place of Claude.
ChartReader = Callable[[list[bytes], type[BaseModel]], BaseModel]


def http_get(url: str) -> bytes:
    response = httpx.get(url, headers={"User-Agent": USER_AGENT}, follow_redirects=True, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.content


def chart_dir(repo: Path) -> Path:
    return repo / "data" / "cache" / "charts"


def _file_for_week(listing: list[dict], start: date, end: date) -> str | None:
    """The newest file whose filename date is on or after start and before end."""
    dated = []
    for item in listing:
        match = FILE_DATE.search(item["source_url"])
        if match:
            chart_date = datetime.strptime(match.group(1), "%Y%m%d").date()
            if start <= chart_date < end:
                dated.append((chart_date, item["source_url"]))
    return max(dated)[1] if dated else None


def _newest_fresh_png(charts: Path, now: datetime) -> Path | None:
    """The most recent cached week PNG that is 14 days old or less, by file time."""
    fresh = [p for p in charts.glob("week-*.png")
             if now.timestamp() - p.stat().st_mtime <= timedelta(days=STALE_DAYS).total_seconds()]
    return max(fresh, key=lambda p: p.stat().st_mtime, default=None)


def fetch_chart(season_start: date, week: int, charts: Path, fetch: Callable[[str], bytes] = http_get,
                now: datetime | None = None) -> Path | None:
    """The cached PNG of the week. It never raises: an outage gives the newest fresh PNG or None."""
    path = charts / f"week-{week:02d}.png"
    # A PNG that is in the cache wins, so a hand placed file stays and the build never re-fetches.
    if path.exists():
        return path
    now = now or datetime.now().astimezone()
    start = default_cutoff(season_start, week).date()
    end = default_cutoff(season_start, week + 1).date()
    try:
        url = _file_for_week(json.loads(fetch(MEDIA_URL)), start, end)
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as error:
        logger.warning("The chart list failed (%s)", error)
        return _fallback(charts, now)
    if url is None:
        logger.warning("The site lists no chart for week %d, so the week gets no trade values", week)
        return None
    if download(url, path, fetch=fetch) is None:
        return _fallback(charts, now)
    return path


def _fallback(charts: Path, now: datetime) -> Path | None:
    stand_in = _newest_fresh_png(charts, now)
    if stand_in is None:
        logger.warning("The chart fetch failed and no cached chart is %d days old or less", STALE_DAYS)
    else:
        logger.warning("The chart fetch failed, so the cached chart %s stands in", stand_in.name)
    return stand_in


def claude_read(strips: list[bytes], output_model: type[BaseModel]) -> BaseModel:
    """Send the strips in order, then one text block, through the writer's client and parse path."""
    content = [{"type": "image",
                "source": {"type": "base64", "media_type": "image/png", "data": base64.b64encode(s).decode()}}
               for s in strips]
    content.append({"type": "text", "text": CHART_PROMPT})
    response = _get_client().messages.parse(
        model=MODEL,
        max_tokens=16000,
        messages=[{"role": "user", "content": content}],
        output_format=output_model,
    )
    if response.stop_reason == "refusal":
        raise RefusalError(f"Claude refused to read the chart as {output_model.__name__}.")
    if response.parsed_output is None:
        raise WriterError(f"Claude gave no parsed output for {output_model.__name__}.")
    return response.parsed_output


def cut_strips(png: bytes) -> list[bytes]:
    """The sheet as PNG strips from top to bottom, each overlapping the one before."""
    sheet = Image.open(io.BytesIO(png))
    strips = []
    top = 0
    while True:
        bottom = min(top + STRIP_HEIGHT, sheet.height)
        out = io.BytesIO()
        sheet.crop((0, top, sheet.width, bottom)).save(out, format="PNG")
        strips.append(out.getvalue())
        if bottom == sheet.height:
            return strips
        top = bottom - STRIP_OVERLAP


def read_chart(png: bytes, read: ChartReader) -> ChartRead:
    """Send every strip to the read in one call. A row in the overlap shows twice, so the first one stays."""
    parsed = read(cut_strips(png), ChartRead)
    seen = set()
    rows = []
    for row in parsed.rows:
        key = name_key(row.name, row.position)
        if key not in seen:
            seen.add(key)
            rows.append(row)
    return parsed.model_copy(update={"rows": rows})


def guard_results(read: ChartRead, week: int, prior_rows: int | None) -> dict[str, bool]:
    """Each guard against a misread image, by name. A week with a failed guard gets no values."""
    values = [row.value for row in read.rows]
    return {
        "header week": read.week == week,
        "values never rise": all(b <= a for a, b in zip(values, values[1:])),
        "values are half points from 0 to 100": all(0 <= v <= 100 and v * 2 == int(v * 2) for v in values),
        "positions are RB, WR, TE, or QB": all(row.position in POSITIONS for row in read.rows),
        # A missing prior week passes: the first chart of a season has nothing to compare with.
        "row count within 10 percent of the prior week": prior_rows is None
        or abs(len(values) - prior_rows) <= prior_rows * 0.1,
    }


def name_key(name: str, position: str) -> str:
    """Letters only, lowercase, no Jr, Sr, II, III, or IV suffix, then the position."""
    words = name.split()
    # The suffix goes before the letters filter, or "Harrison Jr." would keep a stray "jr".
    if len(words) > 1 and words[-1].replace(".", "").lower() in _SUFFIXES:
        words.pop()
    return re.sub(r"[^a-z]", "", "".join(words).lower()) + position


def match_chart(read: ChartRead, lines: Iterable[PlayerLine]) -> ChartValues:
    """Run from each league player to the chart, never the other way, so two NFL players with one name never collide."""
    by_key = {name_key(row.name, row.position): row.value for row in read.rows}
    values = {}
    for line in lines:
        key = name_key(line.name, line.position)
        if key in by_key:
            values[line.player_id] = by_key[key]
    return ChartValues(week=read.week, date=read.date, values=values)


def _saved_read(path: Path) -> ChartRead | None:
    if not path.exists():
        return None
    try:
        return ChartRead.model_validate_json(path.read_text(encoding="utf-8"))
    except ValidationError as error:
        logger.warning("The parsed chart %s does not parse (%s), so the image is read again", path, error)
        return None


def load_chart(repo: Path, season_start: date, week: int, fetch: Callable[[str], bytes] = http_get,
               read: ChartReader = claude_read, now: datetime | None = None) -> tuple[int, ChartRead] | None:
    """The chart week and its parsed read, or None. It never raises, so a build goes on without values.

    After an outage the chart week can be an earlier week than the one asked for.
    """
    charts = chart_dir(repo)
    cached = _saved_read(charts / f"week-{week:02d}.json")
    if cached:
        return week, cached
    png = fetch_chart(season_start, week, charts, fetch, now)
    if png is None:
        return None
    chart_week = int(png.stem.removeprefix("week-"))
    cached = _saved_read(charts / f"week-{chart_week:02d}.json")
    if cached:
        return chart_week, cached
    try:
        parsed = read_chart(png.read_bytes(), read)
    except (RefusalError, WriterError, anthropic.APIError, ValidationError) as error:
        logger.warning("The read of %s failed (%s)", png.name, error)
        return None
    prior = _saved_read(charts / f"week-{chart_week - 1:02d}.json")
    failed = [name for name, ok in guard_results(parsed, chart_week, len(prior.rows) if prior else None).items()
              if not ok]
    if failed:
        # The PNG stays for a hand check. No JSON is written, so the next run reads the image again.
        logger.warning("The read of %s failed the guards: %s", png.name, "; ".join(failed))
        return None
    _write_json(charts / f"week-{chart_week:02d}.json", parsed)
    return chart_week, parsed


def _write_json(path: Path, parsed: ChartRead) -> None:
    # A temp file then a replace, so a stopped write never leaves a half file that the next run reads.
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(parsed.model_dump_json(indent=2))
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def chart_values(repo: Path, season_start: date, week: int, lines: Iterable[PlayerLine],
                 fetch: Callable[[str], bytes] = http_get, read: ChartReader = claude_read,
                 now: datetime | None = None) -> ChartValues | None:
    """The trade values of the players the chart lists, or None when the week has no good chart."""
    loaded = load_chart(repo, season_start, week, fetch, read, now)
    return match_chart(loaded[1], lines) if loaded else None
