"""One planted failed test for AT-3 of fast-cycle, on a throwaway branch that never merges.
The CI job api must fail on it, and the gate job check must fail with it."""


def test_the_planted_failure():
    count = len([1])
    assert count == 2
