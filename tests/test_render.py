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
from cornerstone.writer import template_blurb


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
    ctx = build_context(b, _blurbs(b), {}, {})
    bars = ctx["median"]["bars"]
    assert len(bars) == 12
    assert bars[0]["pct"] == 100.0
    assert [x["score"] for x in bars] == sorted((x["score"] for x in bars), reverse=True)
    assert sum(x["above"] for x in bars) == 6
    assert ctx["median"]["line_pct"] == round(b.data.median.median / bars[0]["score"] * 100, 1)


def test_context_missing_award_is_flagged(fixture_raw_dir):
    b = _bundle(fixture_raw_dir)
    b.data.awards = [a for a in b.data.awards if a.key != "underperformer"]
    ctx = build_context(b, _blurbs(b), {}, {})
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


def test_trades_section_order_and_cards(tbundle, tmp_path):
    html = render_week(tbundle, _blurbs(tbundle), tmp_path, _fake_png).read_text()
    assert html.index('id="trades"') > html.index(">Awards<")
    assert html.index('id="trades"') < html.index(">All Matchups<")
    assert html.count('class="trade"') == 6
    assert "Bhayshul Tuten" in html and "11.8" in html


def test_grade_letter_and_no_grade(tbundle, tmp_path):
    blurbs = _blurbs(tbundle)
    blurbs["trade_5"].grades = {"T5.12": "A"}
    html = render_week(tbundle, blurbs, tmp_path, _fake_png).read_text()
    assert '<span class="grade">A</span>' in html
    assert html.count("No grade") == 11


def test_trades_render_without_a_trades_blurb(tbundle, tmp_path):
    blurbs = _blurbs(tbundle)
    for key in [k for k in blurbs if k.startswith("trade_")]:
        del blurbs[key]
    html = render_week(tbundle, blurbs, tmp_path, _fake_png).read_text()
    assert html.count('class="trade"') == 6 and html.count("No grade") == 12


def test_trades_render_with_the_template_blurb(tbundle, tmp_path):
    blurbs = _blurbs(tbundle)
    for ch in (c for c in tbundle.sheet.chapters if c.key.startswith("trade_")):
        blurbs[ch.key] = template_blurb(ch, tbundle.sheet)
    html = render_week(tbundle, blurbs, tmp_path, _fake_png).read_text()
    assert html.count("No grade") == 12


def test_trades_have_no_opinion_note(tbundle, tmp_path):
    html = render_week(tbundle, _blurbs(tbundle), tmp_path, _fake_png).read_text()
    assert 'id="trades"' in html
    assert "opinion from the fact sheet" not in html


