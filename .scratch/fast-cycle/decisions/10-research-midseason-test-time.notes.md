# Notes for decision 10: the test time of midseason-report

Research of 2026-11-06. The branch is `origin/midseason-report` at `6a5906f8`. The base is `origin/main` at `197fb328`.

## Answer

1. The gap on the same hardware is about 4 min, not 6 min. The "6 min" compares a CI run of the branch with a local run of `main`.
2. Measured on this Mac, back to back: `main` takes 5 min 13 s. The branch takes 9 min 9 s. The gap is 3 min 56 s.
3. Measured on CI: `main` takes 6 min 29 s. The branch takes 10 min 39 s. The gap is 4 min 10 s.
4. So about 2 min of the "6 min" is the slower runner and the old local baseline. About 4 min is the new tests.
5. The sim is not the main cost. One build of the report takes 2.2 s at 500 runs and 2.9 s at 10,000 runs. The 500-run commit `bd82f229` gave no clear CI gain: 11 min 9 s before, 11 min 40 s and 10 min 39 s after.
6. The main cost is repeated builds. The new tests run about 45 full builds of the same report. Each test builds the report into its own `tmp_path`, though most tests only read it.
7. A shared build fixture per input cuts about 40 builds. The estimate is about 2 min 15 s of the 4 min, on the local machine. No assertion changes. This fits rule 1 of decision 01: a cache.

## The times

### Wall time of the pipeline tests

| Run | Where | Tests | Time | Source |
| --- | --- | --- | --- | --- |
| `main` `197fb328` | this Mac | 1579 | 312.78 s (5:12) | `pytest -q --durations=0 --durations-min=0.5` in a throwaway worktree, `local-main.txt` |
| branch `6a5906f8` | this Mac | 1667 | 549.19 s (9:09) | the same command, `local-msr.txt` |
| `main` `197fb328` | CI | 1579 | 388.87 s (6:28) | run 42155519449, job log line 1525 |
| `main` `0a8b8868` | CI | 1579 | 393.98 s (6:33) | run 42131877752, line 1507 |
| `main` `120bc901` | CI | 1579 | 409.56 s (6:49) | run 42110036052, line 881 |
| branch `729ff41d` | CI | 1667 | 693.85 s (11:33), 1 failed | run 42165118435 |
| branch `7f3050c3` | CI | 1667 | 669.43 s (11:09) | run 42167231305, cancelled after pytest |
| branch `bd82f229` (500 runs) | CI | 1667 | 700.80 s (11:40) | run 42222362978, line 1809 |
| branch `6a5906f8` | CI | 1667 | 639.37 s (10:39) | run 42237684234, line 1796 |

Get a job log with `gh api repos/{owner}/{repo}/actions/jobs/<job id>/logs`. `gh run view <id> --log` gave empty output for the runs of `main`.

The CI runner is about 1.2 times slower than this Mac on the whole suite: 389 s over 313 s for `main`, 639 s over 549 s for the branch. The 4 min 40 s for local `main` in the ticket is an older figure. Today the same machine gave 5 min 13 s.

### The CI runner and the new tests

The CI log of run 42237684234 prints a timestamp for each line of 72 dots. Tests 505 to 576 in the collection order took 169 s on CI, from `15:06:32` to `15:09:21`. Those tests are the 30 tests of `test_midseason.py`, then `test_midseason_draft.py`, `test_midseason_moves.py`, `test_midseason_norcal.py`, and 2 tests of `test_midseason_prose.py`. Source: `pytest --collect-only -q` on the branch, indices 500 to 580.

The same files took about 171 s on this Mac, from the sum of the durations. So the CI runner is about as fast as this Mac on the build tests. The slower runner costs time in the old tests, not in the new ones.

### Per file, this Mac

The sums count only the durations of 0.5 s or more. Source: `local-main-dur.txt` and `local-msr-dur.txt`.

| File | `main` | branch | Gap |
| --- | --- | --- | --- |
| `tests/test_midseason.py` | new | 130.4 s | 130.4 s |
| `tests/test_midseason_publish.py` | new | 23.7 s | 23.7 s |
| `tests/test_midseason_draft.py` | new | 20.6 s | 20.6 s |
| `tests/test_sim.py` | new | 10.4 s | 10.4 s |
| `tests/test_cli.py` | 1.1 s | 10.3 s | 9.2 s |
| `tests/test_midseason_prose.py` | new | 8.9 s | 8.9 s |
| `tests/test_midseason_moves.py` | new | 7.1 s | 7.1 s |
| `tests/test_midseason_norcal.py` | new | 6.0 s | 6.0 s |
| `tests/test_history.py` | under 0.5 s each | 12.1 s | 12.1 s |
| `tests/test_live.py` | 5.8 s | 16.3 s | 10.5 s |

