"""
Tests for the trade value chart fetch, read, and match.
They fake the fetch and the read, so no test uses the network or Claude.
"""
import io
import json
from datetime import date

import httpx
import pytest
from PIL import Image

from cornerstone.writer import ClaudeWriter, WriterError, parse_call
from league.chart import (
    CHART_PROMPT,
    MEDIA_URL,
    PNG_SIGNATURE,
    STRIP_HEIGHT,
    STRIP_OVERLAP,
    chart_values,
    claude_read,
    claude_reader,
    cut_strips,
    fetch_chart,
    guard_results,
    load_chart,
    match_chart,
    read_chart,
    saved_chart_read,
)
from league.models import ChartRead, ChartRow, PlayerLine
from league.paths import charts_dir


def _line(player_id, name, position):
    return PlayerLine(player_id=player_id, name=name, position=position, nfl_team=None, points=0.0,
                      projection=None, season_avg=None, started=False, slot=None)


def _read(*rows):
    return ChartRead(week=6, date=date(2026, 10, 13),
                     rows=[ChartRow(value=v, name=n, position=p) for v, n, p in rows])


def test_match_handles_suffix_periods_apostrophe_and_hyphen():
    read = _read((40.0, "Ja'Marr Chase", "WR"), (30.0, "A.J. Brown", "WR"), (20.0, "Kenneth Walker", "RB"),
                 (10.0, "Marvin Harrison Jr.", "WR"), (5.0, "Amon-Ra St. Brown", "WR"))
    lines = [_line("1", "Ja'Marr Chase", "WR"), _line("2", "AJ Brown", "WR"),
             _line("3", "Kenneth Walker III", "RB"), _line("4", "Marvin Harrison", "WR"),
             _line("5", "Amon Ra St Brown", "WR"), _line("6", "Nobody Here", "TE")]
    chart = match_chart(read, lines)
    assert chart.values == {"1": 40.0, "2": 30.0, "3": 20.0, "4": 10.0, "5": 5.0}
    assert (chart.week, chart.date) == (6, date(2026, 10, 13))


def test_match_needs_the_same_position():
    read = _read((40.0, "Josh Allen", "QB"))
    assert match_chart(read, [_line("1", "Josh Allen", "LB")]).values == {}


def _letters(i):
    # The name key drops digits, so each made-up name spells its number in letters to stay unique.
    return "".join(chr(ord("a") + int(d)) for d in str(i))


def _rows(n, start=60.0):
    return [(start - i * 0.5, f"Player {_letters(i)}", "RB") for i in range(n)]


def _padded(*rows):
    """A read of the rows plus 100 more at the last value, so it passes the guard of at least 100 rows."""
    last = rows[-1][0]
    return _read(*rows, *((last, f"Pad {_letters(i)}", "TE") for i in range(100)))


def _failed(read, week=6, prior_rows=None):
    return [name for name, ok in guard_results(read, week, prior_rows).items() if not ok]


def test_guards_pass_a_good_read():
    assert _failed(_read(*_rows(100)), prior_rows=100) == []


def test_guard_header_week():
    assert _failed(_read(*_rows(100)), week=7) == ["header week"]


def test_guard_trade_values_never_rise():
    assert _failed(_padded((10.0, "A", "RB"), (10.5, "B", "WR"))) == ["trade values never rise"]


def test_guard_equal_trade_values_in_a_row_pass():
    assert _failed(_padded((10.0, "A", "RB"), (10.0, "B", "WR"))) == []


def test_guard_trade_values_are_half_points_from_0_to_100():
    for bad in (100.5, 10.25, -1.0):
        assert _failed(_padded((bad, "A", "RB"))) == ["trade values are half points from 0 to 100"]


def test_guard_positions():
    assert _failed(_padded((10.0, "A", "K"))) == ["positions are RB, WR, TE, or QB"]


def test_guard_row_count_within_10_percent_of_prior_week():
    assert _failed(_read(*_rows(135, 100.0)), prior_rows=150) == []
    assert _failed(_read(*_rows(134, 100.0)), prior_rows=150) == ["row count within 10 percent of the prior week"]
    assert _failed(_read(*_rows(166, 100.0)), prior_rows=150) == ["row count within 10 percent of the prior week"]


def test_guard_at_least_100_rows():
    assert _failed(_read()) == ["at least 100 rows"]
    assert _failed(_read(*_rows(99))) == ["at least 100 rows"]
    assert _failed(_read(*_rows(100))) == []


def _png(height, width=40):
    out = io.BytesIO()
    Image.new("RGB", (width, height), "white").save(out, format="PNG")
    return out.getvalue()