def test_no_trades_no_section(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    assert 'id="trades"' not in render_week(b, _blurbs(b), tmp_path, _fake_png).read_text()


def test_awards_show_four_tiles_for_a_bundle_with_drops(dbundle):
    ctx = build_context(dbundle, _blurbs(dbundle), {}, {})
    assert [t["title"] for t in ctx["awards"]] == [
        "Top Scorer", "MVB · Most Valuable Benchwarmer", "Underperformer", "Overachiever",
    ]


def test_no_drop_note_for_any_drop_source(dbundle, tmp_path):
    for source in ("nflverse", "sleeper"):
        bundle = dbundle.model_copy(deep=True)
        bundle.data.drop_source = source
        html = render_week(bundle, _blurbs(bundle), tmp_path, _fake_png).read_text()
        assert "Drop value is an estimate" not in html and "Drops are a count" not in html


def _section(html):
    return html[html.index('id="trades"'):html.index(">All Matchups<")]


def _card(html, n):
    return _section(html).split('class="trade"')[n]


def test_trade_cards_have_a_button_and_a_panel(tbundle, tmp_path):
    html = render_week(tbundle, _blurbs(tbundle), tmp_path, _fake_png).read_text()
    s = _section(html)
    assert s.count("Read the grade") == 6 and s.count("Hide the grade") == 6
    assert s.count('aria-expanded="false"') == 6 and s.count('class="body"') == 6
    assert "Blurb for trade_5." in _card(html, 5)


def test_grade_shows_outside_the_panel(tbundle, tmp_path):
    blurbs = _blurbs(tbundle)
    blurbs["trade_5"].grades = {"T5.11": "C", "T5.12": "A"}
    card = _card(render_week(tbundle, blurbs, tmp_path, _fake_png).read_text(), 5)
    assert card.index('<span class="grade">A</span>') < card.index('class="body"')


def test_card_shows_ppg_not_this_week(tbundle, tmp_path):
    s = _section(render_week(tbundle, _blurbs(tbundle), tmp_path, _fake_png).read_text())
    assert '11.8 <span class="ppg">ppg</span>' in s
    assert "22.7" not in s
    assert "<li><span>Josh Jacobs</span></li>" in s


def test_fallback_card_shows_no_grade_and_the_template(tbundle, tmp_path):
    blurbs = _blurbs(tbundle)
    blurbs["trade_5"] = template_blurb(next(c for c in tbundle.sheet.chapters if c.key == "trade_5"), tbundle.sheet)
    card = _card(render_week(tbundle, blurbs, tmp_path, _fake_png).read_text(), 5)
    assert card.count("No grade") == 2
    assert tbundle.sheet.facts["T5.sides"].text in card


def test_card_without_a_blurb_holds_the_sides_text(tbundle, tmp_path):
    blurbs = _blurbs(tbundle)
    del blurbs["trade_5"]
    card = _card(render_week(tbundle, blurbs, tmp_path, _fake_png).read_text(), 5)
    assert card.count("No grade") == 2 and tbundle.sheet.facts["T5.sides"].text in card


def test_app_js_toggles_trade_cards(tbundle, tmp_path):
    render_week(tbundle, _blurbs(tbundle), tmp_path, _fake_png)
    assert ".trade" in (tmp_path / "static" / "app.js").read_text()


def test_next_week_card_puts_each_team_on_its_own_row(hbundle, tmp_path):
    html = render_week(hbundle, {}, tmp_path, fetch_bytes=lambda url: None).read_text()
    card = html[html.index('class="nx"'):]
    card = card[:card.index("</div>\n    </div>")]
    assert card.count('class="side"') == 2 and card.count('class="vs"') == 1
    # The record carries no parentheses, so it reads as a column on the right of the card.
    assert "(" not in card.split('class="rec"')[1].split("</span>")[0]


def test_week_brand_links_to_season_index(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    html = render_week(b, _blurbs(b), tmp_path, _fake_png).read_text()
    assert '<a class="brand" href="../../">' in html


def test_index_brand_links_to_season_index(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    render_week(b, _blurbs(b), tmp_path, _fake_png)
    idx = render_index(tmp_path).read_text()
    assert '<a class="brand" href="./">' in idx


def _leaders_section(html):
    section = html[html.index('id="leaders"'):]
    return section[:section.index("</section>")]


def test_build_context_has_five_leader_boards(fixture_raw_dir):
    b = _bundle(fixture_raw_dir)
    boards = build_context(b, _blurbs(b), {}, {})["leaders"]
    assert [x["position"] for x in boards] == ["QB", "RB", "WR", "TE", "DEF"]
    assert boards[1]["rows"][0] == {"rank": 1, "player": "Kenneth Walker", "player_id": "8151", "nfl_team": "KC",
                                    "points": 26.9, "team": "Bo Girds"}


def test_a_position_with_no_starters_keeps_its_board(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    b.data.leaders = [l for l in b.data.leaders if l.position != "DEF"]
    boards = build_context(b, _blurbs(b), {}, {})["leaders"]
    assert len(boards) == 5
    assert boards[-1] == {"position": "DEF", "rows": []}
    html = render_week(b, _blurbs(b), tmp_path, _fake_png).read_text()
    assert html.count("No starters this week") == 1


def test_position_leaders_section_shows_five_boards_and_fifteen_rows(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    html = render_week(b, _blurbs(b), tmp_path, _fake_png).read_text()
    assert "Position Leaders" in html
    # The section sits after Awards and before the next chapter.
    assert html.index(">Awards<") < html.index('id="leaders"') < html.index("The Median Game")
    section = _leaders_section(html)
    assert section.count('class="board"') == 5
    assert section.count('class="row"') == 15
    row = re.search(r'<li class="row">(.*?)</li>', section.split("RB", 1)[1], re.S).group(1)
    for s in ("1", "Kenneth Walker", "KC", "26.9", "Bo Girds"):
        assert s in row


def test_position_leaders_section_sits_before_trades(tbundle, tmp_path):
    html = render_week(tbundle, _blurbs(tbundle), tmp_path, _fake_png).read_text()
    assert html.index('id="leaders"') < html.index('id="trades"')


def test_position_leaders_blurb_renders_under_the_boards(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    html = render_week(b, _blurbs(b), tmp_path, _fake_png).read_text()
    section = _leaders_section(html)
    assert section.index("Blurb for position_leaders.") > section.rindex('class="board"')


def _headshot_players(b):
    """The player lines on the Game Changer hero, the award tiles, and the leader rows."""
    awards = [a.line for a in b.data.awards if a.key in ("game_changer", "top_scorer", "mvb",
                                                          "underperformer", "overachiever")]
    return awards + [lead.line for lead in b.data.leaders]


def _game_changer_section(html):
    section = html[html.index(">Game Changer<"):]
    return section[:section.index("</section>")]


def test_headshots_show_on_the_hero_the_tiles_and_the_rows(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    headshots = {line.player_id: f"headshots/{line.player_id}.png" for line in _headshot_players(b)}
    ctx = build_context(b, _blurbs(b), {}, headshots)
    assert ctx["game_changer"]["award"].line.player_id in headshots
    for t in ctx["awards"]:
        assert t["missing"] or t["player_id"] in headshots
    for board in ctx["leaders"]:
        for r in board["rows"]:
            assert r["player_id"] in headshots
    html = render_week(b, _blurbs(b), tmp_path, _fake_png).read_text()
    assert _game_changer_section(html).count('class="headshot"') == 1
    tiles = re.findall(r'<div class="tile">(.*?)<div class="sub">', html, re.S)
    assert len(tiles) == 4 and all('class="headshot"' in t for t in tiles)
    rows = re.findall(r'<li class="row">(.*?)</li>', _leaders_section(html), re.S)
    assert len(rows) == 15 and all('class="headshot"' in r and 'loading="lazy"' in r for r in rows)


def test_headshots_are_fetched_once_per_player_and_saved_next_to_the_page(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    urls = []

    def fetch(url):
        urls.append(url)
        return PNG_BYTES

    page = render_week(b, _blurbs(b), tmp_path, fetch)
    headshot_urls = [u for u in urls if "sleepercdn.com/content/nfl/players/" in u
                     or "sleepercdn.com/images/team_logos/nfl/" in u]
    lines = {line.player_id: line for line in _headshot_players(b)}
    assert len(headshot_urls) == len(set(headshot_urls)) == len(lines)
    wr = next(l for l in lines.values() if l.position == "WR")
    assert f"https://sleepercdn.com/content/nfl/players/{wr.player_id}.jpg" in headshot_urls
    defense = next(l for l in lines.values() if l.position == "DEF")
    assert f"https://sleepercdn.com/images/team_logos/nfl/{defense.player_id.lower()}.png" in headshot_urls
    assert defense.player_id != defense.player_id.lower()
    html = page.read_text()
    for pid in lines:
        assert (page.parent / "headshots" / f"{pid}.png").read_bytes() == PNG_BYTES
        assert f'src="headshots/{pid}.png"' in html


def test_failed_headshot_uses_the_default_silhouette(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    lines = {line.player_id: line for line in _headshot_players(b)}
    failed = next(l for l in lines.values() if l.position == "WR")
    failed_url = f"https://sleepercdn.com/content/nfl/players/{failed.player_id}.jpg"
    page = render_week(b, _blurbs(b), tmp_path, lambda url: None if url == failed_url else PNG_BYTES)
    html = page.read_text()
    assert f'src="headshots/{failed.player_id}.png"' not in html
    assert '<img class="headshot" src="../../static/headshot-default.svg"' in html
    assert not (page.parent / "headshots" / f"{failed.player_id}.png").exists()
    for pid in lines.keys() - {failed.player_id}:
        assert f'src="headshots/{pid}.png"' in html
    assert (tmp_path / "static" / "headshot-default.svg").exists()
