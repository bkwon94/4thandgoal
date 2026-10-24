"""
Tests for the page.json and rankings.json writers.
They build the JSON from the recorded fixture and check the values that the site reads.
"""
import json

import pytest
from pydantic import TypeAdapter

from cornerstone.history import load_history
from cornerstone.models import Blurb, Sentence
from cornerstone.odds import OddsResult, TeamOdds
from cornerstone.parse import parse_week
from cornerstone.render import _saved_avatars, _saved_headshots, build_context, render_rankings, render_week
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


def _page(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_render_week_writes_every_chapter_to_the_json(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    page = render_week(b, _blurbs(b), tmp_path, _fake_png)
    assert page == tmp_path / "2026" / "week-06" / "page.json"
    data = _page(page)
    for key in ("pick", "motw", "game_changer", "awards", "leaders", "trades", "matchups", "median", "table", "next"):
        assert key in data
    assert data["week"] == 6 and data["dates"] == "Oct 15 – Oct 19, 2026"
    assert len(data["matchups"]) == 6
    assert len(data["table"]) == 12
    assert not (page.parent / "index.html").exists()
    assert not (tmp_path / "static").exists()
    assert not (tmp_path / "index.html").exists()


def test_the_json_drops_the_keys_that_only_the_templates_read(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    data = _page(render_week(b, _blurbs(b), tmp_path, _fake_png))
    assert data["schema_version"] == 2
    assert "asset_version" not in data and "root" not in data


def test_avatars_are_written_next_to_the_page(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    page = render_week(b, _blurbs(b), tmp_path, _fake_png)
    assert (page.parent / "avatars" / "1.jpg").read_bytes() == PNG_BYTES
    assert (page.parent / "avatars" / "2.webp").exists()
    assert _page(page)["avatars"]["1"] == "avatars/1.jpg"


def test_missing_avatar_uses_default(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    for t in b.data.teams.values():
        t.avatar_url = None
    page = render_week(b, _blurbs(b), tmp_path, _fake_png)
    assert set(_page(page)["avatars"].values()) == {"../../images/avatar-default.svg"}
    assert not (page.parent / "avatars").exists()


def test_failed_download_uses_default(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    page = render_week(b, _blurbs(b), tmp_path, _no_bytes)
    assert set(_page(page)["avatars"].values()) == {"../../images/avatar-default.svg"}
    assert not list((page.parent / "avatars").glob("*"))


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


def test_summary_names_the_pick(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    summary = _page(render_week(b, _blurbs(b), tmp_path, _fake_png))["summary"]
    assert summary.startswith("Week 6 · Oct 15 – Oct 19, 2026 · ")
    assert summary.endswith(("behold the lamb vs Bo Girds", "Bo Girds vs behold the lamb"))


def test_one_matchup_is_the_pick(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    data = _page(render_week(b, _blurbs(b), tmp_path, _fake_png))
    assert [m["id"] for m in data["matchups"] if m["is_pick"]] == [b.data.pick.matchup_id]


@pytest.mark.live
def test_real_download_writes_avatars(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    page = render_week(b, _blurbs(b), tmp_path)
    assert list((page.parent / "avatars").glob("*"))


def test_tied_matchup_has_no_winner_flag(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    tied = next(f for f in b.data.matchups if f.matchup_id != b.data.pick.matchup_id)
    tied.winner = tied.loser = None
    tied.score_l = tied.score_w
    data = _page(render_week(b, _blurbs(b), tmp_path, _fake_png))
    sides = next(m for m in data["matchups"] if m["id"] == tied.matchup_id)["sides"]
    assert not any(side["winner"] or side["loser"] for side in sides)
    assert {side["team"]["roster_id"] for side in sides} == set(tied.top_scorer)


def test_mvb_tile_spells_out_the_title(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    data = _page(render_week(b, _blurbs(b), tmp_path, _no_bytes))
    assert "MVB · Most Valuable Benchwarmer" in [t["title"] for t in data["awards"]]


def test_trades_hold_one_card_per_trade_with_the_traded_players(tbundle, tmp_path):
    data = _page(render_week(tbundle, _blurbs(tbundle), tmp_path, _fake_png))
    assert len(data["trades"]) == 6
    names = {p["name"] for card in data["trades"] for side in card["sides"] for p in side["players"]}
    assert "Bhayshul Tuten" in names


def test_no_trades_gives_an_empty_list(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    assert _page(render_week(b, _blurbs(b), tmp_path, _fake_png))["trades"] == []


def test_awards_show_four_tiles_for_a_bundle_with_drops(dbundle):
    ctx = build_context(dbundle, _blurbs(dbundle), {}, {})
    assert [t["title"] for t in ctx["awards"]] == [
        "Top Scorer", "MVB · Most Valuable Benchwarmer", "Underperformer", "Overachiever",
    ]


def test_trade_cards_name_every_traded_player(tbundle, fixture_raw_dir, tmp_path):
    week = parse_week(load_raw(fixture_raw_dir))
    names = {line.player_id: line.name for m in week.matchups for side in (m.a, m.b) for line in side.lines}
    data = _page(render_week(tbundle, _blurbs(tbundle), tmp_path, _fake_png))
    for card, trade in zip(data["trades"], tbundle.data.trades):
        listed = {p["name"] for side in card["sides"] for p in side["players"]}
        assert listed == {names[pid] for pid in trade.adds}
    assert "An unlisted player" not in str(data["trades"])


def test_build_context_trade_sides_carry_no_grade(tbundle):
    ctx = build_context(tbundle, _blurbs(tbundle), {}, {})
    assert all("grade" not in side for card in ctx["trades"] for side in card["sides"])


def test_next_week_holds_both_teams_of_each_game(hbundle, tmp_path):
    data = _page(render_week(hbundle, {}, tmp_path, fetch_bytes=lambda url: None))
    assert data["next"]
    assert all(game["a"]["name"] and game["b"]["name"] for game in data["next"])


def test_build_context_has_five_leader_boards(fixture_raw_dir):
    b = _bundle(fixture_raw_dir)
    boards = build_context(b, _blurbs(b), {}, {})["leaders"]
    assert [x["position"] for x in boards] == ["QB", "RB", "WR", "TE", "DEF"]
    assert boards[1]["rows"][0] == {"rank": 1, "player": "Kenneth Walker", "player_id": "8151", "nfl_team": "KC",
                                    "points": 26.9, "team": "Bo Girds"}


def test_a_position_with_no_starters_keeps_its_board(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    b.data.leaders = [leader for leader in b.data.leaders if leader.position != "DEF"]
    boards = _page(render_week(b, _blurbs(b), tmp_path, _fake_png))["leaders"]
    assert len(boards) == 5
    assert boards[-1] == {"position": "DEF", "rows": []}


def test_position_leaders_hold_five_boards_and_fifteen_rows(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    data = _page(render_week(b, _blurbs(b), tmp_path, _fake_png))
    assert len(data["leaders"]) == 5
    assert sum(len(board["rows"]) for board in data["leaders"]) == 15
    assert data["blurbs"]["position_leaders"] == "Blurb for position_leaders."


def _headshot_players(b):
    """The player lines on the Game Changer hero, the award tiles, and the leader rows."""
    awards = [a.line for a in b.data.awards if a.key in ("game_changer", "top_scorer", "mvb",
                                                          "underperformer", "overachiever")]
    return awards + [lead.line for lead in b.data.leaders]


def test_headshots_cover_the_hero_the_tiles_and_the_rows(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    headshots = {line.player_id: f"headshots/{line.player_id}.png" for line in _headshot_players(b)}
    ctx = build_context(b, _blurbs(b), {}, headshots)
    assert ctx["game_changer"]["award"].line.player_id in headshots
    for t in ctx["awards"]:
        assert t["missing"] or t["player_id"] in headshots
    for board in ctx["leaders"]:
        for r in board["rows"]:
            assert r["player_id"] in headshots


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
    wr = next(line for line in lines.values() if line.position == "WR")
    assert f"https://sleepercdn.com/content/nfl/players/{wr.player_id}.jpg" in headshot_urls
    defense = next(line for line in lines.values() if line.position == "DEF")
    assert f"https://sleepercdn.com/images/team_logos/nfl/{defense.player_id.lower()}.png" in headshot_urls
    assert defense.player_id != defense.player_id.lower()
    saved = _page(page)["headshots"]
    for pid in lines:
        assert (page.parent / "headshots" / f"{pid}.png").read_bytes() == PNG_BYTES
        assert saved[pid] == f"headshots/{pid}.png"


def test_failed_headshot_uses_the_default_silhouette(fixture_raw_dir, tmp_path):
    b = _bundle(fixture_raw_dir)
    lines = {line.player_id: line for line in _headshot_players(b)}
    failed = next(line for line in lines.values() if line.position == "WR")
    failed_url = f"https://sleepercdn.com/content/nfl/players/{failed.player_id}.jpg"
    page = render_week(b, _blurbs(b), tmp_path, lambda url: None if url == failed_url else PNG_BYTES)
    saved = _page(page)["headshots"]
    assert saved[failed.player_id] == "../../images/headshot-default.svg"
    assert not (page.parent / "headshots" / f"{failed.player_id}.png").exists()
    for pid in lines.keys() - {failed.player_id}:
        assert saved[pid] == f"headshots/{pid}.png"


def test_trade_context_gives_each_player_a_name_and_a_headshot(tbundle):
    headshots = {"12507": "headshots/12507.png"}
    ctx = build_context(tbundle, _blurbs(tbundle), {}, headshots)
    sides = {side["team"].roster_id: side for side in ctx["trades"][0]["sides"]}
    hampton = next(p for p in sides[12]["players"] if p["name"] == "Omarion Hampton")
    assert hampton == {"name": "Omarion Hampton", "headshot": "headshots/12507.png"}
    montgomery = next(p for p in sides[4]["players"] if p["name"] == "David Montgomery")
    # A player with no saved headshot gets the default silhouette.
    assert montgomery == {"name": "David Montgomery", "headshot": "../../images/headshot-default.svg"}


def test_headshots_of_traded_players_are_fetched_with_the_silhouette_on_a_failed_fetch(tbundle, tmp_path):
    failed = "12533"
    urls = []

    def fetch(url):
        urls.append(url)
        return None if url.endswith(f"/{failed}.jpg") else PNG_BYTES

    page = render_week(tbundle, _blurbs(tbundle), tmp_path, fetch)
    traded = {pid for trade in tbundle.data.trades for pid in trade.adds}
    for pid in traded:
        assert f"https://sleepercdn.com/content/nfl/players/{pid}.jpg" in urls
    players = [p for side in _page(page)["trades"][0]["sides"] for p in side["players"]]
    assert "headshots/12507.png" in {p["headshot"] for p in players}
    assert f"headshots/{failed}.png" not in {p["headshot"] for p in players}
    assert "../../images/headshot-default.svg" in {p["headshot"] for p in players}


def test_two_side_card_has_two_sides_and_a_player_for_each_chip(tbundle, tmp_path):
    card = _page(render_week(tbundle, _blurbs(tbundle), tmp_path, _fake_png))["trades"][0]
    assert len(card["sides"]) == 2
    assert sum(len(side["players"]) for side in card["sides"]) == 4
    assert "Omarion Hampton" in {p["name"] for side in card["sides"] for p in side["players"]}


def test_three_side_card_has_three_sides_and_a_pick_row(tbundle, tmp_path):
    from cornerstone.models import DraftPick, Trade
    first = tbundle.data.trades[0]
    a, b = first.roster_ids
    c = next(rid for rid in tbundle.data.teams if rid not in (a, b))
    trade = Trade(transaction_id="x", created=first.created, roster_ids=[a, b, c],
                  adds={"12507": a, "12533": b, "4046": c}, drops={"12507": b, "12533": c, "4046": a},
                  draft_picks=[DraftPick(season="2027", round=2, roster_id=c, previous_owner_id=c, owner_id=a)])
    bundle = tbundle.model_copy(update={"data": tbundle.data.model_copy(update={"trades": [trade]})})
    card = _page(render_week(bundle, _blurbs(bundle), tmp_path, _fake_png))["trades"][0]
    assert len(card["sides"]) == 3
    assert [pick for side in card["sides"] for pick in side["picks"]] == ["2027 round 2 pick"]
    assert "Patrick Mahomes" in {p["name"] for side in card["sides"] for p in side["players"]}


def test_a_traded_defense_gets_the_team_logo(tbundle, tmp_path):
    trade = tbundle.data.trades[0]
    trade.adds["SEA"] = trade.roster_ids[0]
    urls = []

    def fetch(url):
        urls.append(url)
        return PNG_BYTES

    render_week(tbundle, _blurbs(tbundle), tmp_path, fetch)
    assert "https://sleepercdn.com/images/team_logos/nfl/sea.png" in urls
    assert "https://sleepercdn.com/content/nfl/players/SEA.jpg" not in urls


def test_render_week_writes_page_json_with_the_context(tbundle, tmp_path):
    page = render_week(tbundle, _blurbs(tbundle), tmp_path, _fake_png)
    data = _page(page)
    context = build_context(tbundle, _blurbs(tbundle), {}, {})
    assert data["schema_version"] == 2
    assert data["week"] == context["week"]
    assert len(data["trades"]) == len(context["trades"]) > 0
    assert [s["team"]["name"] for s in data["pick"]["sides"]] == [s["team"].name for s in context["pick"]["sides"]]
    assert data["avatars"]["1"] == "avatars/1.jpg"


def test_page_json_holds_the_whole_context(tbundle, tmp_path):
    page = render_week(tbundle, _blurbs(tbundle), tmp_path, _fake_png)
    written = _page(page)
    # The saved-file lookups read the images on disk, so they do not copy the writer's own paths.
    context = build_context(
        tbundle, _blurbs(tbundle), _saved_avatars(tbundle, page.parent), _saved_headshots(tbundle, page.parent),
    )
    assert written == {"schema_version": 2, **TypeAdapter(dict).dump_python(context, mode="json")}


def test_rankings_file_holds_every_week_in_rank_order(fixture_raw_dir, fixture_history_root, tmp_path):
    raw = load_raw(fixture_raw_dir)
    history = load_history(fixture_history_root, raw, week=6)
    teams = parse_week(raw).teams
    out = render_rankings(history, 2026, teams, tmp_path)
    assert out == tmp_path / "2026" / "rankings.json"
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["season"] == 2026
    assert [w["week"] for w in data["weeks"]] == [1, 2, 3, 4, 5, 6]
    for week in data["weeks"]:
        assert len(week["rows"]) == 12
        assert [row["rank"] for row in week["rows"]] == list(range(1, 13))
        for row in week["rows"]:
            assert set(row) == {"roster_id", "name", "wins", "losses", "rank", "movement", "components", "blurb"}
            assert set(row["components"]) == {"standing", "form", "schedule_played", "scoring"}
            assert row["name"] == teams[row["roster_id"]].name
            assert row["blurb"] == []
    assert all(row["movement"] is None for row in data["weeks"][0]["rows"])
    assert all(isinstance(row["movement"], int) for row in data["weeks"][1]["rows"])


def _rankings_blurb(*tagged):
    return Blurb(chapter="rankings", attempt=1, fallback=False,
                 sentences=[Sentence(text=text, fact_ids=["PR.1"], roster_id=rid) for rid, text in tagged])


def _blurbs_by_week(out):
    data = json.loads(out.read_text(encoding="utf-8"))
    return {w["week"]: {row["roster_id"]: row["blurb"] for row in w["rows"]} for w in data["weeks"]}


def test_rankings_file_puts_the_blurb_in_the_current_week_and_keeps_past_weeks(
    fixture_raw_dir, fixture_history_root, tmp_path,
):
    raw = load_raw(fixture_raw_dir)
    history = load_history(fixture_history_root, raw, week=6)
    teams = parse_week(raw).teams
    render_rankings(history, 2026, teams, tmp_path, 5, _rankings_blurb((1, "Week 5 one."), (2, "Week 5 two.")))
    out = render_rankings(history, 2026, teams, tmp_path, 6, _rankings_blurb(
        (1, "First."), (2, "Second."), (1, "Again."),
        # A sentence with no roster tag has no row to go in.
        (None, "Lost."),
    ))
    blurbs = _blurbs_by_week(out)
    # Each sentence is the shape the site reads: the text and its fact IDs, with no roster tag.
    assert blurbs[6][1] == [{"text": "First.", "fact_ids": ["PR.1"]}, {"text": "Again.", "fact_ids": ["PR.1"]}]
    assert blurbs[6][2] == [{"text": "Second.", "fact_ids": ["PR.1"]}]
    assert blurbs[6][3] == []
    # The past week keeps the blurb of the last file, and a week with no saved blurb keeps an empty list.
    assert blurbs[5][1] == [{"text": "Week 5 one.", "fact_ids": ["PR.1"]}]
    assert blurbs[5][2] == [{"text": "Week 5 two.", "fact_ids": ["PR.1"]}]
    assert all(b == [] for week in (1, 2, 3, 4) for b in blurbs[week].values())
    # A file with no blurb for the current week keeps every week's blurb as it was.
    assert _blurbs_by_week(render_rankings(history, 2026, teams, tmp_path, 6)) == blurbs


def _odds_of(teams, playoff):
    """Odds for every roster: roster 1 clinched, roster 2 out, and the rest open with a seed at 50% or more."""
    def one(rid):
        status = "in" if rid == 1 else "out" if rid == 2 else "open"
        return TeamOdds(roster_id=rid, playoff=playoff, bye=playoff // 4, seed=3 if playoff >= 50 else None,
                        status=status)
    return OddsResult(teams={rid: one(rid) for rid in teams}, swings=[])


def _odds_by_week(out):
    data = json.loads(out.read_text(encoding="utf-8"))
    return {w["week"]: {row["roster_id"]: row.get("odds") for row in w["rows"]} for w in data["weeks"]}


def test_rankings_file_puts_the_odds_on_the_current_week_only(fixture_raw_dir, fixture_history_root, tmp_path):
    raw = load_raw(fixture_raw_dir)
    history = load_history(fixture_history_root, raw, week=6)
    teams = parse_week(raw).teams
    out = render_rankings(history, 2026, teams, tmp_path, 6, odds=_odds_of(teams, 40))
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    week6 = {row["roster_id"]: row for row in data["weeks"][-1]["rows"]}
    # The object is the shape the site reads: whole numbers, a seed or null, and a status.
    assert week6[1]["odds"] == {"playoff": 40, "bye": 10, "seed": None, "status": "in"}
    assert week6[2]["odds"]["status"] == "out"
    assert week6[3]["odds"]["status"] == "open"
    # A past week has no odds key at all, not a null.
    assert all("odds" not in row for w in data["weeks"][:-1] for row in w["rows"])


def test_rankings_file_keeps_the_saved_odds_when_a_rerun_has_none(fixture_raw_dir, fixture_history_root, tmp_path):
    raw = load_raw(fixture_raw_dir)
    history = load_history(fixture_history_root, raw, week=6)
    teams = parse_week(raw).teams
    render_rankings(history, 2026, teams, tmp_path, 5, odds=_odds_of(teams, 60))
    out = render_rankings(history, 2026, teams, tmp_path, 6, odds=_odds_of(teams, 40))
    odds = _odds_by_week(out)
    # The rerun for week 6 keeps the week 5 odds of the last file, so the file never shrinks.
    assert odds[5][3] == {"playoff": 60, "bye": 15, "seed": 3, "status": "open"}
    assert odds[6][3] == {"playoff": 40, "bye": 10, "seed": None, "status": "open"}
    assert all(o is None for week in (1, 2, 3, 4) for o in odds[week].values())
    # A rerun with no odds keeps every week's odds as they were.
    assert _odds_by_week(render_rankings(history, 2026, teams, tmp_path, 6)) == odds
