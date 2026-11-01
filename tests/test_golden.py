"""
Golden tests: a build over the week 6 fixtures must write the four saved files byte for byte.
Run `make golden` to rewrite the saved copies after a change on purpose.
"""
import difflib

import pytest

from golden import GOLDEN_DIR, GOLDEN_FILES, build_golden


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    # One build serves the four tests, because a build takes some seconds.
    return build_golden(tmp_path_factory.mktemp("golden"))


@pytest.mark.parametrize("name", GOLDEN_FILES)
def test_the_build_matches_the_golden_file(built, name):
    golden = GOLDEN_DIR / name
    assert golden.exists(), f"{golden} is missing. Run make golden."
    want = golden.read_text(encoding="utf-8")
    got = built[name].read_text(encoding="utf-8")
    if got != want:
        # The diff starts at the first changed line, so the reviewer sees what moved.
        diff = difflib.unified_diff(want.splitlines(), got.splitlines(), f"golden/{name}", f"built/{name}",
                                    lineterm="", n=2)
        pytest.fail(f"{name} differs from the golden copy:\n" + "\n".join(list(diff)[:60]))
