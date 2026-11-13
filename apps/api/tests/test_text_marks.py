"""
Checks that plain_text() gives the plain letters of each sample text of the shared fixture text-marks.json.
The site test text-block.test.tsx reads the same file, so a drift between the two parsers fails a test.
"""
import json
from pathlib import Path

import pytest

from cornerstone_api.free_wording import plain_text

CASES = json.loads((Path(__file__).parent / "fixtures" / "text-marks.json").read_text())


@pytest.mark.parametrize("case", CASES, ids=[case["name"] for case in CASES])
def test_plain_text_matches_the_fixture(case: dict) -> None:
    assert plain_text(case["text"]) == case["plain"]
