"""
Tests for topics.json, the Answers of the 7 league Topics of the front door that the weekly build writes per team.
They run the build and the page-json command on recorded data and on the saved CPC week 8, with no network call.
"""
import json
import shutil
from pathlib import Path

from cpc import ROOT, cpc_client
from fakes import FakeJev, fixture_nflverse, no_claims, no_news
from test_pipeline import _fake, _no_bytes, _repo_with_history

from cornerstone.pipeline import run_build, run_page_json
from cornerstone.topics import write_topics
from league.models import Week
from league.parse import parse_week
from league.paths import client_dir
from league.provider.sleeper import league_settings, load_raw

LEAGUE_TOPICS = {"week_recap", "last_matchup", "next_matchup", "power_rankings", "playoff_race", "your_season",
                 "leaders_trades"}
CPC = client_dir(ROOT, "cpc")
# Lil Fridge, the team of the acceptance tests.
LIL_FRIDGE = "3"


def _topics(build: Path, season: int, week: int) -> dict:
    return json.loads((build / str(season) / f"week-{week:02d}" / "topics.json").read_text(encoding="utf-8"))


def _saved_week_8(tmp_path: Path) -> Path:
    """A client folder with the saved facts and blurbs of CPC 2026 week 8 and the two season files of its build."""
    data = tmp_path / "data" / "2026" / "week-08"
    data.mkdir(parents=True)
    for name in ("facts.json", "blurbs.json"):
        shutil.copy(CPC / "data" / "2026" / "week-08" / name, data / name)
    season = tmp_path / "build" / "2026"
    season.mkdir(parents=True)
    for name in ("rankings.json", "managers.json"):
        shutil.copy(CPC / "build" / "2026" / name, season / name)
    return tmp_path


def test_the_build_writes_an_answer_of_each_league_topic_for_each_team(tmp_path, fixture_raw_dir,
                                                                        fixture_history_root, tmp_path_factory):
    repo = _repo_with_history(tmp_path, fixture_raw_dir, fixture_history_root)
    run_build(repo, 2026, 6, _fake, fetch=False, news=no_news, fetch_bytes=_no_bytes,
              nflverse=fixture_nflverse(tmp_path_factory.mktemp("nflverse")), research=no_claims, jev=FakeJev(),
              client=cpc_client(at=repo))
    topics = _topics(repo / "build", 2026, 6)
    assert topics["schema_version"] == 2
    assert (topics["season"], topics["week"]) == (2026, 6)
    assert sorted(topics["teams"], key=int) == [str(n) for n in range(1, 13)]
    for answers in topics["teams"].values():
        assert {answer["topic"] for answer in answers} == LEAGUE_TOPICS
        # The build hands its raw week to the Topics, so both matchup Topics carry the matchup card.
        blocks = {answer["topic"]: answer["block"] for answer in answers}
        assert (blocks["last_matchup"]["kind"], blocks["last_matchup"]["final"]) == ("matchup", True)
        assert (blocks["next_matchup"]["kind"], blocks["next_matchup"]["final"]) == ("matchup", False)


def test_week_8_of_cpc_has_7_answers_for_each_of_the_12_teams_and_the_same_page(tmp_path):
    """AT-51 and AT-56: the command writes topics.json from the saved week, and page.json stays as published."""
    folder = _saved_week_8(tmp_path)
    page = run_page_json(folder, 2026, 8, client=cpc_client(at=folder))
    topics = _topics(folder / "build", 2026, 8)
    assert len(topics["teams"]) == 12
    for answers in topics["teams"].values():
        assert sorted(answer["topic"] for answer in answers) == sorted(LEAGUE_TOPICS)
        # Each Suggestion shows one real number, so each fact holds a digit.
        assert all(any(ch.isdigit() for ch in answer["fact"]) for answer in answers)
    # The Topics step writes only its own file, so page.json keeps each byte and the week folder gains one file.
    before = page.read_bytes()
    assert write_topics(folder / "build", 2026, 8) == page.parent / "topics.json"
    assert page.read_bytes() == before
    assert sorted(path.name for path in page.parent.iterdir()) == ["page.json", "topics.json"]


