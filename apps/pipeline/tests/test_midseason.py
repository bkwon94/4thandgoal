"""
Tests for the build of the midseason report: make midseason writes midseason.json into the build folder of the season,
from the real saved CPC data of 2026. test_pipeline.py checks that the weekly build never touches it.
"""
import json
import shutil
from functools import partial
from pathlib import Path

import pytest
from cpc import ROOT, cpc_client
from fakes import FakeWriter

from cornerstone.pipeline import BuildStopped, run_midseason
from cornerstone.value_models import VALUE_MODELS
from facts.writer import claude_call
from league.client import read_client_values
from league.models import Sentence, Verdict, VerifyOut, WriterOut
from league.paths import build_dir, client_dir, history_root, nflverse_cache_dir, week_dir

# The real saved data of CPC 2026. The tests copy it, so no test writes under clients/.
CPC_DATA = client_dir(ROOT, "cpc") / "data" / "2026"


def copy_cpc_week_8(client) -> None:
    """Copy the saved history and week 8 of the real CPC data into the client folder, and the NFL schedule of the
    fixtures into its NFL data. The sim reads the raw week and the schedule, which git ignores in the real cache."""
    shutil.copytree(CPC_DATA / "history", history_root(client.folder, 2026))
    shutil.copytree(CPC_DATA / "week-08", week_dir(client.folder, 2026, 8))
    nflverse_cache_dir(client.nfl_dir).mkdir(parents=True, exist_ok=True)
    shutil.copy(Path(__file__).parent / "fixtures" / "nflverse" / "games.csv", nflverse_cache_dir(client.nfl_dir))


def _cpc_week_8(tmp_path: Path):
    """A CPC client folder in `tmp_path` with the saved history and week 8 of the real CPC data."""
    client = cpc_client(at=tmp_path)
    copy_cpc_week_8(client)
    return client


def _call(*answers):
    """The Claude call of the build with a fake writer that gives `answers` in order. With none, each call fails, so
    each prose block gets its template blurb."""
    return partial(claude_call, writer=FakeWriter(list(answers)))


def _passed(count: int) -> VerifyOut:
    return VerifyOut(verdicts=[Verdict(index=i, supported=True, reason="The fact says so.") for i in range(count)])


# A blurb of the state of the league that passes the code check on the real CPC week 8 facts.
STATE_BLURB = WriterOut(sentences=[
    Sentence(text="All You Need Is Love sits at 11-5.", fact_ids=["ST.2.record"]),
    Sentence(text="Nobody saw that coming.", fact_ids=[]),
    Sentence(text="Lil Fridge has 909.55 points for.", fact_ids=["ST.3.points"]),
])
# A roast blurb of the state of the league. Each sentence cites a fact.
ROAST_BLURB = WriterOut(sentences=[
    Sentence(text="NFC Least is 3-13, 12th in the standings.", fact_ids=["ST.4.record"]),
    Sentence(text="Bo Girds has lost 4 head-to-head games in a row.", fact_ids=["ST.6.streak"]),
])


