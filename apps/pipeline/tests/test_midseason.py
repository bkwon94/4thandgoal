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
from midseason_inputs import copy_report_inputs, provider_now

from cornerstone.pipeline import BuildStopped, run_midseason
from cornerstone.value_models import VALUE_MODELS
from facts.writer import claude_call
from league.client import read_client_values
from league.models import Sentence, Verdict, VerifyOut, WriterOut
from league.paths import build_dir, client_dir, history_root, week_dir
from midseason.prose import is_roast

# The real saved data of CPC 2026. The tests copy it, so no test writes under clients/.
CPC_DATA = client_dir(ROOT, "cpc") / "data" / "2026"


def _cpc_week_8(tmp_path: Path):
    """A CPC client folder in `tmp_path` with the saved history and the week 8 facts of the real CPC data."""
    client = cpc_client(at=tmp_path)
    shutil.copytree(CPC_DATA / "history", history_root(client.folder, 2026))
    week_dir(client.folder, 2026, 8).mkdir(parents=True)
    shutil.copy(CPC_DATA / "week-08" / "facts.json", week_dir(client.folder, 2026, 8) / "facts.json")
    copy_report_inputs(client)
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

# A blurb for each prose block after the state of the league, in sheet order, each of two cited fact sentences. Each
# passes the code check on the real CPC week 8 facts. The writer of each gets the answer, then the verdicts.
CHAPTER_SENTENCES = [
    [("behold the lamb lost 9 starter games to injury, 1st in the league.", "IT.10"),
     ("Kyle Monangai missed 4 games as a starter of behold the lamb.", "IT.10.top")],
    [("The Blue Tent lost 5 starter games to injury, 2nd in the league.", "IT.1"),
     ("Davante Adams missed 2 games as a starter of The Blue Tent.", "IT.1.top")],
    [("Josh Allen is the QB #1 with 189.32 points, rostered by behold the lamb.", "TOP.QB.1"),
     ("Jahmyr Gibbs is the RB #1 with 178.8 points, rostered by Maye d'force B with U.", "TOP.RB.1")],
    [("Tampa Bay Buccaneers is the DEF #3 with 77.75 points, a free agent.", "TOP.DEF.3"),
     ("CeeDee Lamb is the WR #2 with 138.3 points, rostered by NFC Least.", "TOP.WR.2")],
    [(("Jaxon Smith-Njigba of Lil Fridge scores 7.68 points per game over what his volume says, over 8 games, so he "
       "is due to fall."), "PW.fall.1"),
     ("Kyler Murray is a free agent with 92.93 projected points through the regular season.", "PW.grab.1")],
    [(("Michael Wilson of London Cooking scores 5.65 points per game under what his volume says, over 8 games, so he "
       "is due to rise."), "PW.rise.1"),
     ("J.J. McCarthy is a free agent with 91.14 projected points through the regular season.", "PW.grab.2")],
]
CHAPTER_BLURBS = [WriterOut(sentences=[Sentence(text=text, fact_ids=[fid]) for text, fid in sentences])
                  for sentences in CHAPTER_SENTENCES]


def chapter_answers() -> list:
    """The writer answers of the prose blocks after the state of the league: each blurb, then its verdicts."""
    return [answer for blurb in CHAPTER_BLURBS for answer in (blurb, _passed(len(blurb.sentences)))]


def _clean_call():
    """The call of a clean build. The blurbs of the chapters cite the facts of the rosters now, so a clean build takes
    the provider of provider_now."""
    return _call(STATE_BLURB, _passed(3), ROAST_BLURB, _passed(2), *chapter_answers())


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


def test_each_row_has_the_playoff_odds_of_the_week(tmp_path):
    client = _cpc_week_8(tmp_path)
    saved = json.loads((CPC_DATA / "week-08" / "facts.json").read_text(encoding="utf-8"))["odds"]["teams"]
    rows = _state_rows(_report(run_midseason(2026, 8, _call(), client=client)))
    assert len(rows) == 12
    assert {row["roster_id"]: row["playoff_odds"] for row in rows.values()} == {
        int(rid): odds["playoff"] for rid, odds in saved.items()}


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
    run_midseason(2026, 8, _clean_call(), client=client, provider=provider_now(tmp_path))
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
    report = _report(run_midseason(2026, 8, _call(STATE_BLURB, _passed(3), no_fact, no_fact), client=client))
    roasts = _roasts(report)
    assert roasts
    for roast in roasts:
        assert any(sentence["fact_ids"] for sentence in roast["sentences"])
    review = (build_dir(client.folder) / "2026" / "midseason-review.md").read_text(encoding="utf-8")
    assert "a second reaction sentence" in review.split("## state.roast")[1]


def test_a_clean_build_keeps_the_roast_of_the_writer_with_its_cited_facts(tmp_path):
    report = _report(run_midseason(2026, 8, _clean_call(), client=_cpc_week_8(tmp_path),
                                   provider=provider_now(tmp_path)))
    state_roast = _chapter(report, "how-we-got-here", "state")["roast"]
    assert [s["fact_ids"] for s in state_roast["sentences"]] == [["ST.4.record"], ["ST.6.streak"]]