def test_a_league_answer_reuses_the_blurbs_and_the_data_of_the_week(tmp_path):
    folder = _saved_week_8(tmp_path)
    run_page_json(folder, 2026, 8, client=cpc_client(at=folder))
    answers = {a["topic"]: a for a in _topics(folder / "build", 2026, 8)["teams"][LIL_FRIDGE]}
    page = json.loads((CPC / "published" / "2026" / "week-08" / "page.json").read_text(encoding="utf-8"))
    rankings = json.loads((CPC / "build" / "2026" / "rankings.json").read_text(encoding="utf-8"))
    # The test names week 8, so a later weekly publish adds a week to rankings.json and breaks nothing.
    week_8 = next(w for w in rankings["weeks"] if w["week"] == 8)
    row = next(r for r in week_8["rows"] if r["roster_id"] == 3)

    ranked = answers["power_rankings"]
    assert ranked["fact"] == "6th, down 5"
    assert ranked["text"] == [" ".join(sentence["text"] for sentence in row["blurb"])]

    # Lil Fridge lost game 1 of week 8, 80.11 to 121.16, and its recap is the Answer text.
    last = answers["last_matchup"]
    assert last["fact"] == "Lost 80.11 to 121.16"
    assert last["text"] == [next(m["recap"] for m in page["matchups"] if m["id"] == 1)]
    assert [(r["label"], r["value"], r["you"]) for r in last["rows"]] == [
        ("Maye d'force B with U", "121.16", False), ("Lil Fridge", "80.11", True)]

    assert answers["next_matchup"]["fact"] == "Next: behold the lamb, 6-10"
    assert answers["next_matchup"]["text"] == [page["blurbs"]["next_week"]]
    assert answers["playoff_race"]["fact"] == "86% playoff odds"
    assert answers["your_season"]["fact"] == "10-6, 2nd of 12"
    assert answers["week_recap"]["fact"] == "You scored 80.11, 12th of 12"
    assert answers["week_recap"]["text"] == [page["blurbs"]["motw"]]
    # The list of the leaders leads the text, and the blurb of the week follows it.
    assert answers["leaders_trades"]["text"][1:] == [page["blurbs"]["position_leaders"]]


# Bo Girds, the team of the acceptance tests of the recap card, in each league.
BO_GIRDS = {"cpc": "6", "norcal": "7"}


def _published_week_9(tmp_path: Path, slug: str) -> Path:
    """A site folder with the published page.json of week 9 of one client and the two season files beside it."""
    published = client_dir(ROOT, slug) / "published" / "2026"
    week = tmp_path / "2026" / "week-09"
    week.mkdir(parents=True)
    shutil.copy(published / "week-09" / "page.json", week / "page.json")
    for name in ("rankings.json", "managers.json"):
        shutil.copy(published / name, tmp_path / "2026" / name)
    return tmp_path


def _recap_block(tmp_path: Path, slug: str) -> dict:
    site = _published_week_9(tmp_path, slug)
    write_topics(site, 2026, 9)
    topics = _topics(site, 2026, 9)
    assert topics["schema_version"] == 2
    answers = {a["topic"]: a for a in topics["teams"][BO_GIRDS[slug]]}
    return answers["week_recap"]["block"]


def test_the_cpc_recap_block_holds_the_score_the_place_the_strip_and_the_median(tmp_path):
    """AT-22 and AT-40: Bo Girds scored 114.07 in week 9 of cpc, 3rd of 12, over a median of 103.51."""
    block = _recap_block(tmp_path, "cpc")
    assert block["kind"] == "recap"
    assert (block["score"], block["place"], block["teams"]) == (114.07, 3, 12)
    assert block["median"] == 103.51
    assert (block["opponent"], block["opponent_score"]) == ("Teehee", 100.63)
    # The strip has one mark per team, high to low, and the mark of Your team carries `you`.
    assert len(block["strip"]) == 12
    assert [m["score"] for m in block["strip"]] == sorted((m["score"] for m in block["strip"]), reverse=True)
    assert [m["name"] for m in block["strip"] if m["you"]] == ["Bo Girds"]
    assert block["top"] == {"name": "Kenneth Walker III", "position": "RB", "points": 34.3, "projection": 20.07}
    # The sentence is the first sentence of the recap of the game of Your team.
    page = json.loads((CPC / "published" / "2026" / "week-09" / "page.json").read_text(encoding="utf-8"))
    recap = next(m["recap"] for m in page["matchups"] if m["id"] == 6)
    assert recap.startswith(block["sentence"])
    assert block["sentence"].endswith(".") and len(block["sentence"]) < len(recap)