# The blurbs of the arcs and of Schedule luck that pass the code check on the real CPC week 8 facts.
ARCS_BLURB = WriterOut(sentences=[
    Sentence(text="Return of T Mac rode a win streak of 5 and a loss streak of 3.", fact_ids=["ARC.8.roller-coaster"]),
    Sentence(text="Bo Girds has the Collapse arc.", fact_ids=["ARC.6.collapse"]),
    Sentence(text="Nobody saw that coming.", fact_ids=[]),
])
ARCS_ROAST = WriterOut(sentences=[
    Sentence(text="Bo Girds is Snakebit at -2.18.", fact_ids=["ARC.6.snakebit"]),
    Sentence(text="Return of T Mac started 2-6.", fact_ids=["ARC.8.turnaround"]),
])
LUCK_BLURB = WriterOut(sentences=[
    Sentence(text="All You Need Is Love has a Schedule luck of +2.73.", fact_ids=["SL.2.luck"]),
    Sentence(text="Bo Girds would be 14-2 with the schedule of Maye d'force B with U.", fact_ids=["SW.6.best"]),
    Sentence(text="That is cruel.", fact_ids=[]),
])
LUCK_ROAST = WriterOut(sentences=[
    Sentence(text="Bo Girds does better with 10 other schedules than with its own.", fact_ids=["SW.most"]),
    Sentence(text="To Infinity and Bijan has 947.27 points against.", fact_ids=["SL.7.against"]),
])
# The blurbs of the opener and of the look ahead that pass the code check on the real CPC week 8 facts.
OPENER_BLURB = WriterOut(sentences=[
    Sentence(text="London Cooking leads the race at 16.8% title odds.", fact_ids=["OP.5.title"]),
    Sentence(text="All You Need Is Love leads at 11-5 with 9.7% title odds.", fact_ids=["OP.record"]),
    Sentence(text="Nobody owns this race.", fact_ids=[]),
])
OPENER_ROAST = WriterOut(sentences=[
    Sentence(text="All You Need Is Love is 11-5 and only 6th in title odds.", fact_ids=["OP.record"]),
    Sentence(text="Bo Girds has 16.3% title odds.", fact_ids=["OP.6.title"]),
])
LOOK_BLURB = WriterOut(sentences=[
    Sentence(text="Maye d'force B with U gets the softest schedule at 0.44.", fact_ids=["LA.9.rate"]),
    Sentence(text="behold the lamb gets the hardest at 0.56.", fact_ids=["LA.10.rate"]),
    Sentence(text="Good luck.", fact_ids=[]),
])
LOOK_ROAST = WriterOut(sentences=[
    Sentence(text="behold the lamb faces a 0.56 win rate.", fact_ids=["LA.10.rate"]),
    Sentence(text="NFC Least faces a 0.54 win rate too.", fact_ids=["LA.4.rate"]),
])
# The writer answers of the opener, which the build writes first.
OPENER_BUILD = [OPENER_BLURB, _passed(3), OPENER_ROAST, _passed(2)]
# The writer answers of a clean build, in page order: each blurb, then the verdicts that pass it.
CLEAN_BUILD = [*OPENER_BUILD, STATE_BLURB, _passed(3), ROAST_BLURB, _passed(2), ARCS_BLURB, _passed(3), ARCS_ROAST,
               _passed(2), LUCK_BLURB, _passed(3), LUCK_ROAST, _passed(2), LOOK_BLURB, _passed(3), LOOK_ROAST, _passed(2)]
# The verdicts of the recheck of the publish on a clean draft, in page order.
CLEAN_RECHECK = [_passed(3), _passed(2), _passed(3), _passed(2), _passed(3), _passed(2), _passed(3), _passed(2),
                 _passed(3), _passed(2)]


def _clean_call():
    return _call(*CLEAN_BUILD)


def _with_roast(client, tmp_path: Path, roast: str):
    """The client with the values of a local copy of the CPC client.toml that takes sim and midseason and sets
    `roast`. The real file never changes."""
    folder = tmp_path / "toml"
    folder.mkdir()
    text = (client_dir(ROOT, "cpc") / "client.toml").read_text(encoding="utf-8")
    text = text.replace('"analyzer"]', '"analyzer", "sim", "midseason"]', 1)
    (folder / "client.toml").write_text(text + f'\n[values.midseason]\nroast = "{roast}"\n', encoding="utf-8")
    return client.model_copy(update={"values": read_client_values(folder, VALUE_MODELS)})


