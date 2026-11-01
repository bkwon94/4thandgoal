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
    return build_golden(tmp_path_factory.mktemp("golden"), tmp_path_factory.mktemp("nflverse"))


@pytest.mark.parametrize("name", GOLDEN_FILES)
def test_the_build_matches_the_golden_file(built, name):
    golden = GOLDEN_DIR / name
    assert golden.exists(), f"{golden} is missing. Run make golden."
    want = golden.read_bytes()
    got = built[name].read_bytes()
    # The check compares bytes, because a text read hides a change of line ends.
    if got != want:
        # The diff starts at the first changed line, so the reviewer sees what moved.
        diff = difflib.unified_diff(want.decode("utf-8", "replace").splitlines(keepends=True),
                                    got.decode("utf-8", "replace").splitlines(keepends=True),
                                    f"golden/{name}", f"built/{name}", n=2)
        pytest.fail(f"{name} differs from the golden copy:\n" + "".join(list(diff)[:60]))