def test_the_norcal_recap_block_has_no_median(tmp_path):
    """AT-23 and AT-40: norcal plays no median game, so its recap block has no median."""
    block = _recap_block(tmp_path, "norcal")
    assert (block["score"], block["opponent"], block["opponent_score"]) == (155.38, "kaiedmonds", 128.06)
    assert block["median"] is None
    assert len(block["strip"]) == 12


def _week_9(slug: str) -> Week:
    """The parsed raw week 9 of one client, as the build reads it."""
    raw = load_raw(client_dir(ROOT, slug) / "data" / "2026" / "week-09" / "raw")
    return parse_week(raw, week=9, points_key=league_settings(raw.league).points_key)


def _block(tmp_path: Path, slug: str, topic: str) -> dict:
    site = _published_week_9(tmp_path, slug)
    write_topics(site, 2026, 9, league_week=_week_9(slug))
    answers = {a["topic"]: a for a in _topics(site, 2026, 9)["teams"][BO_GIRDS[slug]]}
    return answers[topic]["block"]


def test_the_cpc_last_matchup_block_holds_the_final_scores_slot_by_slot(tmp_path):
    """AT-24 and AT-40: Bo Girds beat Teehee 114.07 to 100.63 in week 9 of cpc."""
    block = _block(tmp_path, "cpc", "last_matchup")
    assert block["kind"] == "matchup"
    assert block["final"] is True
    assert (block["you"]["name"], block["you"]["score"]) == ("Bo Girds", 114.07)
    assert (block["them"]["name"], block["them"]["score"]) == ("Teehee", 100.63)
    # A final card has no win odds: the game is over.
    assert block["odds"] is None
    # One row per starting slot, in the Sleeper order of the league, with the bench left out.
    assert [s["slot"] for s in block["slots"]] == ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "FLEX", "DEF"]
    # The points of the starters of each side add up to the final score.
    for side in ("you", "them"):
        points = sum(s[side]["points"] for s in block["slots"] if s[side])
        assert round(points, 2) == block[side]["score"]
    walker = next(s["you"] for s in block["slots"] if s["you"] and s["you"]["name"] == "Kenneth Walker III")
    assert (walker["position"], walker["points"]) == ("RB", 34.3)


def test_the_next_matchup_block_holds_the_projected_scores_of_week_10_in_both_leagues(tmp_path):
    """AT-40: the weekly build gives Your next matchup a projected card. The API makes it live in ticket 08."""
    for slug in ("cpc", "norcal"):
        block = _block(tmp_path / slug, slug, "next_matchup")
        league_week = _week_9(slug)
        page = json.loads((client_dir(ROOT, slug) / "published" / "2026" / "week-09" / "page.json").read_text())
        rid = int(BO_GIRDS[slug])
        pair = next(p for p in page["next"] if rid in (p["a"]["roster_id"], p["b"]["roster_id"]))
        other = pair["b"] if pair["a"]["roster_id"] == rid else pair["a"]
        assert block["kind"] == "matchup"
        assert block["final"] is False
        assert (block["you"]["roster_id"], block["them"]["roster_id"]) == (rid, other["roster_id"])
        assert block["them"]["name"] == other["name"]
        assert [s["slot"] for s in block["slots"]] == [
            slot for slot in league_week.roster_positions if slot != "BN"]
        projections = league_week.projections_ahead[10]
        for side in ("you", "them"):
            roster = league_week.rosters[block[side]["roster_id"]]
            # A slot is empty only when the roster holds no player for it: The Blue Tent of cpc holds no DEF.
            assert all(s["slot"] not in roster.values() for s in block["slots"] if s[side] is None)
            starters = [s[side] for s in block["slots"] if s[side]]
            # Each projection is the week 10 projection, so a player on a bye never starts over a bench player.
            assert all(p["points"] > 0 for p in starters)
            assert round(sum(p["points"] for p in starters), 2) == block[side]["score"]
        names = {pid: name for pid, (name, _) in league_week.roster_players.items()}
        mine = league_week.rosters[rid]
        best = max((pid for pid in mine if mine[pid] == "QB"), key=lambda pid: projections.get(pid, 0.0))
        assert block["slots"][0]["you"]["name"] == names[best]