def test_strips_cover_the_sheet_with_overlap():
    strips = [Image.open(io.BytesIO(s)) for s in cut_strips(_png(2500))]
    assert [s.size for s in strips] == [
        (40, STRIP_HEIGHT), (40, STRIP_HEIGHT), (40, 2500 - 2 * (STRIP_HEIGHT - STRIP_OVERLAP))
    ]


def test_a_short_sheet_is_one_strip():
    assert len(cut_strips(_png(STRIP_HEIGHT))) == 1


def test_read_sends_every_strip_in_order_and_drops_the_overlap_rows():
    sent = []

    def read(strips, output_model):
        sent.append((len(strips), output_model))
        return _read((50.0, "A", "RB"), (40.0, "B", "WR"), (40.0, "B", "WR"), (30.0, "C", "RB"))

    parsed = read_chart(_png(2500), read)
    assert sent == [(3, ChartRead)]
    assert [r.name for r in parsed.rows] == ["A", "B", "C"]


def test_overlap_rows_that_differ_fail_the_guard():
    def read(strips, output_model):
        return _padded((50.0, "DJ Moore", "WR"), (49.0, "D.J. Moore", "WR"))
    assert _failed(read_chart(_png(2500), read)) == ["overlap rows agree"]


def test_overlap_rows_that_agree_dedupe_and_pass():
    def read(strips, output_model):
        return _padded((50.0, "DJ Moore", "WR"), (50.0, "D.J. Moore", "WR"))
    parsed = read_chart(_png(2500), read)
    assert [r.name for r in parsed.rows[:2]] == ["DJ Moore", "Pad a"]
    assert _failed(parsed) == []


SEASON_START = date(2026, 9, 9)


def _url(chart_date):
    return f"https://peakedinhighskool.com/wp-content/uploads/1QB0.5PPR4pt_{chart_date}.png"


def _site(*chart_dates):
    """A fake fetch that serves the media list and one PNG per date, and logs every call."""
    calls = []
    listing = [{"date": "2026-10-14T08:27:47", "source_url": _url(d)} for d in chart_dates]

    def fetch(url):
        calls.append(url)
        if url == MEDIA_URL:
            return json.dumps(listing).encode()
        return PNG_SIGNATURE + b"png of " + url.rsplit("_", 1)[1].encode()

    fetch.calls = calls
    return fetch


def _down(url):
    raise httpx.ConnectError("down")


def test_fetch_picks_the_file_in_the_week_window(tmp_path):
    fetch = _site("20261006", "20261013", "20261020")
    path = fetch_chart(SEASON_START, 6, tmp_path, fetch)
    assert path == charts_dir(tmp_path) / "week-06.png"
    assert path.read_bytes() == PNG_SIGNATURE + b"png of 20261013.png"
    path = fetch_chart(SEASON_START, 7, tmp_path, fetch)
    assert path.read_bytes() == PNG_SIGNATURE + b"png of 20261020.png"

def test_a_fetched_body_that_is_not_a_png_is_a_failed_fetch(tmp_path, caplog):
    listing = _site("20261013")
    def fetch(url):
        return listing(url) if url == MEDIA_URL else b"<html>Not found</html>"
    assert fetch_chart(SEASON_START, 6, tmp_path, fetch) is None
    assert not (charts_dir(tmp_path) / "week-06.png").exists()
    assert "is not a PNG" in caplog.text



def test_fetch_finds_no_file_for_a_week_the_site_lacks(tmp_path):
    assert fetch_chart(SEASON_START, 8, tmp_path, _site("20261013", "20261020")) is None


def test_a_hand_placed_png_wins_and_nothing_is_fetched(tmp_path):
    charts_dir(tmp_path).mkdir(parents=True)
    (charts_dir(tmp_path) / "week-06.png").write_bytes(b"by hand")
    fetch = _site("20261013")
    assert fetch_chart(SEASON_START, 6, tmp_path, fetch).read_bytes() == b"by hand"
    assert fetch.calls == []


def _cached(repo, *weeks):
    charts_dir(repo).mkdir(parents=True)
    for week in weeks:
        (charts_dir(repo) / f"week-{week:02d}.png").write_bytes(b"old")


def test_an_outage_uses_the_week_before(tmp_path):
    _cached(tmp_path, 6)
    assert fetch_chart(SEASON_START, 7, tmp_path, _down) == charts_dir(tmp_path) / "week-06.png"


def test_an_outage_ignores_a_chart_three_weeks_old(tmp_path):
    _cached(tmp_path, 4)
    assert fetch_chart(SEASON_START, 7, tmp_path, _down) is None


