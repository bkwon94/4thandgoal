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
from fakes import CPC_TRANSACTIONS, FakeWriter, FixtureProvider

from cornerstone.pipeline import BuildStopped, run_midseason
from cornerstone.value_models import VALUE_MODELS
from facts.writer import claude_call
from league.client import read_client_values
from league.models import Sentence, Verdict, VerifyOut, WriterOut
from league.paths import build_dir, client_dir, history_root, nflverse_cache_dir, week_dir

# The real saved data of CPC 2026. The tests copy it, so no test writes under clients/.
CPC_DATA = client_dir(ROOT, "cpc") / "data" / "2026"
# The provider of the report's fetch of each week's transactions: the saved CPC data with the full weeks of Sleeper.
# The rosters of CPC from Sleeper on 2026-11-05, after the week 9 moves. A manager dropped the Buccaneers DEF by then.
ROSTERS_NOW = Path(__file__).parent / "fixtures" / "midseason" / "cpc-rosters-now.json"
# The provider of the report's fetch of each week's transactions: the saved CPC data with the full weeks of Sleeper.
# Its live fetch gives the rosters now, which Position top 10 and the players to watch read.
CPC_PROVIDER = FixtureProvider(raw_dir=CPC_DATA / "week-08" / "raw", history_root=CPC_DATA / "history",
                               transactions=CPC_TRANSACTIONS, rosters_now=ROSTERS_NOW)


def copy_cpc_week_8(client) -> None:
    """Copy the saved history and week 8 of the real CPC data into the client folder, and the NFL schedule of the
    fixtures into its NFL data. The sim reads the raw week and the schedule, which git ignores in the real cache."""
    shutil.copytree(CPC_DATA / "history", history_root(client.folder, 2026))
    shutil.copytree(CPC_DATA / "week-08", week_dir(client.folder, 2026, 8))
    nflverse_cache_dir(client.nfl_dir).mkdir(parents=True, exist_ok=True)
    shutil.copy(Path(__file__).parent / "fixtures" / "nflverse" / "games.csv", nflverse_cache_dir(client.nfl_dir))
    prime_nflverse(client.nfl_dir)


# The real nflverse injury report of weeks 1 to 9 of 2026, as fetched on 2026-11-05, the rows of the ffverse id map
# for the drafted players of CPC and NorCal and for each player on a CPC roster, and the ffopportunity expected points
# cut to the columns that the reader reads.
NFLVERSE_2026_11_05 = Path(__file__).parent / "fixtures" / "nflverse-2026-11-05"


