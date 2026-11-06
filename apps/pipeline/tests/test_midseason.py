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
from fakes import CPC_DRAFT_FIXTURES, FakeWriter, FixtureProvider

from cornerstone.pipeline import BuildStopped, run_midseason
from cornerstone.value_models import VALUE_MODELS
from facts.writer import claude_call
from league.client import read_client_values
from league.models import Sentence, Verdict, VerifyOut, WriterOut
from league.paths import build_dir, client_dir, history_root, nflverse_cache_dir, week_dir

# The real saved data of CPC 2026. The tests copy it, so no test writes under clients/.
CPC_DATA = client_dir(ROOT, "cpc") / "data" / "2026"
# The fake provider of the build: the real CPC week 8 players file and the real CPC draft.
CPC_PROVIDER = FixtureProvider(raw_dir=CPC_DATA / "week-08" / "raw", draft_dir=CPC_DRAFT_FIXTURES)
# The real nflverse injury report of weeks 1 to 9 of 2026, as fetched on 2026-11-05, and the rows of the ffverse id
# map for the drafted players of CPC and NorCal.
NFLVERSE_2026_11_05 = Path(__file__).parent / "fixtures" / "nflverse-2026-11-05"


def prime_nflverse(nfl: Path) -> None:
    """Put the recorded injury report and id map in the nflverse cache of the NFL data folder `nfl`. A fresh copy is a
    fresh cache, so the build reads it and calls no network."""
    cache = nflverse_cache_dir(nfl)
    cache.mkdir(parents=True, exist_ok=True)
    for f in NFLVERSE_2026_11_05.iterdir():
        shutil.copy(f, cache / f.name)


def _cpc_week_8(tmp_path: Path):
    """A CPC client folder in `tmp_path` with the saved history and the week 8 facts of the real CPC data."""
    client = cpc_client(at=tmp_path)
    shutil.copytree(CPC_DATA / "history", history_root(client.folder, 2026))
    week_dir(client.folder, 2026, 8).mkdir(parents=True)
    shutil.copy(CPC_DATA / "week-08" / "facts.json", week_dir(client.folder, 2026, 8) / "facts.json")
    prime_nflverse(client.nfl_dir)
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


# A blurb and a roast of the draft steals and busts that pass the code check on the real CPC week 8 facts.
DRAFT_BLURB = WriterOut(sentences=[
    Sentence(text="Bo Girds drafted Matthew Golden for $2.", fact_ids=["DV.steal.12501"]),
    Sentence(text="Matthew Golden is the 7th drafted WR by points, with 110 points.",
             fact_ids=["DV.steal.12501.points"]),
])
DRAFT_ROAST = WriterOut(sentences=[
    Sentence(text="Unsolicited Dak Picks drafted A.J. Brown for $39.", fact_ids=["DV.bust.5859"]),
    Sentence(text="The bust of A.J. Brown is tagged just bad.", fact_ids=["DV.bust.5859.tag"]),
])


def _clean_call():
    return _call(STATE_BLURB, _passed(3), ROAST_BLURB, _passed(2), DRAFT_BLURB, _passed(2), DRAFT_ROAST, _passed(2))


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
    assert [act["key"] for act in report["acts"]] == ["how-we-got-here", "the-moves"]
    assert not (client.folder / "published").exists()


def test_points_for_is_the_sum_of_the_weekly_scores(tmp_path):
    # AT-4: Sleeper says 901.65 after a stat correction. The standings sum says 900.65.
    rows = _state_rows(_report(run_midseason(2026, 8, _call(), client=_cpc_week_8(tmp_path), provider=CPC_PROVIDER)))
    assert rows["Maye d'force B with U"]["points_for"] == 900.65
    assert (rows["All You Need Is Love"]["wins"], rows["All You Need Is Love"]["losses"]) == (11, 5)
    assert rows["All You Need Is Love"]["rank"] == 1


def test_each_row_has_the_playoff_odds_of_the_week(tmp_path):
    client = _cpc_week_8(tmp_path)
    saved = json.loads((CPC_DATA / "week-08" / "facts.json").read_text(encoding="utf-8"))["odds"]["teams"]
    rows = _state_rows(_report(run_midseason(2026, 8, _call(), client=client, provider=CPC_PROVIDER)))
    assert len(rows) == 12
    assert {row["roster_id"]: row["playoff_odds"] for row in rows.values()} == {
        int(rid): odds["playoff"] for rid, odds in saved.items()}


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
    report = _report(run_midseason(2026, 8, _call(STATE_BLURB, _passed(3), no_fact, no_fact), client=client, provider=CPC_PROVIDER))
    roasts = _roasts(report)
    assert roasts
    for roast in roasts:
        assert any(sentence["fact_ids"] for sentence in roast["sentences"])
    review = (build_dir(client.folder) / "2026" / "midseason-review.md").read_text(encoding="utf-8")
    assert "a second reaction sentence" in review.split("## state.roast")[1]


def test_a_clean_build_keeps_the_roast_of_the_writer_with_its_cited_facts(tmp_path):
    report = _report(run_midseason(2026, 8, _clean_call(), client=_cpc_week_8(tmp_path), provider=CPC_PROVIDER))
    assert [[s["fact_ids"] for s in roast["sentences"]] for roast in _roasts(report)] == [
        [["ST.4.record"], ["ST.6.streak"]], [["DV.bust.5859"], ["DV.bust.5859.tag"]]]


def test_with_the_roast_off_the_draft_has_no_roast_lines(tmp_path):
    # AT-41, on a local copy of client.toml.
    client = _with_roast(_cpc_week_8(tmp_path), tmp_path, "off")
    writer = FakeWriter([STATE_BLURB, _passed(3), DRAFT_BLURB, _passed(2)])
    report = _report(run_midseason(2026, 8, partial(claude_call, writer=writer), client=client, provider=CPC_PROVIDER))
    assert _roasts(report) == []
    review = (build_dir(client.folder) / "2026" / "midseason-review.md").read_text(encoding="utf-8")
    assert "Roast: off." in review and "roast" not in review.split("Roast: off.")[1].lower()
    # The writer of each prose block hears that the roast is off, so its blurb holds no roast either.
    assert "Roast: off. Write no roast" in (writer.calls[0].system or "")
    assert "Roast: off. Write no roast" in (writer.calls[2].system or "")
    assert len(writer.calls) == 4


def test_with_the_roast_warm_the_roast_block_gets_the_roast_rules_and_the_soft_step(tmp_path):
    client = _with_roast(_cpc_week_8(tmp_path), tmp_path, "warm")
    writer = FakeWriter([STATE_BLURB, _passed(3), ROAST_BLURB, _passed(2), DRAFT_BLURB, _passed(2), DRAFT_ROAST,
                         _passed(2)])
    report = _report(run_midseason(2026, 8, partial(claude_call, writer=writer), client=client, provider=CPC_PROVIDER))
    assert len(_roasts(report)) == 2
    roast_system = writer.calls[2].system or ""
    assert "Never roast life outside fantasy" in roast_system and "Roast: warm." in roast_system
    assert "Roast:" not in (writer.calls[0].system or "")
