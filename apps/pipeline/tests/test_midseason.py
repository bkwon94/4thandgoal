"""
Tests for the build of the midseason report: make midseason writes midseason.json into the build folder of the season,
from the real saved CPC data of 2026. test_pipeline.py checks that the weekly build never touches it.
"""
import json
import shutil
from pathlib import Path

import pytest
from cpc import ROOT, cpc_client

from cornerstone.pipeline import BuildStopped, run_midseason
from league.paths import build_dir, client_dir, history_root, week_dir

# The real saved data of CPC 2026. The tests copy it, so no test writes under clients/.
CPC_DATA = client_dir(ROOT, "cpc") / "data" / "2026"


def _cpc_week_8(tmp_path: Path):
    """A CPC client folder in `tmp_path` with the saved history and the week 8 facts of the real CPC data."""
    client = cpc_client(at=tmp_path)
    shutil.copytree(CPC_DATA / "history", history_root(client.folder, 2026))
    week_dir(client.folder, 2026, 8).mkdir(parents=True)
    shutil.copy(CPC_DATA / "week-08" / "facts.json", week_dir(client.folder, 2026, 8) / "facts.json")
    return client


def _report(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _state_rows(report: dict) -> dict[str, dict]:
    act = next(act for act in report["acts"] if act["key"] == "how-we-got-here")
    chapter = next(chapter for chapter in act["chapters"] if chapter["key"] == "state")
    return {row["name"]: row for row in chapter["facts"]["teams"]}


def test_the_build_writes_midseason_json_to_the_build_folder_of_the_season_and_nothing_to_published(tmp_path):
    # AT-1: the report goes live only through its own publish.
    client = _cpc_week_8(tmp_path)
    out = run_midseason(2026, 8, client=client)
    assert out == build_dir(client.folder) / "2026" / "midseason.json"
    report = _report(out)
    assert (report["schema_version"], report["season"], report["week"], report["takeover_end_week"]) == (1, 2026, 8, 9)
    assert [act["key"] for act in report["acts"]] == ["how-we-got-here"]
    assert not (client.folder / "published").exists()


def test_points_for_is_the_sum_of_the_weekly_scores(tmp_path):
    # AT-4: Sleeper says 901.65 after a stat correction. The standings sum says 900.65.
    rows = _state_rows(_report(run_midseason(2026, 8, client=_cpc_week_8(tmp_path))))
    assert rows["Maye d'force B with U"]["points_for"] == 900.65
    assert (rows["All You Need Is Love"]["wins"], rows["All You Need Is Love"]["losses"]) == (11, 5)
    assert rows["All You Need Is Love"]["rank"] == 1


def test_each_row_has_the_playoff_odds_of_the_week(tmp_path):
    client = _cpc_week_8(tmp_path)
    saved = json.loads((CPC_DATA / "week-08" / "facts.json").read_text(encoding="utf-8"))["odds"]["teams"]
    rows = _state_rows(_report(run_midseason(2026, 8, client=client)))
    assert len(rows) == 12
    assert {row["roster_id"]: row["playoff_odds"] for row in rows.values()} == {
        int(rid): odds["playoff"] for rid, odds in saved.items()}


def test_a_rerun_gives_the_same_file(tmp_path):
    client = _cpc_week_8(tmp_path)
    first = run_midseason(2026, 8, client=client).read_bytes()
    assert run_midseason(2026, 8, client=client).read_bytes() == first


def test_a_gap_in_the_history_stops_the_build_with_the_command_that_fills_it(tmp_path):
    client = _cpc_week_8(tmp_path)
    shutil.rmtree(history_root(client.folder, 2026) / "week-05")
    with pytest.raises(BuildStopped, match="cornerstone history --through 8"):
        run_midseason(2026, 8, client=client)
    assert not (build_dir(client.folder) / "2026" / "midseason.json").exists()


def test_a_week_with_no_saved_facts_stops_the_build_with_the_command_that_builds_it(tmp_path):
    client = _cpc_week_8(tmp_path)
    (week_dir(client.folder, 2026, 8) / "facts.json").unlink()
    with pytest.raises(BuildStopped, match="make build CLIENT=cpc WEEK=8"):
        run_midseason(2026, 8, client=client)