The new tests hold about 215 s of the 236 s local gap. `test_history.py` and `test_live.py` did not change on the branch, but each test ran about twice as slow. The cause is not clear. The likely cause is load on this Mac from other work at the time of the branch run. Treat those 20 s as noise until a second run shows them.

### The slowest tests of the branch, this Mac

| Time | Test |
| --- | --- |
| 8.18 s | `test_cli.py::test_the_midseason_command_writes_the_report_to_the_build_folder` |
| 8.13 s | `test_midseason.py::test_a_rerun_gives_the_same_file` |
| 7.21 s | `test_midseason.py::test_with_the_roast_off_the_draft_has_no_roast_lines` |
| 6.52 s | setup of `test_midseason_prose.py` (module fixture `built`) |
| 6.04 s | setup of `test_midseason_norcal.py` (module fixture `norcal_build`) |
| 5.91 s | `test_midseason.py::test_the_record_book_high_is_maye_in_week_5_and_the_closest_game_is_0_4_in_week_3` |
| 5.75 s | `test_midseason.py::test_act_one_holds_the_state_then_the_arcs_then_schedule_luck` |
| 5.74 s | `test_midseason.py::test_the_report_tile_shows_the_title_odds_of_the_title_favorite` |
| 5.50 s | `test_midseason.py::test_a_clean_build_keeps_the_blurb_of_the_writer_for_each_chapter` |
| 4.88 s | `test_midseason_publish.py::test_a_clean_publish_commits_midseason_json_and_sim_json_and_no_other_path` |

Most other tests of `test_midseason.py` take 3.4 s to 5.3 s each. The full list is in `local-msr-dur.txt`.

## Where the time of one build goes

A throwaway script ran `build_week_8` of `tests/test_midseason.py:69` outside pytest, with `cProfile`. Output:

```
runs=500 copy=0.03s build=2.16s
runs=10000 copy=0.03s build=2.93s
runs=500 copy=0.03s build=2.14s
runs=10000 copy=0.05s build=2.96s
```

The profile of one build at 500 runs, by cumulative time:

| Time | Function |
| --- | --- |
| 2.44 s | `pipeline.py:766(run_midseason)` |
| 0.84 s | `json.loads`, 138 calls |
| 0.90 s | pydantic `validate_python`, 31,186 calls, of which 0.83 s is 80 calls of `model_validate` |
| 0.83 s | `league/provider/sleeper.py:320(load_raw)`, 4 calls |
| 0.44 s | `history.py:80(load_saved_weeks)` |
| 0.42 s | `pipeline.py:750(season_transactions)`, through `fakes.py:110(fetch_past_leg)`, 8 calls |
| 0.24 s | `fakes.py:103(fetch_live)` |
| 0.12 s | `sim/season.py:86(season_sim)` |

So about 75 percent of a build is the parse and the validation of the same saved JSON files. The sim is about 5 percent at 500 runs. At 10,000 runs the sim adds about 0.8 s to a build. A build makes no network call. No test holds a sleep.

## Each slow group, its cause, and its fix

### 1. One default build per test in `test_midseason.py` and `test_midseason_draft.py`

Cause: each test calls `build_week_8(_call(), client=_cpc_week_8(tmp_path), provider=CPC_PROVIDER)` with the default 500 runs. The inputs are the same each time. The helpers `_cpc_report` at `tests/test_midseason.py:510` and `_cpc_draft` at `tests/test_midseason_draft.py:48` build again on each call.

The tests with this same input:

- `tests/test_midseason.py` lines 263, 273, 395, 403, 418, 438, 459, 479, 608, and 639.
- The 8 users of `_cpc_report`: lines 516, 529, 538, 548, 571, 580, 589, and 601.
- `tests/test_midseason_draft.py` lines 54, 64, 72, 79, and 86 through `_cpc_draft`, and lines 118 and 125.
- `tests/test_midseason_moves.py` line 98.

That is 26 builds. Each test only reads the build folder or the report after the build.

Fix: one session fixture builds this report once into a folder from `tmp_path_factory`. Each test reads that folder. A test that changes a file gets a `shutil.copytree` of the folder. A copy takes 0.03 s. `tests/test_sim.py:62` and `tests/test_midseason_moves.py:15` already use this pattern at module scope.

Assertion: the same. Each test asserts on the same output of the same inputs. The build is pure for one input: `test_a_rerun_gives_the_same_file` at `tests/test_midseason.py:292` and `test_two_builds_give_the_same_sim_json_byte_for_byte` at `tests/test_sim.py:87` prove that.

Gain: about 26 builds of 3 s to 4 s in pytest. About 90 s on this Mac.

### 2. One clean build at the full count per test

