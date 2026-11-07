"""
Tests for the egg draft on a real temp egg file: the read of the dropped eggs, the write of six spots, and the repeat check.
The agent is a port, so each test gives the text that an agent answers. No spot is real.
"""
import json
from pathlib import Path

import pytest

from eggs.draft import DraftError, draft_prompt, draft_week
from eggs.eggfile import Spot, append_spots, read_spots

# T1 to T4 of the acceptance tests: four test eggs that dropped before week 8.
DROPPED = [Spot(week=7, page="/midseason/2026/", target=f"test-t{index}", action="tap2", reason=f"Test T{index}.",
                confirmed=True) for index in range(1, 5)]


def _answer(spots: list[dict]) -> str:
    # An agent may write a line of text around the JSON, so the answer holds one.
    return "Here are the six spots.\n```json\n" + json.dumps(spots) + "\n```\n"


def _six(start: int = 0) -> list[dict]:
    return [{"page": "/week/2026/8/", "target": f"test-new-{index}", "action": "tap2",
             "conditions": {"theme": "light"}, "reason": f"Test reason {index}."} for index in range(start, start + 6)]


def _file(tmp_path: Path) -> Path:
    path = tmp_path / "cpc-eggs" / "2026.toml"
    append_spots(path, DROPPED)
    return path


def test_the_draft_writes_six_spots_each_with_a_reason_and_marked_not_confirmed(tmp_path):
    path = _file(tmp_path)
    draft_week(path, 8, lambda prompt: _answer(_six()), prompt="the prompt")
    spots = [spot for spot in read_spots(path) if spot.week == 8]
    assert len(spots) == 6
    assert all(spot.reason and not spot.confirmed for spot in spots)
    assert spots[0].conditions == {"theme": "light"}
    # The spots that dropped before stay as they were.
    assert [spot for spot in read_spots(path) if spot.week == 7] == DROPPED


def test_the_draft_keeps_the_text_that_the_commissioner_wrote(tmp_path):
    path = _file(tmp_path)
    path.write_text("# The notes of the commissioner.\n" + path.read_text(encoding="utf-8"), encoding="utf-8")
    draft_week(path, 8, lambda prompt: _answer(_six()), prompt="the prompt")
    assert path.read_text(encoding="utf-8").startswith("# The notes of the commissioner.\n")


def test_a_draft_that_repeats_a_dropped_egg_writes_nothing(tmp_path):
    path = _file(tmp_path)
    before = path.read_text(encoding="utf-8")
    spots = _six()
    spots[2] = {**spots[2], "page": "/midseason/2026/", "target": "test-t3"}
    with pytest.raises(DraftError, match="test-t3"):
        draft_week(path, 8, lambda prompt: _answer(spots), prompt="the prompt")
    assert path.read_text(encoding="utf-8") == before


def test_a_draft_with_a_spot_that_has_no_reason_or_not_six_spots_writes_nothing(tmp_path):
    path = _file(tmp_path)
    no_reason = _six()
    no_reason[0] = {**no_reason[0], "reason": ""}
    with pytest.raises(DraftError, match="reason"):
        draft_week(path, 8, lambda prompt: _answer(no_reason), prompt="the prompt")
    with pytest.raises(DraftError, match="not 6"):
        draft_week(path, 8, lambda prompt: _answer(_six()[:5]), prompt="the prompt")
    assert [spot for spot in read_spots(path) if spot.week == 8] == []


@pytest.mark.parametrize("change", [{"action": "tap3"}, {"action": "hold1"}, {"conditions": {"trade": "1:2|3:4"}},
                                    {"conditions": {"trade_teams": [1]}}])
def test_a_draft_with_an_old_action_or_a_bad_condition_writes_nothing(tmp_path, change):
    path = _file(tmp_path)
    spots = _six()
    spots[2] = {**spots[2], **change}
    with pytest.raises(DraftError, match="test-new-2"):
        draft_week(path, 8, lambda prompt: _answer(spots), prompt="the prompt")
    assert [spot for spot in read_spots(path) if spot.week == 8] == []


def test_a_second_draft_of_one_week_writes_nothing(tmp_path):
    path = _file(tmp_path)
    draft_week(path, 8, lambda prompt: _answer(_six()), prompt="the prompt")
    with pytest.raises(DraftError, match="already holds"):
        draft_week(path, 8, lambda prompt: _answer(_six(10)), prompt="the prompt")


def test_the_prompt_names_the_catalog_the_notes_the_week_page_and_each_dropped_egg(tmp_path):
    path = _file(tmp_path)
    page = tmp_path / "build" / "week-08" / "page.json"
    prompt = draft_prompt(path, 8, page, size=6)
    assert "01-grill-egg-catalog.md" in prompt
    assert "01-grill-egg-catalog.notes.md" in prompt
    assert str(page) in prompt
    assert all(spot.target in prompt for spot in DROPPED)