def test_an_outage_never_uses_a_later_week(tmp_path):
    _cached(tmp_path, 8)
    assert fetch_chart(SEASON_START, 7, tmp_path, _down) is None


def test_an_outage_uses_the_newest_of_the_two_weeks_before(tmp_path, caplog):
    _cached(tmp_path, 5, 6)
    assert fetch_chart(SEASON_START, 7, tmp_path, _down) == charts_dir(tmp_path) / "week-06.png"
    assert "week 6 stands in for week 7" in caplog.text


def test_a_failed_file_fetch_falls_back_too(tmp_path):
    _cached(tmp_path, 5)
    listing = _site("20261013")
    def fetch(url):
        return listing(url) if url == MEDIA_URL else _down(url)
    assert fetch_chart(SEASON_START, 6, tmp_path, fetch) == charts_dir(tmp_path) / "week-05.png"


def test_an_outage_with_no_cache_gives_none(tmp_path):
    assert fetch_chart(SEASON_START, 6, tmp_path, _down) is None


def _site_with_png(chart_date, height=1500):
    """A fake fetch like _site, but the PNG is a real image that the strip cut can open."""
    png = _png(height)
    inner = _site(chart_date)
    def fetch(url):
        return inner(url) if url == MEDIA_URL else png
    fetch.calls = inner.calls
    return fetch


class _Reader:
    """A fake read that returns a fixed result and counts its calls."""

    def __init__(self, read):
        self.result = read
        self.calls = 0

    def __call__(self, strips, output_model):
        self.calls += 1
        return self.result


def test_chart_values_fetch_read_match_and_cache(tmp_path):
    fetch = _site_with_png("20261013")
    reader = _Reader(_padded((50.0, "Ja'Marr Chase", "WR"), (40.0, "Kenneth Walker", "RB")))
    lines = [_line("1", "Ja'Marr Chase", "WR"), _line("2", "Kenneth Walker III", "RB")]
    values = chart_values(tmp_path, SEASON_START, 6, lines, fetch, read=reader)
    assert values.values == {"1": 50.0, "2": 40.0}
    assert (charts_dir(tmp_path) / "week-06.png").exists()
    assert ChartRead.model_validate_json((charts_dir(tmp_path) / "week-06.json").read_text()) == reader.result


def test_a_parsed_json_is_reused_with_no_fetch_and_no_read(tmp_path):
    fetch = _site_with_png("20261013")
    reader = _Reader(_padded((50.0, "Ja'Marr Chase", "WR")))
    chart_values(tmp_path, SEASON_START, 6, [], fetch, read=reader)
    fetch.calls.clear()
    values = chart_values(tmp_path, SEASON_START, 6, [_line("9", "Ja'Marr Chase", "WR")], _down, read=_Reader(None))
    assert values.values == {"9": 50.0}
    assert reader.calls == 1
    assert fetch.calls == []


def test_a_hand_placed_png_is_read_not_fetched(tmp_path):
    charts_dir(tmp_path).mkdir(parents=True)
    (charts_dir(tmp_path) / "week-06.png").write_bytes(_png(1500))
    reader = _Reader(_padded((50.0, "A", "RB")))
    assert load_chart(tmp_path, SEASON_START, 6, _down, read=reader) == (6, reader.result)


def test_a_hand_placed_png_newer_than_the_saved_read_is_read_again(tmp_path):
    import os
    charts = charts_dir(tmp_path)
    charts.mkdir(parents=True)
    png, saved = charts / "week-06.png", charts / "week-06.json"
    png.write_bytes(_png(1500))
    first = _Reader(_padded((50.0, "A", "RB")))
    assert load_chart(tmp_path, SEASON_START, 6, _down, read=first) == (6, first.result)
    # A later PNG drop, by hand, must beat the saved read of the old image.
    os.utime(saved, (1_000_000, 1_000_000))
    png.write_bytes(_png(1500))
    second = _Reader(_padded((60.0, "A", "RB")))
    assert load_chart(tmp_path, SEASON_START, 6, _down, read=second) == (6, second.result)
    assert second.calls == 1


def test_a_parsed_json_that_is_not_utf_8_is_read_again_from_the_image(tmp_path):
    charts_dir(tmp_path).mkdir(parents=True)
    (charts_dir(tmp_path) / "week-06.png").write_bytes(_png(1500))
    (charts_dir(tmp_path) / "week-06.json").write_bytes(b"\xff\xfe not utf-8")
    reader = _Reader(_padded((50.0, "A", "RB")))
    assert load_chart(tmp_path, SEASON_START, 6, _down, read=reader) == (6, reader.result)
    assert reader.calls == 1