def prime_nflverse(nfl: Path) -> None:
    """Put the recorded injury report and id map in the nflverse cache of the NFL data folder `nfl`. A fresh copy is a
    fresh cache, so the build reads it and calls no network."""
    cache = nflverse_cache_dir(nfl)
    cache.mkdir(parents=True, exist_ok=True)
    for f in NFLVERSE_2026_11_05.iterdir():
        shutil.copy(f, cache / f.name)


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
    Sentence(text="behold the lamb would gain 4 wins with the schedule of Maye d'force B with U.",
             fact_ids=["SW.biggest"]),
    Sentence(text="That is cruel.", fact_ids=[]),
])
LUCK_ROAST = WriterOut(sentences=[
    Sentence(text="Teehee does better with 5 other schedules than with its own.", fact_ids=["SW.most"]),
    Sentence(text="NFC Least has 898 points against.", fact_ids=["SL.4.against"]),
])
# The blurbs of the opener and of the look ahead that pass the code check on the real CPC week 8 facts.
OPENER_BLURB = WriterOut(sentences=[
    Sentence(text="London Cooking leads the race at 16.8% title odds.", fact_ids=["OP.5.title"]),
    Sentence(text="All You Need Is Love leads at 11-5 with 9.7% title odds.", fact_ids=["OP.record", "OP.record.title"]),
    Sentence(text="Nobody owns this race.", fact_ids=[]),
])
OPENER_ROAST = WriterOut(sentences=[
    Sentence(text="All You Need Is Love is 11-5 and only 6th in title odds.", fact_ids=["OP.record", "OP.record.title"]),
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
# The blurbs of the draft steals and busts, the first chapter of Act II.
DRAFT_BLURB = WriterOut(sentences=[
    Sentence(text="NFC Least drafted Jalen Coker for $1.", fact_ids=["DV.steal.11646"]),
    Sentence(text="Jalen Coker is the 24th drafted WR by points, with 64.9 points.",
             fact_ids=["DV.steal.11646.points"]),
    Sentence(text="What a bargain.", fact_ids=[]),
])
DRAFT_ROAST = WriterOut(sentences=[
    Sentence(text="Unsolicited Dak Picks drafted A.J. Brown for $39.", fact_ids=["DV.bust.5859"]),
    Sentence(text="The bust of A.J. Brown is tagged just bad.", fact_ids=["DV.bust.5859.tag"]),
])
# The blurbs of the waivers and the trades of Act II, each in the shape that passes the code check.
WAIVERS_BLURB = WriterOut(sentences=[
    Sentence(text="Ollie Gordon II went to Unsolicited Dak Picks for $40.", fact_ids=["WV.hit.1"]),
    Sentence(text="The Blue Tent bid $36 on him and lost by $4.", fact_ids=["WV.outbid.1", "WV.outbid.1.margin"]),
    Sentence(text="Ouch.", fact_ids=[]),
])
WAIVERS_ROAST = WriterOut(sentences=[
    Sentence(text="To Infinity and Bijan paid $40 for Joe Mixon and got 0 starts.",
             fact_ids=["WV.miss.1", "WV.miss.1.value"]),
    Sentence(text="NFC Least paid $26 for Rico Dowdle and got 0 starts.", fact_ids=["WV.miss.3", "WV.miss.3.value"]),
])
TRADES_BLURB = WriterOut(sentences=[
    Sentence(text="To Infinity and Bijan won the week 7 trade with Return of T Mac.", fact_ids=["TR.4"]),
    Sentence(text="The gap is 68.4.", fact_ids=["TR.4"]),
    Sentence(text="Brutal.", fact_ids=[]),
])
TRADES_ROAST = WriterOut(sentences=[
    Sentence(text="Return of T Mac has a net of -34.2 points over the line since the week 7 trade.",
             fact_ids=["TR.4.8"]),
    Sentence(text="Return of T Mac is 3-1 since that trade.", fact_ids=["TR.4.8.since"]),
])
# The blurbs of the lineup choices and the record book, the last chapters of Act II. The spread rule moved the bench
# callout to Lil Fridge, so the lineup block may not name the four teams ahead of it.
LINEUP_BLURB = WriterOut(sentences=[
    Sentence(text="Lil Fridge left 85.02 points on the bench.", fact_ids=["LC.3"]),
    Sentence(text="The Blue Tent lost to behold the lamb by 9.04 in week 2.", fact_ids=["LC.1.2"]),
    Sentence(text="Painful.", fact_ids=[]),
])
LINEUP_ROAST = WriterOut(sentences=[
    Sentence(text="Maye d'force B with U left 83.48 points on the bench.", fact_ids=["LC.9"]),
    Sentence(text="Maye d'force B with U lost to The Blue Tent by 4.68 in week 7.", fact_ids=["LC.9.7"]),
])
RECORDS_BLURB = WriterOut(sentences=[
    Sentence(text="Maye d'force B with U scored 158.96 in week 5.", fact_ids=["RB.high"]),
    Sentence(text="Jahmyr Gibbs has 135.1 points over the line in his starts.", fact_ids=["AW.mvp"]),
    Sentence(text="Wild.", fact_ids=[]),
])
RECORDS_ROAST = WriterOut(sentences=[
    Sentence(text="To Infinity and Bijan scored 46.08 in week 6.", fact_ids=["RB.low"]),
    Sentence(text="The Blue Tent lost to All You Need Is Love by 0.4 in week 3.", fact_ids=["AW.heartbreak"]),
])
# The blurbs of the injury toll, Position top 10, and the players to watch, each in the shape that passes the code
# check on the real CPC week 8 facts with the rosters now.
INJURY_BLURB = WriterOut(sentences=[
    Sentence(text="behold the lamb lost 9 starter games to injury, 1st in the league.", fact_ids=["IT.10"]),
    Sentence(text="Kyle Monangai missed 4 games as a starter of behold the lamb.", fact_ids=["IT.10.top"]),
    Sentence(text="Rough.", fact_ids=[]),
])
INJURY_ROAST = WriterOut(sentences=[
    Sentence(text="The Blue Tent lost 5 starter games to injury, 2nd in the league.", fact_ids=["IT.1"]),
    Sentence(text="Davante Adams missed 2 games as a starter of The Blue Tent.", fact_ids=["IT.1.top"]),
])
TOP10_BLURB = WriterOut(sentences=[
    Sentence(text="Josh Allen is the QB #1 with 189.32 points, rostered by behold the lamb.", fact_ids=["TOP.QB.1"]),
    Sentence(text="Jahmyr Gibbs is the RB #1 with 178.8 points, rostered by Maye d'force B with U.",
             fact_ids=["TOP.RB.1"]),
    Sentence(text="Not bad.", fact_ids=[]),
])
TOP10_ROAST = WriterOut(sentences=[
    Sentence(text="Tampa Bay Buccaneers is the DEF #3 with 77.75 points, a free agent.", fact_ids=["TOP.DEF.3"]),
    Sentence(text="CeeDee Lamb is the WR #2 with 138.3 points, rostered by NFC Least.", fact_ids=["TOP.WR.2"]),
])
WATCH_BLURB = WriterOut(sentences=[
    Sentence(text="Jaxon Smith-Njigba of Lil Fridge scores 7.68 points per game over what his volume says, over 8 "
                  "games, so he is due to fall.", fact_ids=["PW.fall.1"]),
    Sentence(text="Kyler Murray is a free agent with 92.93 projected points through the regular season.",
             fact_ids=["PW.grab.1"]),
    Sentence(text="Go get him.", fact_ids=[]),
])
WATCH_ROAST = WriterOut(sentences=[
    Sentence(text="Michael Wilson of London Cooking scores 5.65 points per game under what his volume says, over 8 "
                  "games, so he is due to rise.", fact_ids=["PW.rise.1"]),
    Sentence(text="J.J. McCarthy is a free agent with 91.14 projected points through the regular season.",
             fact_ids=["PW.grab.2"]),
])
# The writer answers of a clean build, in page order: each blurb, then the verdicts that pass it.
CLEAN_BUILD = [*OPENER_BUILD, STATE_BLURB, _passed(3), ROAST_BLURB, _passed(2), ARCS_BLURB, _passed(3), ARCS_ROAST,
               _passed(2), LUCK_BLURB, _passed(3), LUCK_ROAST, _passed(2), INJURY_BLURB, _passed(3), INJURY_ROAST,
               _passed(2), TOP10_BLURB, _passed(3), TOP10_ROAST, _passed(2), DRAFT_BLURB, _passed(3), DRAFT_ROAST,
               _passed(2), WAIVERS_BLURB, _passed(3), WAIVERS_ROAST, _passed(2),
               TRADES_BLURB, _passed(3), TRADES_ROAST, _passed(2), LINEUP_BLURB, _passed(3), LINEUP_ROAST, _passed(2),
               RECORDS_BLURB, _passed(3), RECORDS_ROAST, _passed(2), LOOK_BLURB, _passed(3), LOOK_ROAST, _passed(2),
               WATCH_BLURB, _passed(3), WATCH_ROAST, _passed(2)]
# The verdicts of the recheck of the publish on a clean draft, in page order.
CLEAN_RECHECK = [_passed(3), _passed(2)] * 13


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
    out = run_midseason(2026, 8, _call(), client=client, provider=CPC_PROVIDER)
    assert out == build_dir(client.folder) / "2026" / "midseason.json"
    report = _report(out)
    assert (report["schema_version"], report["season"], report["week"], report["takeover_end_week"]) == (1, 2026, 8, 9)
    assert [act["key"] for act in report["acts"]] == ["how-we-got-here", "the-moves", "what-comes-next"]
    assert not (client.folder / "published").exists()


def test_points_for_is_the_sum_of_the_weekly_scores(tmp_path):
    # AT-4: Sleeper says 901.65 after a stat correction. The standings sum says 900.65.
    rows = _state_rows(_report(run_midseason(2026, 8, _call(), client=_cpc_week_8(tmp_path), provider=CPC_PROVIDER)))
    assert rows["Maye d'force B with U"]["points_for"] == 900.65
    assert (rows["All You Need Is Love"]["wins"], rows["All You Need Is Love"]["losses"]) == (11, 5)
    assert rows["All You Need Is Love"]["rank"] == 1


def test_each_row_has_the_playoff_odds_of_the_sim_within_2_points_of_the_week(tmp_path):
    client = _cpc_week_8(tmp_path)
    saved = json.loads((CPC_DATA / "week-08" / "facts.json").read_text(encoding="utf-8"))["odds"]["teams"]
    rows = _state_rows(_report(run_midseason(2026, 8, _call(), client=client, provider=CPC_PROVIDER)))
    sim = json.loads((build_dir(client.folder) / "2026" / "sim.json").read_text(encoding="utf-8"))
    assert len(rows) == 12
    assert {row["roster_id"]: row["playoff_odds"] for row in rows.values()} == {
        int(rid): team["playoff"] for rid, team in sim["teams"].items()}
    for row in rows.values():
        assert abs(row["playoff_odds"] - saved[str(row["roster_id"])]["playoff"]) <= 2


def test_a_rerun_gives_the_same_file(tmp_path):
    client = _cpc_week_8(tmp_path)
    first = run_midseason(2026, 8, _call(), client=client, provider=CPC_PROVIDER).read_bytes()
    assert run_midseason(2026, 8, _call(), client=client, provider=CPC_PROVIDER).read_bytes() == first


def test_a_gap_in_the_history_stops_the_build_with_the_command_that_fills_it(tmp_path):
    client = _cpc_week_8(tmp_path)
    shutil.rmtree(history_root(client.folder, 2026) / "week-05")
    with pytest.raises(BuildStopped, match="cornerstone history --through 8"):
        run_midseason(2026, 8, _call(), client=client, provider=CPC_PROVIDER)
    assert not (build_dir(client.folder) / "2026" / "midseason.json").exists()


def test_a_week_with_no_saved_facts_stops_the_build_with_the_command_that_builds_it(tmp_path):
    client = _cpc_week_8(tmp_path)
    (week_dir(client.folder, 2026, 8) / "facts.json").unlink()
    with pytest.raises(BuildStopped, match="make build CLIENT=cpc WEEK=8"):
        run_midseason(2026, 8, _call(), client=client, provider=CPC_PROVIDER)



def test_the_review_file_shows_each_blurb_with_its_prose_block_its_facts_and_the_verifier_result(tmp_path):
    # AT-39.
    client = _cpc_week_8(tmp_path)
    run_midseason(2026, 8, _clean_call(), client=client, provider=CPC_PROVIDER)
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
    call = _call(*OPENER_BUILD, STATE_BLURB, _passed(3), no_fact, no_fact)
    report = _report(run_midseason(2026, 8, call, client=client, provider=CPC_PROVIDER))
    roasts = _roasts(report)
    assert roasts
    for roast in roasts:
        assert any(sentence["fact_ids"] for sentence in roast["sentences"])
    review = (build_dir(client.folder) / "2026" / "midseason-review.md").read_text(encoding="utf-8")
    assert "the blurb cites no fact" in review.split("## state.roast")[1]


def test_a_clean_build_keeps_the_roast_of_the_writer_with_its_cited_facts(tmp_path):
    report = _report(run_midseason(2026, 8, _clean_call(), client=_cpc_week_8(tmp_path), provider=CPC_PROVIDER))
    assert [[s["fact_ids"] for s in roast["sentences"]] for roast in _roasts(report)] == [
        [["ST.4.record"], ["ST.6.streak"]], [["ARC.6.snakebit"], ["ARC.8.turnaround"]], [["SW.most"], ["SL.4.against"]],
        [["IT.1"], ["IT.1.top"]], [["TOP.DEF.3"], ["TOP.WR.2"]],
        [["DV.bust.5859"], ["DV.bust.5859.tag"]], [["WV.miss.1", "WV.miss.1.value"], ["WV.miss.3", "WV.miss.3.value"]], [["TR.4.8"], ["TR.4.8.since"]],
        [["LC.9"], ["LC.9.7"]], [["RB.low"], ["AW.heartbreak"]], [["LA.10.rate"], ["LA.4.rate"]],
        [["PW.rise.1"], ["PW.grab.2"]]]
    assert [s["fact_ids"] for s in report["opener"]["roast"]["sentences"]] == [["OP.record", "OP.record.title"],
                                                                              ["OP.6.title"]]


def test_with_the_roast_off_the_draft_has_no_roast_lines(tmp_path):
    # AT-41, on a local copy of client.toml.
    client = _with_roast(_cpc_week_8(tmp_path), tmp_path, "off")
    writer = FakeWriter([OPENER_BLURB, _passed(3), STATE_BLURB, _passed(3), ARCS_BLURB, _passed(3), LUCK_BLURB,
                         _passed(3), INJURY_BLURB, _passed(3), TOP10_BLURB, _passed(3), DRAFT_BLURB, _passed(3),
                         WAIVERS_BLURB, _passed(3), TRADES_BLURB, _passed(3), LINEUP_BLURB, _passed(3), RECORDS_BLURB,
                         _passed(3), LOOK_BLURB, _passed(3), WATCH_BLURB, _passed(3)])
    report = _report(run_midseason(2026, 8, partial(claude_call, writer=writer), client=client, provider=CPC_PROVIDER))
    assert _roasts(report) == [] and report["opener"]["roast"] is None
    review = (build_dir(client.folder) / "2026" / "midseason-review.md").read_text(encoding="utf-8")
    assert "Roast: off." in review and "roast" not in review.split("Roast: off.")[1].lower()
    # The writer of each prose block hears that the roast is off, so its blurb holds no roast either.
    assert "Roast: off. Write no roast" in (writer.calls[0].system or "")
    assert len(writer.calls) == 26


def test_with_the_roast_warm_the_roast_block_gets_the_roast_rules_and_the_soft_step(tmp_path):
    client = _with_roast(_cpc_week_8(tmp_path), tmp_path, "warm")
    writer = FakeWriter(list(CLEAN_BUILD))
    report = _report(run_midseason(2026, 8, partial(claude_call, writer=writer), client=client, provider=CPC_PROVIDER))
    assert len(_roasts(report)) == 12
    # The calls of the state come after the four calls of the opener.
    roast_system = writer.calls[6].system or ""
    assert "Never roast life outside fantasy" in roast_system and "Roast: warm." in roast_system
    assert "Roast:" not in (writer.calls[4].system or "")


def _chapter(report: dict, key: str) -> dict:
    """The chapter `key` of any act. Each key is on one chapter only."""
    return next(chapter for act in report["acts"] for chapter in act["chapters"] if chapter["key"] == key)


def test_act_one_holds_the_state_then_the_arcs_then_schedule_luck(tmp_path):
    report = _report(run_midseason(2026, 8, _call(), client=_cpc_week_8(tmp_path), provider=CPC_PROVIDER))
    keys = [chapter["key"] for chapter in report["acts"][0]["chapters"]]
    assert keys.index("state") < keys.index("arcs") < keys.index("luck")


def test_the_arcs_of_return_of_t_mac_and_bo_girds(tmp_path):
    # AT-5. Return of T Mac also has an active streak of 5, a Heater, but the 2-arc limit drops it.
    teams = {team["name"]: team for team in
             _chapter(_report(run_midseason(2026, 8, _call(), client=_cpc_week_8(tmp_path), provider=CPC_PROVIDER)), "arcs")["facts"]["teams"]}
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
    report = _report(run_midseason(2026, 8, _call(), client=_cpc_week_8(tmp_path), provider=CPC_PROVIDER))
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
    report = _report(run_midseason(2026, 8, _call(), client=_cpc_week_8(tmp_path), provider=CPC_PROVIDER))
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
    # Bo Girds has the most schedules better than its own, 10, but it holds 3 headlines. So the spread rule gives the
    # callout to the next team that needs one, and the grid still shows each record of Bo Girds.
    assert swap["most_better"] == {"roster_id": ids["Teehee"], "count": 5, "place": 4}


def test_the_look_ahead_has_maye_s_schedule_softest_and_behold_the_lamb_s_hardest(tmp_path):
    # AT-24.
    report = _report(run_midseason(2026, 8, _call(), client=_cpc_week_8(tmp_path), provider=CPC_PROVIDER))
    look = _chapter(report, "look-ahead")["facts"]
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
    report = _report(run_midseason(2026, 8, _call(), client=client, provider=CPC_PROVIDER))
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
    report = _report(run_midseason(2026, 8, _clean_call(), client=client, provider=CPC_PROVIDER))
    review = (build_dir(client.folder) / "2026" / "midseason-review.md").read_text(encoding="utf-8")
    # The opener is the top of the page, so its blocks come first in the review file.
    assert review.index("## opener: The title race") < review.index("## opener.roast") < review.index("## state:")
    assert "## look-ahead: The look ahead" in review and "## look-ahead.roast" in review
    assert "London Cooking leads the race at 16.8% title odds. [OP.5.title]" in review
    assert "Maye d'force B with U gets the softest schedule at 0.44. [LA.9.rate]" in review
    assert review.count("Verifier: passed on attempt 1.") == 26
    assert report["opener"]["blurb"]["sentences"][0]["fact_ids"] == ["OP.5.title"]
    look = _chapter(report, "look-ahead")
    assert look["blurb"]["sentences"][0]["fact_ids"] == ["LA.9.rate"]


def _cpc_report(tmp_path: Path) -> dict:
    return _report(run_midseason(2026, 8, _call(), client=_cpc_week_8(tmp_path), provider=CPC_PROVIDER))


def test_position_top_10_ranks_every_nfl_player_in_the_league_scoring_with_the_manager_now(tmp_path):
    # AT-10.
    boards = {b["position"]: b["players"] for b in _chapter(_cpc_report(tmp_path), "top10")["facts"]["positions"]}
    # CPC starts a DEF and no kicker, so the boards are the positions of its lineup.
    assert list(boards) == ["QB", "RB", "WR", "TE", "DEF"]
    assert all(len(players) == 10 for players in boards.values())
    qb = boards["QB"][0]
    assert (qb["rank"], qb["name"], qb["points"], qb["manager"]) == (1, "Josh Allen", 189.32, "behold the lamb")
    defense = boards["DEF"][2]
    assert (defense["rank"], defense["name"], defense["tag"], defense["roster_id"]) == (
        3, "Tampa Bay Buccaneers", "Free agent", None)


def test_the_players_to_watch_name_3_players_each(tmp_path):
    # AT-23.
    watch = _chapter(_cpc_report(tmp_path), "watch")["facts"]
    assert [len(watch[key]) for key in ("due_to_rise", "due_to_fall", "grab_him_now")] == [3, 3, 3]
    assert "Jaxon Smith-Njigba" in [p["name"] for p in watch["due_to_fall"]]
    assert "Kyler Murray" in [p["name"] for p in watch["grab_him_now"]]
    assert all(p["games"] >= 4 for p in watch["due_to_rise"] + watch["due_to_fall"])


def test_the_injury_toll_has_each_team_and_behold_the_lamb_lost_the_most_starter_games(tmp_path):
    # AT-9. Quinshon Judkins has no Out row in week 6, so the fallback of the roster status counts his game.
    teams = _chapter(_cpc_report(tmp_path), "injuries")["facts"]["teams"]
    assert len(teams) == 12
    first = teams[0]
    assert (first["name"], first["games"], first["rank"]) == ("behold the lamb", 9, 1)
    assert teams[1]["games"] < 9
    assert {(p["name"], p["games"]) for p in first["players"]} == {
        ("Kyle Monangai", 4), ("Saquon Barkley", 2), ("Emeka Egbuka", 2), ("Quinshon Judkins", 1)}


def test_the_acts_hold_the_chapters_in_page_order(tmp_path):
    report = _cpc_report(tmp_path)
    chapters = {act["key"]: [chapter["key"] for chapter in act["chapters"]] for act in report["acts"]}
    assert chapters["how-we-got-here"] == ["state", "arcs", "luck", "injuries", "top10"]
    assert chapters["what-comes-next"] == ["look-ahead", "watch"]


def test_a_clean_build_keeps_the_blurb_of_the_writer_for_each_chapter(tmp_path):
    report = _report(run_midseason(2026, 8, _clean_call(), client=_cpc_week_8(tmp_path), provider=CPC_PROVIDER))
    for key in ("injuries", "top10", "lineup", "records", "watch"):
        chapter = _chapter(report, key)
        assert not chapter["blurb"]["fallback"] and not chapter["roast"]["fallback"]


def test_the_report_tile_shows_the_title_odds_of_the_title_favorite(tmp_path):
    # AT-45. The home tile shows one big fact of the title race: London Cooking leads at 16.8% title odds.
    tile = _cpc_report(tmp_path)["tile"]
    assert tile == {"label": "Title favorite", "value": "16.8%", "note": "London Cooking"}


def test_london_cooking_lost_week_2_by_1_67_with_27_54_points_on_the_bench(tmp_path):
    # AT-18.
    teams = {team["name"]: team for team in _chapter(_cpc_report(tmp_path), "lineup")["facts"]["teams"]}
    assert len(teams) == 12
    week = next(week for week in teams["London Cooking"]["lost_with_better"] if week["week"] == 2)
    assert (week["margin"], week["bench_points"]) == (1.67, 27.54)
    assert week["best"] > week["score"] + week["margin"]


def test_the_record_book_high_is_maye_in_week_5_and_the_closest_game_is_0_4_in_week_3(tmp_path):
    # AT-19.
    book = _chapter(_cpc_report(tmp_path), "records")["facts"]
    assert (book["high"]["score"], book["high"]["team"], book["high"]["week"]) == (158.96, "Maye d'force B with U", 5)
    closest = book["closest"]
    assert (closest["margin"], closest["winner"], closest["loser"], closest["week"]) == (
        0.4, "All You Need Is Love", "The Blue Tent", 3)


def test_the_seven_awards_each_have_a_winner_and_a_fact(tmp_path):
    # AT-20.
    awards = {award["key"]: award for award in _chapter(_cpc_report(tmp_path), "records")["facts"]["awards"]}
    assert len(awards) == 7 and all(award["team"] and award["fact"] for award in awards.values())
    assert awards["mvp"]["player"] == "Jahmyr Gibbs"
    assert (awards["most-active"]["team"], awards["most-active"]["value"]) == ("Bo Girds", 42)
    assert (awards["set-and-forget"]["team"], awards["set-and-forget"]["value"]) == ("London Cooking", 3)
    assert (awards["bench-crime"]["team"], awards["bench-crime"]["week"]) == ("London Cooking", 2)
    # Each game of the record book shows once: Heartbreak and Beatdown are its closest game and its biggest margin.
    assert awards["heartbreak"]["in_record_book"] and awards["beatdown"]["in_record_book"]
    assert awards["heartbreak"]["team"] == "The Blue Tent"


def test_act_two_ends_on_the_lineup_choices_then_the_record_book(tmp_path):
    keys = [chapter["key"] for chapter in _cpc_report(tmp_path)["acts"][1]["chapters"]]
    assert keys == ["draft", "waivers", "trades", "lineup", "records"]


def test_the_spread_rule_gives_each_team_1_to_3_headlines_and_moves_both_swap_callouts_off_bo_girds(tmp_path):
    # AT-22.
    client = _cpc_week_8(tmp_path)
    report = _report(run_midseason(2026, 8, _call(), client=client, provider=CPC_PROVIDER))
    ids = {name: row["roster_id"] for name, row in _state_rows(report).items()}
    headlines = report["headlines"]
    for rid in ids.values():
        assert 1 <= sum(h["roster_id"] == rid for h in headlines) <= 3
    bo = ids["Bo Girds"]
    assert sorted(h["key"] for h in headlines if h["roster_id"] == bo) == [
        "arc.collapse", "arc.snakebit", "award.most-active"]
    swap = _chapter(report, "luck")["facts"]["swap"]
    callouts = {h["key"]: h for h in headlines if h["kind"] == "callout"}
    for key, field in (("luck.most_better", "most_better"), ("luck.biggest_miss", "biggest_miss")):
        assert swap[field]["roster_id"] != bo
        assert (callouts[key]["roster_id"], callouts[key]["place"]) == (swap[field]["roster_id"], swap[field]["place"])
    # The prose block of Schedule luck keeps Bo Girds in its scope, and its callout fact says that Bo Girds is not the
    # headline of the callout.
    sheet = _prose_blocks(client)
    assert "Bo Girds" in sheet["luck"]["scope_teams"]
    note = sheet["facts"]["CO.luck.most_better"]["text"]
    assert note.startswith("The callout of the most schedules better than its own names Teehee. Bo Girds and ")
    assert note.endswith(" are not the headline of this callout.")


def _prose_blocks(client) -> dict:
    """The prose blocks of the saved facts of the draft by key, and the facts by id under "facts"."""
    draft = json.loads((build_dir(client.folder) / "2026" / "midseason-facts.json").read_text(encoding="utf-8"))
    return {**{chapter["key"]: chapter for chapter in draft["sheet"]["chapters"]}, "facts": draft["sheet"]["facts"]}


def test_a_team_moved_off_a_callout_keeps_its_facts_in_the_prose_block(tmp_path):
    # Brian chose the loose rule: the trades block holds both Robberies, and the lineup block names London Cooking.
    client = _cpc_week_8(tmp_path)
    run_midseason(2026, 8, _call(), client=client, provider=CPC_PROVIDER)
    sheet = _prose_blocks(client)
    robberies = [fid for fid in sheet["trades"]["fact_ids"] if "The Trade result is Robbery" in sheet["facts"][fid]["text"]]
    assert robberies == ["TR.1", "TR.2"]
    assert "London Cooking" in sheet["lineup"]["scope_teams"]
    assert "LC.5" in sheet["lineup"]["fact_ids"]
    assert "London Cooking" in sheet["facts"]["CO.lineup.bench"]["text"]
