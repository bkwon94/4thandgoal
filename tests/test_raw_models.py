"""
The contract test of the raw Sleeper models: every recorded raw file loads through its model.
A dump of the loaded model equals the file, so the models drop no field that Sleeper sends.
"""
import json
from pathlib import Path

import pytest
from cornerstone.sleeper import RawPastWeek, RawTrending, RawWeek, load_raw


def _same(dumped, data) -> bool:
    """True when the dump and the file have the same JSON text.

    Plain == takes 0 and 0.0 as equal, so it hides a change from an int to a float.
    """
    return json.dumps(dumped, sort_keys=True) == json.dumps(data, sort_keys=True)

HISTORY_WEEKS = sorted((Path(__file__).parent / "fixtures" / "2026" / "history").glob("week-*"))


def test_every_raw_file_is_a_field_of_the_raw_week(fixture_raw_dir):
    assert {p.stem for p in fixture_raw_dir.glob("*.json")} <= set(RawWeek.model_fields)


def test_every_raw_file_round_trips(fixture_raw_dir):
    raw = load_raw(fixture_raw_dir)
    for path in sorted(fixture_raw_dir.glob("*.json")):
        assert _same(raw.file_json(path.stem), json.loads(path.read_text(encoding="utf-8"))), path.name


def test_the_raw_week_dump_equals_the_files(fixture_raw_dir):
    # A file that does not exist, such as trending.json here, adds no key to the dump.
    files = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in fixture_raw_dir.glob("*.json")}
    assert _same(load_raw(fixture_raw_dir).model_dump(mode="json", exclude_unset=True), files)


@pytest.mark.parametrize("directory", HISTORY_WEEKS, ids=lambda d: d.name)
def test_every_history_file_round_trips(directory):
    files = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in directory.glob("*.json")}
    week = RawPastWeek.model_validate(files)
    for name, data in files.items():
        assert _same(week.file_json(name), data), f"{directory.name}/{name}.json"


def test_a_trending_row_round_trips():
    # The recorded week has no trending file, so one row in the Sleeper shape stands in.
    row = {"player_id": "11635", "count": 4210}
    assert _same(RawTrending.model_validate(row).model_dump(), row)