def test_a_hand_placed_file_with_html_inside_gives_no_trade_values_and_does_not_raise(tmp_path, caplog):
    charts_dir(tmp_path).mkdir(parents=True)
    (charts_dir(tmp_path) / "week-06.png").write_bytes(b"<html>Not found</html>")
    assert load_chart(tmp_path, SEASON_START, 6, _down, read=_Reader(None)) is None
    assert "does not open as an image" in caplog.text


def test_a_failed_guard_keeps_the_png_writes_no_json_and_names_the_guard(tmp_path, caplog):
    fetch = _site_with_png("20261013")
    bad = _Reader(_read((10.0, "A", "RB"), (20.0, "B", "RB")))
    assert chart_values(tmp_path, SEASON_START, 6, [_line("1", "A", "RB")], fetch, read=bad) is None
    assert (charts_dir(tmp_path) / "week-06.png").exists()
    assert not (charts_dir(tmp_path) / "week-06.json").exists()
    assert "trade values never rise" in caplog.text


def test_a_failed_header_week_guard_gives_no_trade_values(tmp_path):
    wrong_week = _Reader(_read((50.0, "A", "RB")).model_copy(update={"week": 5}))
    assert load_chart(tmp_path, SEASON_START, 6, _site_with_png("20261013"), read=wrong_week) is None


def test_the_row_count_guard_uses_the_parsed_prior_week(tmp_path):
    charts_dir(tmp_path).mkdir(parents=True)
    prior = _read(*_rows(200)).model_copy(update={"week": 5})
    (charts_dir(tmp_path) / "week-05.json").write_text(prior.model_dump_json())
    short = _Reader(_read(*_rows(150, 100.0)))
    assert load_chart(tmp_path, SEASON_START, 6, _site_with_png("20261013"), read=short) is None


def test_a_failed_read_gives_no_trade_values_and_does_not_raise(tmp_path):
    def broken(strips, output_model):
        raise WriterError("no parsed output")

    assert load_chart(tmp_path, SEASON_START, 6, _site_with_png("20261013"), read=broken) is None


def test_no_chart_and_no_cache_gives_no_trade_values(tmp_path):
    assert chart_values(tmp_path, SEASON_START, 6, [], _down, read=_Reader(None)) is None


def test_an_outage_reads_the_stand_in_as_its_own_week(tmp_path):
    charts_dir(tmp_path).mkdir(parents=True)
    (charts_dir(tmp_path) / "week-05.png").write_bytes(_png(1500))
    stand_in = _Reader(_padded((50.0, "A", "RB")).model_copy(update={"week": 5}))
    assert load_chart(tmp_path, SEASON_START, 6, _down, read=stand_in) == (5, stand_in.result)


def test_claude_read_sends_the_strips_in_order_then_one_text_block():
    sent = {}

    class Messages:
        def parse(self, **kwargs):
            sent.update(kwargs)
            usage = type("Usage", (), {
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
                "input_tokens": 1,
            })
            return type("Response", (), {
                "stop_reason": "end_turn", "parsed_output": "parsed", "usage": usage,
            })()

    writer = ClaudeWriter(client=type("Client", (), {"messages": Messages()})())
    assert claude_read([b"one", b"two"], ChartRead, writer.parse) == "parsed"
    content = sent["messages"][0]["content"]
    assert [block["type"] for block in content] == ["image", "image", "text"]
    assert content[0]["source"] == {"type": "base64", "media_type": "image/png", "data": "b25l"}
    assert content[2]["text"] == CHART_PROMPT
    assert sent["output_format"] is ChartRead
    assert sent["output_config"] == {"effort": "high"}
    assert "system" not in sent


@pytest.mark.live
def test_live_week_6_chart_passes_the_guards(tmp_path):
    loaded = load_chart(tmp_path, SEASON_START, 6, read=claude_reader(parse_call))
    assert loaded is not None, "a guard failed or the fetch failed, see the log"
    chart_week, parsed = loaded
    assert chart_week == 6
    top = parsed.rows[0]
    assert (top.name, top.position, top.value) == ("Jahmyr Gibbs", "RB", 68.5)


def test_saved_chart_read_gives_the_saved_read_or_none(tmp_path):
    assert saved_chart_read(tmp_path, 6) is None
    charts = charts_dir(tmp_path)
    charts.mkdir(parents=True)
    read = _read((40.0, "Ja'Marr Chase", "WR"))
    (charts / "week-06.json").write_text(read.model_dump_json(), encoding="utf-8")
    assert saved_chart_read(tmp_path, 6) == read
