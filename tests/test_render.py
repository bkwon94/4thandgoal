"""
Tests for the week page and the home page renderer.
They build the page from the recorded fixture and check the HTML that a reader sees.
"""
import re

import pytest

from cornerstone.models import Blurb, Sentence
from cornerstone.parse import parse_week
from cornerstone.render import build_context, render_index, render_week
from cornerstone.sheet import build_bundle
from cornerstone.sleeper import load_raw


def _bundle(d):
    return build_bundle(parse_week(load_raw(d)), news=lambda pid: [])


def _blurbs(bundle):
    return {c.key: Blurb(chapter=c.key, attempt=1, fallback=False,
            sentences=[Sentence(text=f"Blurb for {c.key}.", fact_ids=c.fact_ids[:1])])
            for c in bundle.sheet.chapters}


PNG_BYTES = b"\x89PNG\r\n\x1a\nfake"


def _fake_png(url):
    return PNG_BYTES


def _no_bytes(url):
    return None


def test_render_week_has_every_chapter(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    page = render_week(b, _blurbs(b), tmp_path, _fake_png)
    html = page.read_text()
    for s in ("WEEK", "Matchup of the Week", "Game Changer", "Top Scorer", "MVB", "Read recap",
              "The Median Game", "Standings", "Next Week", "Oct 15 – Oct 19, 2026", "Bo Girds"):
        assert s in html
    assert html.count("Read recap") == 6
    assert (tmp_path / "static" / "style.css").exists()


def test_avatars_are_written_next_to_the_page(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    page = render_week(b, _blurbs(b), tmp_path, _fake_png)
    assert (page.parent / "avatars" / "1.jpg").read_bytes() == PNG_BYTES
    assert (page.parent / "avatars" / "2.webp").exists()
    assert 'src="avatars/1.jpg"' in page.read_text()


def test_missing_avatar_uses_default(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    for t in b.data.teams.values():
        t.avatar_url = None
    page = render_week(b, _blurbs(b), tmp_path, _fake_png)
    assert "avatar-default.svg" in page.read_text()
    assert not (page.parent / "avatars").exists()


def test_failed_download_uses_default(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    page = render_week(b, _blurbs(b), tmp_path, _no_bytes)
    assert "avatar-default.svg" in page.read_text()
    assert not list((page.parent / "avatars").glob("*"))


def test_index_lists_week(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    render_week(b, _blurbs(b), tmp_path, _fake_png)
    idx = render_index(tmp_path).read_text()
    assert "Week 6" in idx and "2026/week-06/" in idx


def test_index_sorts_newest_first(tmp_path):
    for season, week in ((2026, 6), (2026, 10), (2026, 7)):
        d = tmp_path / str(season) / f"week-{week:02d}"
        d.mkdir(parents=True)
        (d / "index.html").write_text(
            f'<meta name="cornerstone-summary" content="Week {week} · Dates · A vs B">')
    idx = render_index(tmp_path).read_text()
    assert idx.index("week-10/") < idx.index("week-07/") < idx.index("week-06/")


def test_context_median_bars(fixture_raw_dir):
    b = _bundle(fixture_raw_dir)
    ctx = build_context(b, _blurbs(b), {})
    bars = ctx["median"]["bars"]
    assert len(bars) == 12
    assert bars[0]["pct"] == 100.0
    assert [x["score"] for x in bars] == sorted((x["score"] for x in bars), reverse=True)
    assert sum(x["above"] for x in bars) == 6
    assert ctx["median"]["line_pct"] == round(b.data.median.median / bars[0]["score"] * 100, 1)


def test_context_missing_award_is_flagged(fixture_raw_dir):
    b = _bundle(fixture_raw_dir)
    b.data.awards = [a for a in b.data.awards if a.key != "underperformer"]
    ctx = build_context(b, _blurbs(b), {})
    assert [t["title"] for t in ctx["awards"]] == [
        "Top Scorer", "MVB · Most Valuable Benchwarmer", "Underperformer", "Overachiever",
    ]
    assert [t["missing"] for t in ctx["awards"]] == [False, False, True, False]


def test_summary_meta_names_the_pick(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    html = render_week(b, _blurbs(b), tmp_path, _fake_png).read_text()
    assert '<meta name="cornerstone-summary" content="Week 6 · Oct 15 – Oct 19, 2026 · ' in html
    assert "behold the lamb vs Bo Girds" in html or "Bo Girds vs behold the lamb" in html


def test_pick_row_links_to_top_of_page(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    html = render_week(b, _blurbs(b), tmp_path, _fake_png).read_text()
    assert html.count("This is the Matchup of the Week.") == 1
    assert 'href="#motw"' in html


@pytest.mark.live
def test_real_download_writes_avatars(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    page = render_week(b, _blurbs(b), tmp_path)
    assert list((page.parent / "avatars").glob("*"))


def test_tied_matchup_has_no_winner_color(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    tied = next(f for f in b.data.matchups if f.matchup_id != b.data.pick.matchup_id)
    tied.winner = tied.loser = None
    tied.score_l = tied.score_w
    html = render_week(b, _blurbs(b), tmp_path, _fake_png).read_text()
    row = re.findall(r'<div class="mu">.*?<button', html, re.S)[tied.matchup_id - 1]
    assert 'class="w"' not in row
    for rid in tied.top_scorer:
        assert b.data.teams[rid].name in row


def test_mvb_tile_spells_out_the_title(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    html = render_week(b, _blurbs(b), tmp_path, _no_bytes).read_text()
    assert "MVB · Most Valuable Benchwarmer" in html
