# 51: The research test gives its free agent a projection

Spec: `.scratch/front-door/PRD.md`. Source: CI run 43111521960 of PR #34, the pipeline job.

**App:** pipeline

**What to build:** `test_a_build_with_no_search_sends_the_research_through_the_writer` fails on `front-door` every time, in CI and locally. It passes on `main` (`1d7bfc0d`). The test is not flaky, and it does not depend on the clock, the network, or the order of the tests.

The cause is ticket 15 (`071b6021`). A player with a rest of season projection of 0 now lands in no add bucket. The test builds from `free_agent_raw_dir`, and no free agent of that fixture is in `projections_ahead.json`. So each free agent has a rest of season projection of 0, and every bucket of the waiver board is empty. `research_players` gets no player, the research makes no call, and `fake_writer.calls` is `[]`.

A probe on `research_players` shows the board of each side:

- `main`: `best_adds` is `['2505', '80001', '9225']`, and the research gets the same three players.
- `front-door`: every bucket is `[]`, and the research gets `[]`.

The rule of ticket 15 is correct, so the fix is in the test. The test builds from `_repo_with_free_agent`, which gives its free agent a projection ahead of 8.0. The shared fixture `free_agent_raw_dir` stays the same, because tests in `test_snapshot.py` and `test_live.py` use it.

**Blocked by:** none

**Status:** done

- [x] Red first: the test fails on `front-door` with `assert ([])`, the same failure as CI.
- [x] The test builds a repo whose free agent has a rest of season projection above 0, so the research sends one search through the writer.
- [x] `tests/test_pipeline.py` passes in full.

## Comments
- Closes with the squash merge of the spec PR.