def test_with_the_roast_off_the_draft_has_no_roast_lines(tmp_path):
    # AT-41, on a local copy of client.toml.
    client = _with_roast(_cpc_week_8(tmp_path), tmp_path, "off")
    writer = FakeWriter([STATE_BLURB, _passed(3)])
    report = _report(run_midseason(2026, 8, partial(claude_call, writer=writer), client=client))
    assert _roasts(report) == []
    review = (build_dir(client.folder) / "2026" / "midseason-review.md").read_text(encoding="utf-8")
    assert "Roast: off." in review and "roast" not in review.split("Roast: off.")[1].lower()
    # The writer of the one prose block hears that the roast is off, so its blurb holds no roast either.
    assert "Roast: off. Write no roast" in (writer.calls[0].system or "")
    # No chapter of the report has a roast block.
    draft = json.loads((build_dir(client.folder) / "2026" / "midseason-facts.json").read_text(encoding="utf-8"))
    assert draft["sheet"]["chapters"] and not any(is_roast(c["key"]) for c in draft["sheet"]["chapters"])


def test_with_the_roast_warm_the_roast_block_gets_the_roast_rules_and_the_soft_step(tmp_path):
    client = _with_roast(_cpc_week_8(tmp_path), tmp_path, "warm")
    writer = FakeWriter([STATE_BLURB, _passed(3), ROAST_BLURB, _passed(2)])
    report = _report(run_midseason(2026, 8, partial(claude_call, writer=writer), client=client))
    assert _chapter(report, "how-we-got-here", "state")["roast"] is not None
    roast_system = writer.calls[2].system or ""
    assert "Never roast life outside fantasy" in roast_system and "Roast: warm." in roast_system
    assert "Roast:" not in (writer.calls[0].system or "")


def _chapter(report: dict, act_key: str, key: str) -> dict:
    act = next(act for act in report["acts"] if act["key"] == act_key)
    return next(chapter for chapter in act["chapters"] if chapter["key"] == key)


def _cpc_report(tmp_path: Path) -> dict:
    client = _cpc_week_8(tmp_path)
    return _report(run_midseason(2026, 8, _call(), client=client, provider=provider_now(tmp_path)))


def test_position_top_10_ranks_every_nfl_player_in_the_league_scoring_with_the_manager_now(tmp_path):
    # AT-10.
    report = _cpc_report(tmp_path)
    boards = {b["position"]: b["players"] for b in _chapter(report, "how-we-got-here", "top10")["facts"]["positions"]}
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
    watch = _chapter(_cpc_report(tmp_path), "what-comes-next", "watch")["facts"]
    assert [len(watch[key]) for key in ("due_to_rise", "due_to_fall", "grab_him_now")] == [3, 3, 3]
    assert "Jaxon Smith-Njigba" in [p["name"] for p in watch["due_to_fall"]]
    assert "Kyler Murray" in [p["name"] for p in watch["grab_him_now"]]
    assert all(p["games"] >= 4 for p in watch["due_to_rise"] + watch["due_to_fall"])


def test_the_injury_toll_has_each_team_and_behold_the_lamb_lost_the_most_starter_games(tmp_path):
    # AT-9. Quinshon Judkins has no Out row in week 6, so the fallback of the roster status counts his game.
    teams = _chapter(_cpc_report(tmp_path), "how-we-got-here", "injuries")["facts"]["teams"]
    assert len(teams) == 12
    first = teams[0]
    assert (first["name"], first["games"], first["rank"]) == ("behold the lamb", 9, 1)
    assert teams[1]["games"] < 9
    assert {(p["name"], p["games"]) for p in first["players"]} == {
        ("Kyle Monangai", 4), ("Saquon Barkley", 2), ("Emeka Egbuka", 2), ("Quinshon Judkins", 1)}


def test_the_acts_hold_the_chapters_in_report_order(tmp_path):
    report = _cpc_report(tmp_path)
    chapters = {act["key"]: [chapter["key"] for chapter in act["chapters"]] for act in report["acts"]}
    assert chapters["how-we-got-here"][0] == "state"
    assert chapters["how-we-got-here"].index("injuries") < chapters["how-we-got-here"].index("top10")
    assert chapters["what-comes-next"] == ["watch"]


def test_a_clean_build_keeps_the_blurb_of_the_writer_for_each_chapter(tmp_path):
    client = _cpc_week_8(tmp_path)
    report = _report(run_midseason(2026, 8, _clean_call(), client=client, provider=provider_now(tmp_path)))
    for act_key, key in (("how-we-got-here", "injuries"), ("how-we-got-here", "top10"), ("what-comes-next", "watch")):
        chapter = _chapter(report, act_key, key)
        assert not chapter["blurb"]["fallback"] and not chapter["roast"]["fallback"]