Cause: these tests build with `_clean_call()` and `sim_runs=SIM_RUNS`, the 10,000 runs of `packages/sim/python/src/sim/tunables.py:6`. The comment at `tests/test_midseason.py:31-33` says why: the writer answers of the opener cite the title odds of the full count.

- `tests/test_midseason.py` lines 317, 348, 497, and 555.
- `tests/test_midseason_moves.py:19`, the module fixture `moves`.
- `tests/test_midseason_publish.py:50`, in `_drafted_repo` at line 39. Each of the 6 publish tests builds again.

That is 11 builds.

Fix: one session fixture holds one clean build at the full count. Each publish test copies it into its own git repo, because a publish changes the folder.

Assertion: the same. The count of runs stays 10,000, so each cited number stays the same.

Gain: about 10 builds of about 4 s. About 45 s on this Mac.

### 3. The full count with the default writer

Cause: `tests/test_midseason.py:283` and `tests/test_midseason.py:564` each build with `_call()` and `SIM_RUNS`.

Fix: one shared build for the two tests.

Assertion: the same. Gain: one build, about 4 s.

### 4. Builds that must stay

These builds have inputs of their own or test the build itself. Keep each one.

- `test_a_rerun_gives_the_same_file` at `tests/test_midseason.py:292` needs a second build. It can take its first build from fixture 1 as a copy, then build once. That saves one build.
- `test_a_gap_in_the_history_...` at line 298 and `test_a_week_with_no_saved_facts_...` at line 306 change the input first. Each stops early.
- The two roast tests at lines 360 and 377 change `client.toml`. The roast test at line 333 uses its own writer.
- `test_sim.py` builds twice at the full count: the fixture at line 62 and the second build at line 91. AT-37 asserts `runs == 10_000` at line 75, so the count must stay.
- `test_midseason_norcal.py:18` and `test_midseason_prose.py:21` already build once per module.
- `test_cli.py:708` runs the `midseason` command once, at the full count. It is the one test of the CLI path.

### 5. The sim count

A smaller sample gains little. At most about 13 builds run at 10,000 runs. Each costs about 0.8 s more than at 500 runs, so the total is about 10 s.

Three tests need the full count, and their assertions do not hold at 500 runs:

- `tests/test_midseason.py:279` asserts each playoff odds number within 2 points of the saved weekly odds. At 500 runs the sample error near 50 percent is about 4.4 points at 95 percent.
- `tests/test_midseason.py:562` asserts the exact tile value `16.8%`. A 500-run sim gives a different number, so the literal would change. That is a new expected value, not the same assertion. Brian must decide if that counts as the same under rule 6.
- `tests/test_sim.py:70` asserts `runs == 10_000`.

Recommendation: keep the full count. Share the builds instead.

### 6. A cache of the parse of the saved JSON, optional

Cause: each build parses and validates the same raw week and history files. `FixtureProvider.fetch_live` at `tests/fakes.py:103` and `fetch_past_leg` at `tests/fakes.py:110` read and parse them on each call.

Fix: the fake provider keeps the parsed result of each file for the session. This is test code only.

Assertion: the same. Gain: about 0.6 s per build. After fixes 1 to 3 only about 15 builds remain, so this saves about 10 s. Do it only if fixes 1 to 3 are not enough.

### 7. Parallel tests, for a later decision

`pytest-xdist` is not in `uv.lock`. A run with `-n 4` on the 4 cores of a CI runner splits the whole suite, old tests too. It is a move to parallel under rule 1. It needs a check that no two tests write to the same path. That fits the other decisions of the map better than this one.

## Expected result

After fixes 1 to 3, the new tests cost about 1 min 45 s on this Mac instead of about 4 min. On CI the branch run drops from about 10 min 39 s to about 8 min 15 s. No test disappears. No assertion changes. The count of sim runs stays the same for each test that reads a number of the full count.

## Sources

- Commands ran in a throwaway worktree of `origin/midseason-report` at `6a5906f8`, and of `origin/main` at `197fb328`, under the scratchpad of the session. Both are removed.
- The pipeline command: `uv run --exact --package cornerstone pytest -q --durations=0 --durations-min=0.5 -p no:cacheprovider` in `apps/pipeline`.
- The diff: `git diff --name-status origin/main...origin/midseason-report -- apps/pipeline/tests`. The new test files are `test_midseason.py`, `test_midseason_draft.py`, `test_midseason_moves.py`, `test_midseason_norcal.py`, `test_midseason_prose.py`, `test_midseason_publish.py`, and `test_sim.py`.
- CI runs: `gh run list --workflow check.yml --branch midseason-report` and `--branch main`. The job logs came from `gh api repos/{owner}/{repo}/actions/jobs/<job id>/logs`.
- CI pytest runs with `-q` and no `--durations`, so the CI log has no time per test. The block times come from the timestamps of the dot lines.