def test_the_power_rankings_block_lists_each_team_with_its_rank_and_its_move(tmp_path):
    """AT-26 and AT-40: one row per team of cpc week 9, by rank, with the move in places since week 8."""
    block = _block(tmp_path, "cpc", "power_rankings")
    assert block["kind"] == "rank_movers"
    assert [(r["rank"], r["name"], r["move"]) for r in block["rows"]] == [
        (1, "Return of T Mac", 3), (2, "The Blue Tent", 3), (3, "All You Need Is Love", -2), (4, "Bo Girds", 3),
        (5, "London Cooking", 3), (6, "Teehee", -4), (7, "Maye d'force B with U", -4), (8, "Lil Fridge", -2),
        (9, "To Infinity and Bijan", 0), (10, "Unsolicited Dak Picks", 0), (11, "NFC Least", 1),
        (12, "behold the lamb", -1)]
    assert [r["name"] for r in block["rows"] if r["you"]] == ["Bo Girds"]
    norcal = _block(tmp_path / "norcal", "norcal", "power_rankings")
    assert norcal["kind"] == "rank_movers"
    assert len(norcal["rows"]) == 12


def test_the_cpc_ladder_block_lists_each_team_by_standing_with_its_odds_and_the_playoff_line(tmp_path):
    """AT-27 and AT-40: one row per team of cpc week 9 by standing, with its playoff odds and its record. The playoff
    line sits after the 6th row, as `settings.playoff_teams` of the raw league says."""
    block = _block(tmp_path, "cpc", "playoff_race")
    assert block["kind"] == "ladder"
    assert [(r["rank"], r["name"], r["record"]) for r in block["rows"]] == [
        (1, "All You Need Is Love", "12-6"), (2, "Bo Girds", "11-7"), (3, "London Cooking", "11-7"),
        (4, "Lil Fridge", "11-7"), (5, "The Blue Tent", "11-7"), (6, "Return of T Mac", "11-7"),
        (7, "Maye d'force B with U", "10-8"), (8, "Teehee", "8-10"), (9, "To Infinity and Bijan", "8-10"),
        (10, "Unsolicited Dak Picks", "6-12"), (11, "behold the lamb", "6-12"), (12, "NFC Least", "3-15")]
    league = json.loads((CPC / "data" / "2026" / "week-09" / "raw" / "league.json").read_text(encoding="utf-8"))
    assert block["playoff_teams"] == league["settings"]["playoff_teams"] == 6
    assert [r["name"] for r in block["rows"] if r["you"]] == ["Bo Girds"]
    # The odds of each row are the playoff odds of the week in rankings.json.
    rankings = json.loads((CPC / "published" / "2026" / "rankings.json").read_text(encoding="utf-8"))
    odds = {r["roster_id"]: r["odds"]["playoff"] for w in rankings["weeks"] if w["week"] == 9 for r in w["rows"]}
    assert {r["roster_id"]: r["odds"] for r in block["rows"]} == odds
    assert all(0 <= r["odds"] <= 100 for r in block["rows"])
    norcal = _block(tmp_path / "norcal", "norcal", "playoff_race")
    assert (norcal["kind"], len(norcal["rows"]), norcal["playoff_teams"]) == ("ladder", 12, 6)


