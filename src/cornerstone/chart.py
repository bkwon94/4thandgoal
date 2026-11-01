"""
Fetch the weekly trade value chart image, read it with Claude, and match its rows to players.
The module caches the parsed read per week, so the image read runs once.
"""
import base64
import io
import json
import logging
import re
from collections.abc import Callable, Iterable
from datetime import date, datetime
from functools import partial
from pathlib import Path
from typing import NamedTuple

import anthropic
import httpx
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, ValidationError

from cornerstone.claude_errors import RefusalError, WriterError
from cornerstone.files import write_bytes_atomic
from cornerstone.models import ChartRead, ChartValues, PlayerLine
from cornerstone.paths import chart_image, chart_read, charts_dir, week_from_label
from cornerstone.trades import cutoff_date

logger = logging.getLogger(__name__)

# The WordPress media API lists every weekly file of the half-PPR redraft chart.
MEDIA_URL = "https://peakedinhighskool.com/wp-json/wp/v2/media?search=1QB0.5PPR4pt&_fields=date,source_url&per_page=100"
FILE_DATE = re.compile(r"1QB0\.5PPR4pt_(\d{8})\.png$")
# WordPress.com turns away a client with no browser User-Agent.
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/130.0 Safari/537.36"
)
TIMEOUT_SECONDS = 60
# Every PNG file starts with these eight bytes. An error page served with a 200 status does not.
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
CHART_PROMPT = (
    "These images are consecutive strips of one trade value chart, from top to bottom. "
    "Each strip repeats about 80 pixels of the strip before it. "
    "Give the week number and the date from the header. "
    "Then give every player row in order, from the top of the first strip to the bottom of the last. "
    "For each row, give the trade value, the name, and the position. "
    "The position is the column that holds the name. "
    "The positions are RB, WR, TE, and QB. "
    "Go row by row. "
    "Inside a row, go from left to right. "
    "Copy each name exactly as the chart spells it."
)
# After an outage, a cached chart stands in only when it is at most this many weeks older than the
# week. An older chart is not a stand-in for the week: the market moved.
STAND_IN_WEEKS = 2

# The real sheet has about 130 rows. A read with far fewer missed part of the image.
MIN_ROWS = 100

_SUFFIXES = {"jr", "sr", "ii", "iii", "iv"}
POSITIONS = {"RB", "WR", "TE", "QB"}

# Claude downsizes an image to 1568 pixels on its long edge, so the 4700 pixel sheet would blur.
# Strips of this height stay sharp. The overlap keeps a row that sits on a cut whole in one strip.
STRIP_HEIGHT = 1000
STRIP_OVERLAP = 80

# (strips, output_model) -> parsed output. Tests pass a fake in place of Claude.
ChartReader = Callable[[list[bytes], type[BaseModel]], BaseModel]
# (content, output_model) -> parsed output: the writer's parse_call in a run.
# The caller passes it, so this module imports no writer and stays in the provider layer.
ParseCall = Callable[[list[dict], type[BaseModel]], BaseModel]