def _report(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _state_rows(report: dict) -> dict[str, dict]:
    act = next(act for act in report["acts"] if act["key"] == "how-we-got-here")
    chapter = next(chapter for chapter in act["chapters"] if chapter["key"] == "state")
    return {row["name"]: row for row in chapter["facts"]["teams"]}


def test_the_build_writes_midseason_json_to_the_build_folder_of_the_season_and_nothing_to_published(tmp_path):
    # AT-1: the report goes live only through its own publish.
    client = _cpc_week_8(tmp_path)
    out = run_midseason(2026, 8, _call(), client=client)
    assert out == build_dir(client.folder) / "2026" / "midseason.json"
    report = _report(out)
    assert (report["schema_version"], report["season"], report["week"], report["takeover_end_week"]) == (1, 2026, 8, 9)
    assert [act["key"] for act in report["acts"]] == ["how-we-got-here", "what-comes-next"]
    assert not (client.folder / "published").exists()


def test_points_for_is_the_sum_of_the_weekly_scores(tmp_path):
    # AT-4: Sleeper says 901.65 after a stat correction. The standings sum says 900.65.
    rows = _state_rows(_report(run_midseason(2026, 8, _call(), client=_cpc_week_8(tmp_path))))
    assert rows["Maye d'force B with U"]["points_for"] == 900.65
    assert (rows["All You Need Is Love"]["wins"], rows["All You Need Is Love"]["losses"]) == (11, 5)
    assert rows["All You Need Is Love"]["rank"] == 1


def test_each_row_has_the_playoff_odds_of_the_sim_within_2_points_of_the_week(tmp_path):
    client = _cpc_week_8(tmp_path)
    saved = json.loads((CPC_DATA / "week-08" / "facts.json").read_text(encoding="utf-8"))["odds"]["teams"]
    rows = _state_rows(_report(run_midseason(2026, 8, _call(), client=client)))
    sim = json.loads((build_dir(client.folder) / "2026" / "sim.json").read_text(encoding="utf-8"))
    assert len(rows) == 12
    assert {row["roster_id"]: row["playoff_odds"] for row in rows.values()} == {
        int(rid): team["playoff"] for rid, team in sim["teams"].items()}
    for row in rows.values():
        assert abs(row["playoff_odds"] - saved[str(row["roster_id"])]["playoff"]) <= 2


def test_a_rerun_gives_the_same_file(tmp_path):
    client = _cpc_week_8(tmp_path)
    first = run_midseason(2026, 8, _call(), client=client).read_bytes()
    assert run_midseason(2026, 8, _call(), client=client).read_bytes() == first


def test_a_gap_in_the_history_stops_the_build_with_the_command_that_fills_it(tmp_path):
    client = _cpc_week_8(tmp_path)
    shutil.rmtree(history_root(client.folder, 2026) / "week-05")
    with pytest.raises(BuildStopped, match="cornerstone history --through 8"):
        run_midseason(2026, 8, _call(), client=client)
    assert not (build_dir(client.folder) / "2026" / "midseason.json").exists()


def test_a_week_with_no_saved_facts_stops_the_build_with_the_command_that_builds_it(tmp_path):
    client = _cpc_week_8(tmp_path)
    (week_dir(client.folder, 2026, 8) / "facts.json").unlink()
    with pytest.raises(BuildStopped, match="make build CLIENT=cpc WEEK=8"):
        run_midseason(2026, 8, _call(), client=client)



def test_the_review_file_shows_each_blurb_with_its_prose_block_its_facts_and_the_verifier_result(tmp_path):
    # AT-39.
    client = _cpc_week_8(tmp_path)
    run_midseason(2026, 8, _clean_call(), client=client)
    review = (build_dir(client.folder) / "2026" / "midseason-review.md").read_text(encoding="utf-8")
    state, roast = review.split("## state.roast")
    assert "## state: The state of the league" in state
    assert "3 to 6 sentences" in state
    assert "All You Need Is Love sits at 11-5. [ST.2.record]" in state
    assert "- ST.2.record: All You Need Is Love is 11-5, 1st in the standings." in state
    assert "Verifier: passed on attempt 1." in state
    assert "NFC Least is 3-13, 12th in the standings. [ST.4.record]" in roast
    assert "Verifier: passed on attempt 1." in roast


def _roasts(report: dict) -> list[dict]:
    return [chapter["roast"] for act in report["acts"] for chapter in act["chapters"] if chapter["roast"] is not None]


def test_each_roast_blurb_cites_a_fact_even_when_the_writer_gives_a_roast_with_none(tmp_path):
    # AT-40. The roast gets two attempts of two reaction sentences each, so the verifier fails both.
    no_fact = WriterOut(sentences=[Sentence(text="Oh no.", fact_ids=[]), Sentence(text="Truly awful.", fact_ids=[])])
    client = _cpc_week_8(tmp_path)
    report = _report(run_midseason(2026, 8, _call(*OPENER_BUILD, STATE_BLURB, _passed(3), no_fact, no_fact), client=client))
    roasts = _roasts(report)
    assert roasts
    for roast in roasts:
        assert any(sentence["fact_ids"] for sentence in roast["sentences"])
    review = (build_dir(client.folder) / "2026" / "midseason-review.md").read_text(encoding="utf-8")
    assert "a second reaction sentence" in review.split("## state.roast")[1]


def test_a_clean_build_keeps_the_roast_of_the_writer_with_its_cited_facts(tmp_path):
    report = _report(run_midseason(2026, 8, _clean_call(), client=_cpc_week_8(tmp_path)))
    assert [[s["fact_ids"] for s in roast["sentences"]] for roast in _roasts(report)] == [
        [["ST.4.record"], ["ST.6.streak"]], [["ARC.6.snakebit"], ["ARC.8.turnaround"]], [["SW.most"], ["SL.7.against"]],
        [["LA.10.rate"], ["LA.4.rate"]]]
    assert [s["fact_ids"] for s in report["opener"]["roast"]["sentences"]] == [["OP.record"], ["OP.6.title"]]


def test_with_the_roast_off_the_draft_has_no_roast_lines(tmp_path):
    # AT-41, on a local copy of client.toml.
    client = _with_roast(_cpc_week_8(tmp_path), tmp_path, "off")
    writer = FakeWriter([OPENER_BLURB, _passed(3), STATE_BLURB, _passed(3), ARCS_BLURB, _passed(3), LUCK_BLURB,
                         _passed(3), LOOK_BLURB, _passed(3)])
    report = _report(run_midseason(2026, 8, partial(claude_call, writer=writer), client=client))
    assert _roasts(report) == [] and report["opener"]["roast"] is None
    review = (build_dir(client.folder) / "2026" / "midseason-review.md").read_text(encoding="utf-8")
    assert "Roast: off." in review and "roast" not in review.split("Roast: off.")[1].lower()
    # The writer of each prose block hears that the roast is off, so its blurb holds no roast either.
    assert "Roast: off. Write no roast" in (writer.calls[0].system or "")
    assert len(writer.calls) == 10


def test_with_the_roast_warm_the_roast_block_gets_the_roast_rules_and_the_soft_step(tmp_path):
    client = _with_roast(_cpc_week_8(tmp_path), tmp_path, "warm")
    writer = FakeWriter(list(CLEAN_BUILD))
    report = _report(run_midseason(2026, 8, partial(claude_call, writer=writer), client=client))
    assert len(_roasts(report)) == 4
    # The calls of the state come after the four calls of the opener.
    roast_system = writer.calls[6].system or ""
    assert "Never roast life outside fantasy" in roast_system and "Roast: warm." in roast_system
    assert "Roast:" not in (writer.calls[4].system or "")


def _chapter(report: dict, key: str) -> dict:
    act = next(act for act in report["acts"] if act["key"] == "how-we-got-here")
    return next(chapter for chapter in act["chapters"] if chapter["key"] == key)


def test_act_one_holds_the_state_then_the_arcs_then_schedule_luck(tmp_path):
    report = _report(run_midseason(2026, 8, _call(), client=_cpc_week_8(tmp_path)))
    keys = [chapter["key"] for chapter in report["acts"][0]["chapters"]]
    assert keys.index("state") < keys.index("arcs") < keys.index("luck")


def test_the_arcs_of_return_of_t_mac_and_bo_girds(tmp_path):
    # AT-5. Return of T Mac also has an active streak of 5, a Heater, but the 2-arc limit drops it.
    teams = {team["name"]: team for team in
             _chapter(_report(run_midseason(2026, 8, _call(), client=_cpc_week_8(tmp_path))), "arcs")["facts"]["teams"]}
    assert len(teams) == 12
    mac = {arc["kind"]: arc for arc in teams["Return of T Mac"]["arcs"]}
    assert list(mac) == ["Roller coaster", "Turnaround"]
    assert (mac["Roller coaster"]["win_streak"], mac["Roller coaster"]["loss_streak"]) == (5, 3)
    turnaround = mac["Turnaround"]
    assert (turnaround["start"]["wins"], turnaround["start"]["losses"]) == (2, 6)
    assert (turnaround["now"]["wins"], turnaround["now"]["losses"]) == (7, 1)
    bo = {arc["kind"]: arc for arc in teams["Bo Girds"]["arcs"]}
    assert set(bo) == {"Snakebit", "Collapse"}
    assert bo["Snakebit"]["schedule_luck"] == -2.18


def test_schedule_luck_of_all_you_need_is_love_and_bo_girds_with_points_against_and_close_games(tmp_path):
    # AT-6.
    report = _report(run_midseason(2026, 8, _call(), client=_cpc_week_8(tmp_path)))
    luck = _chapter(report, "luck")["facts"]
    teams = {team["name"]: team for team in luck["teams"]}
    assert len(teams) == 12
    assert teams["All You Need Is Love"]["schedule_luck"] == 2.73
    assert teams["Bo Girds"]["schedule_luck"] == -2.18
    assert luck["teams"][0]["name"] == "All You Need Is Love"
    arcs = {team["name"]: [arc["kind"] for arc in team["arcs"]] for team in _chapter(report, "arcs")["facts"]["teams"]}
    assert "Smoke and mirrors" in arcs["All You Need Is Love"]
    assert "Snakebit" in arcs["Bo Girds"]
    state = _state_rows(report)
    for name, team in teams.items():
        assert team["points_against"] == state[name]["points_against"]
        assert 1 <= team["points_against_rank"] <= 12
        assert team["close_wins"] + team["close_losses"] + team["close_ties"] <= 8
    assert teams["To Infinity and Bijan"]["points_against_rank"] == 1


def test_the_schedule_swap_diagonal_is_the_standings_and_bo_girds_is_14_2_with_maye_s_schedule(tmp_path):
    # AT-7.
    report = _report(run_midseason(2026, 8, _call(), client=_cpc_week_8(tmp_path)))
    swap = _chapter(report, "luck")["facts"]["swap"]
    state = _state_rows(report)
    ids = {row["name"]: row["roster_id"] for row in state.values()}
    assert len(swap["rows"]) == 12 and all(len(row["cells"]) == 12 for row in swap["rows"])
    for row in swap["rows"]:
        own = next(cell for cell in row["cells"] if cell["schedule_of"] == row["roster_id"])
        assert (own["wins"], own["losses"], own["ties"]) == (
            state[row["name"]]["wins"], state[row["name"]]["losses"], state[row["name"]]["ties"])
    bo = next(row for row in swap["rows"] if row["name"] == "Bo Girds")
    maye = next(cell for cell in bo["cells"] if cell["schedule_of"] == ids["Maye d'force B with U"])
    assert (maye["wins"], maye["losses"]) == (14, 2)
    best = {callout["roster_id"]: callout for callout in swap["best_missed"]}
    assert best[ids["Bo Girds"]]["schedule_of"] == ids["Maye d'force B with U"]
    assert swap["most_better"] == {"roster_id": ids["Bo Girds"], "count": 10}


def _act_chapter(report: dict, act_key: str, key: str) -> dict:
    act = next(act for act in report["acts"] if act["key"] == act_key)
    return next(chapter for chapter in act["chapters"] if chapter["key"] == key)


def test_the_look_ahead_has_maye_s_schedule_softest_and_behold_the_lamb_s_hardest(tmp_path):
    # AT-24.
    report = _report(run_midseason(2026, 8, _call(), client=_cpc_week_8(tmp_path)))
    look = _act_chapter(report, "what-comes-next", "look-ahead")["facts"]
    teams = {team["name"]: team for team in look["teams"]}
    assert len(teams) == 12
    ids = {name: team["roster_id"] for name, team in teams.items()}
    assert look["softest"] == ids["Maye d'force B with U"]
    assert teams["Maye d'force B with U"]["opponents_rate"] == 0.44
    assert look["hardest"] == ids["behold the lamb"]
    assert teams["behold the lamb"]["opponents_rate"] == 0.56
    # Each team has the 6 games of weeks 9 to 14, each with the opponent's full record of the standings.
    state = _state_rows(report)
    for team in teams.values():
        assert [game["week"] for game in team["games"]] == list(range(9, 15))
        for game in team["games"]:
            assert (game["wins"], game["losses"]) == (state[game["name"]]["wins"], state[game["name"]]["losses"])


def test_the_opener_is_the_title_race_with_the_leaders_and_all_you_need_is_love_at_11_5(tmp_path):
    # AT-25. The title odds come from the sim, so the opener and the replay give one number.
    client = _cpc_week_8(tmp_path)
    report = _report(run_midseason(2026, 8, _call(), client=client))
    sim = json.loads((build_dir(client.folder) / "2026" / "sim.json").read_text(encoding="utf-8"))["teams"]
    title = {int(rid): team["title"] for rid, team in sim.items()}
    race = report["opener"]["facts"]
    assert report["opener"]["title"] == "The title race"
    best = sorted(title, key=lambda rid: -title[rid])[:3]
    assert [(leader["roster_id"], leader["title_odds"]) for leader in race["leaders"]] == [
        (rid, title[rid]) for rid in best]
    leader = race["record_leader"]
    assert (leader["name"], leader["wins"], leader["losses"]) == ("All You Need Is Love", 11, 5)
    assert leader["title_odds"] == title[leader["roster_id"]]
    # No team owns the title, and the record leader is not the favorite.
    assert race["leaders"][0]["title_odds"] < 50
    assert leader["roster_id"] not in best


def test_the_opener_and_the_look_ahead_have_their_prose_blocks_in_the_review_file(tmp_path):
    client = _cpc_week_8(tmp_path)
    report = _report(run_midseason(2026, 8, _clean_call(), client=client))
    review = (build_dir(client.folder) / "2026" / "midseason-review.md").read_text(encoding="utf-8")
    # The opener is the top of the page, so its blocks come first in the review file.
    assert review.index("## opener: The title race") < review.index("## opener.roast") < review.index("## state:")
    assert "## look-ahead: The look ahead" in review and "## look-ahead.roast" in review
    assert "London Cooking leads the race at 16.8% title odds. [OP.5.title]" in review
    assert "Maye d'force B with U gets the softest schedule at 0.44. [LA.9.rate]" in review
    assert review.count("Verifier: passed on attempt 1.") == 10
    assert report["opener"]["blurb"]["sentences"][0]["fact_ids"] == ["OP.5.title"]
    look = _act_chapter(report, "what-comes-next", "look-ahead")
    assert look["blurb"]["sentences"][0]["fact_ids"] == ["LA.9.rate"]