def test_the_cpc_schedule_block_lists_the_opponents_of_weeks_10_to_14_by_their_standing(tmp_path):
    """AT-28 and AT-40: Bo Girds meets one opponent each week from 10 to 14, each with its standing and its record
    after week 9, against the playoff line of 6."""
    block = _block(tmp_path, "cpc", "your_season")
    assert block["kind"] == "schedule"
    assert block["playoff_teams"] == 6
    assert block["teams"] == 12
    assert [(r["week"], r["opponent"], r["rank"], r["record"]) for r in block["rows"]] == [
        (10, "The Blue Tent", 5, "11-7"), (11, "Maye d'force B with U", 7, "10-8"), (12, "London Cooking", 3, "11-7"),
        (13, "NFC Least", 12, "3-15"), (14, "Lil Fridge", 4, "11-7")]
    norcal = _block(tmp_path / "norcal", "norcal", "your_season")
    assert norcal["kind"] == "schedule"
    assert [r["week"] for r in norcal["rows"]] == [10, 11, 12, 13, 14]
    assert norcal["rows"][0]["opponent"] == "Davlionman"


def test_each_league_topic_but_leaders_and_trades_has_a_block_in_both_leagues(tmp_path):
    """AT-40: with the raw week, six league Topics carry a block in cpc and in norcal, and Position leaders and recent
    trades has none."""
    for slug in ("cpc", "norcal"):
        site = _published_week_9(tmp_path / slug, slug)
        write_topics(site, 2026, 9, league_week=_week_9(slug))
        topics = _topics(site, 2026, 9)
        assert topics["schema_version"] == 2
        for answers in topics["teams"].values():
            kinds = {a["topic"]: (a["block"] or {}).get("kind") for a in answers}
            assert kinds == {"week_recap": "recap", "last_matchup": "matchup", "next_matchup": "matchup",
                             "power_rankings": "rank_movers", "playoff_race": "ladder", "your_season": "schedule",
                             "leaders_trades": None}


def test_the_matchup_topics_have_no_block_without_the_raw_week(tmp_path):
    """The matchup cards read the lineups of the raw week. With no raw week, those two Topics have no block, and the
    blocks from the published files still come. The schedule strip reads the pairs of the raw week too."""
    site = _published_week_9(tmp_path, "cpc")
    write_topics(site, 2026, 9)
    for answers in _topics(site, 2026, 9)["teams"].values():
        kinds = {a["topic"]: (a["block"] or {}).get("kind") for a in answers}
        assert kinds == {"week_recap": "recap", "last_matchup": None, "next_matchup": None,
                         "power_rankings": "rank_movers", "playoff_race": "ladder", "your_season": None,
                         "leaders_trades": None}


def test_position_leaders_lists_one_leader_per_position_in_its_text_and_has_no_block(tmp_path):
    """AT-21: Position leaders and recent trades shows no block. Its text opens with a markdown list of the top scorer
    at each position of week 9, so the text block of the site draws it as a list. The blurb of the week follows it."""
    for slug in ("cpc", "norcal"):
        site = _published_week_9(tmp_path / slug, slug)
        write_topics(site, 2026, 9, league_week=_week_9(slug))
        page = json.loads((site / "2026" / "week-09" / "page.json").read_text(encoding="utf-8"))
        answer = next(a for a in _topics(site, 2026, 9)["teams"][BO_GIRDS[slug]] if a["topic"] == "leaders_trades")
        assert answer["block"] is None
        items = answer["text"][0].split("\n")
        groups = [group for group in page["leaders"] if group["rows"]]
        assert len(items) == len(groups)
        for item, group in zip(items, groups):
            top = group["rows"][0]
            assert item.startswith(f"- **{group['position']}** ")
            assert top["player"] in item
            assert top["team"] in item
        # The list takes the place of the rows, so the leaders show once.
        assert answer["rows"] == []
        assert answer["text"][1:] == [page["blurbs"]["position_leaders"]]
    # In cpc, Kenneth Walker III of Bo Girds led the backs with 34.3.
    cpc = next(a for a in _topics(tmp_path / "cpc", 2026, 9)["teams"]["6"] if a["topic"] == "leaders_trades")
    assert "- **RB** Kenneth Walker III, 34.3, Bo Girds" in cpc["text"][0].split("\n")