def http_get(url: str) -> bytes:
    response = httpx.get(url, headers={"User-Agent": USER_AGENT}, follow_redirects=True, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.content


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


def fetch_chart(season_start: date, week: int, repo: Path, fetch: Callable[[str], bytes] = http_get) -> Path | None:
    """The cached PNG of the week. It never raises: an outage gives the PNG of a recent earlier week or None."""
    path = chart_image(repo, week)
    # A PNG that is in the cache wins, so a hand-placed file stays and the build never re-fetches.
    if path.exists():
        return path
    start = cutoff_date(season_start, week)
    end = cutoff_date(season_start, week + 1)
    try:
        url = _file_for_week(json.loads(fetch(MEDIA_URL)), start, end)
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as error:
        logger.warning("The chart list failed (%s)", error)
        return _fallback(repo, week)
    if url is None:
        logger.warning("The site lists no chart for week %d, so the week gets no trade values", week)
        return None
    try:
        body = fetch(url)
    except httpx.HTTPError as error:
        logger.warning("The chart download of %s failed (%s)", url, error)
        return _fallback(repo, week)
    # A body that is not a PNG never goes into the cache, so the next run fetches again.
    if not body.startswith(PNG_SIGNATURE):
        logger.warning("The chart download of %s is not a PNG", url)
        return _fallback(repo, week)
    charts_dir(repo).mkdir(parents=True, exist_ok=True)
    write_bytes_atomic(path, body)
    return path


def _fallback(repo: Path, week: int) -> Path | None:
    """The cached PNG of the newest of the STAND_IN_WEEKS weeks before the week, never a later week."""
    for earlier in range(week - 1, week - 1 - STAND_IN_WEEKS, -1):
        stand_in = chart_image(repo, earlier)
        if stand_in.exists():
            logger.warning("The chart fetch failed, so the chart of week %d stands in for week %d", earlier, week)
            return stand_in
    logger.warning("The chart fetch failed and no chart of the %d weeks before week %d is cached",
                   STAND_IN_WEEKS, week)
    return None


def claude_read(strips: list[bytes], output_model: type[BaseModel], call: ParseCall) -> BaseModel:
    """Send the strips in order, then one text block, through `call`, the writer's client and parse path."""
    content = [{"type": "image",
                "source": {"type": "base64", "media_type": "image/png", "data": base64.b64encode(s).decode()}}
               for s in strips]
    content.append({"type": "text", "text": CHART_PROMPT})
    return call(content, output_model)


def claude_reader(call: ParseCall) -> ChartReader:
    """The Claude read of the chart through `call`. The CLI and the API pass the writer's parse_call."""
    return partial(claude_read, call=call)


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
    """Send every strip to the read in one call. A row in the overlap shows twice, so the first one stays.

    Two rows with one name key and two trade values both stay, so the overlap guard can fail them.
    """
    parsed = read(cut_strips(png), ChartRead)
    seen = set()
    rows = []
    for row in parsed.rows:
        key = (name_key(row.name, row.position), row.value)
        if key not in seen:
            seen.add(key)
            rows.append(row)
    return parsed.model_copy(update={"rows": rows})


def guard_results(chart: ChartRead, week: int, prior_rows: int | None) -> dict[str, bool]:
    """Each guard against a misread image, by name. A week with a failed guard gets no trade values."""
    values = [row.value for row in chart.rows]
    return {
        "header week": chart.week == week,
        "trade values never rise": all(b <= a for a, b in zip(values, values[1:])),
        "trade values are half points from 0 to 100": all(0 <= v <= 100 and v * 2 == int(v * 2) for v in values),
        "positions are RB, WR, TE, or QB": all(row.position in POSITIONS for row in chart.rows),
        f"at least {MIN_ROWS} rows": len(values) >= MIN_ROWS,
        # The read keeps an overlap row twice only when its two trade values differ.
        "overlap rows agree": len({name_key(row.name, row.position) for row in chart.rows}) == len(chart.rows),
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


def match_chart(chart: ChartRead, lines: Iterable[PlayerLine]) -> ChartValues:
    """Run from each league player to the chart, never the other way, so two NFL players with one name never collide."""
    by_key = {name_key(row.name, row.position): row.value for row in chart.rows}
    values = {}
    for line in lines:
        key = name_key(line.name, line.position)
        if key in by_key:
            values[line.player_id] = by_key[key]
    return ChartValues(week=chart.week, date=chart.date, values=values)


def _saved_read(path: Path) -> ChartRead | None:
    if not path.exists():
        return None
    try:
        return ChartRead.model_validate_json(path.read_text(encoding="utf-8"))
    # A file that is not UTF-8 or not JSON is a bad cache, the same as a malformed one.
    except (ValidationError, UnicodeDecodeError, ValueError) as error:
        logger.warning("The parsed chart %s does not parse (%s), so the image is read again", path, error)
        return None


def _current_saved_read(repo: Path, week: int) -> ChartRead | None:
    """The saved read of the week, unless a hand-placed PNG is newer than it. A newer PNG wins and is read again."""
    json_path, png = chart_read(repo, week), chart_image(repo, week)
    if png.exists() and json_path.exists() and png.stat().st_mtime > json_path.stat().st_mtime:
        return None
    return _saved_read(json_path)


def saved_chart_read(repo: Path, week: int) -> ChartRead | None:
    """The saved read of the week under the cache rules, or None. It never fetches or reads an image."""
    return _current_saved_read(repo, week)


def _prior_row_count(repo: Path, week: int) -> int | None:
    """The row count of the saved read of the week before, or None when no good read is saved."""
    prior = _saved_read(chart_read(repo, week - 1))
    return len(prior.rows) if prior else None


class ChartCheck(NamedTuple):
    """The chart week, its parsed read, and each guard by name."""
    week: int
    chart: ChartRead
    guards: dict[str, bool]


def _read_png(png: Path, read: ChartReader) -> ChartRead | None:
    try:
        return read_chart(png.read_bytes(), read)
    except (UnidentifiedImageError, OSError) as error:
        logger.warning("The chart %s does not open as an image (%s)", png.name, error)
    except (RefusalError, WriterError, anthropic.APIError, ValidationError) as error:
        logger.warning("The read of %s failed (%s)", png.name, error)
    return None


def check_chart(repo: Path, season_start: date, week: int, fetch: Callable[[str], bytes] = http_get, *,
                read: ChartReader) -> ChartCheck | None:
    """The chart week, its parsed read, and the guard results, or None when no read exists. It never raises.

    After an outage the chart week can be an earlier week than the one asked for.
    """
    chart_week = week
    parsed = _current_saved_read(repo, week)
    fresh = False
    if parsed is None:
        png = fetch_chart(season_start, week, repo, fetch)
        if png is None:
            return None
        chart_week = week_from_label(png.stem)
        parsed = _current_saved_read(repo, chart_week)
        if parsed is None:
            parsed = _read_png(png, read)
            if parsed is None:
                return None
            fresh = True
    # A saved read passed the guards before the save. A second check catches a guard added since then.
    guards = guard_results(parsed, chart_week, _prior_row_count(repo, chart_week))
    # On a failed guard the PNG stays for a hand check. No JSON is written, so the next run reads the image again.
    if fresh and all(guards.values()):
        _write_json(chart_read(repo, chart_week), parsed)
    return ChartCheck(chart_week, parsed, guards)


def load_chart(repo: Path, season_start: date, week: int, fetch: Callable[[str], bytes] = http_get, *,
               read: ChartReader) -> tuple[int, ChartRead] | None:
    """The chart week and its parsed read, or None. It never raises, so a build goes on without trade values.

    After an outage the chart week can be an earlier week than the one asked for.
    """
    check = check_chart(repo, season_start, week, fetch, read=read)
    if check is None:
        return None
    failed = [name for name, ok in check.guards.items() if not ok]
    if failed:
        logger.warning("The read of the week %d chart failed the guards: %s", check.week, "; ".join(failed))
        return None
    return check.week, check.chart


def _write_json(path: Path, parsed: ChartRead) -> None:
    write_bytes_atomic(path, parsed.model_dump_json(indent=2).encode("utf-8"))


def chart_values(repo: Path, season_start: date, week: int, lines: Iterable[PlayerLine],
                 fetch: Callable[[str], bytes] = http_get, *, read: ChartReader) -> ChartValues | None:
    """The trade values of the players the chart lists, or None when the week has no good chart."""
    loaded = load_chart(repo, season_start, week, fetch, read=read)
    return match_chart(loaded[1], lines) if loaded else None
