# 09: Notes on pytest-xdist for the pipeline and the API tests

Research notes for `09-research-parallel-pytest.md`. Measured on 2026-11-06 in the worktree `fast-cycle`, on a Mac with 10 cores (`sysctl -n hw.physicalcpu hw.logicalcpu` gives `10` and `10`), with `pytest-xdist` 3.8.0 from `--with`.

## Answer

Yes, with no test fix. Both suites pass under `pytest-xdist` in every run on a quiet tree, and no run leaves a file in the tree.

| Suite | Serial | `-n 4` | `-n auto` (10 workers) |
| --- | --- | --- | --- |
| Pipeline, 1579 tests | 275.48 s | 82.52 s, 69.67 s | 63.61 s, 57.39 s, 50.97 s (random order) |
| API, 163 tests | 83.91 s | 20.92 s, 20.46 s | 31.00 s, 15.30 s |

One rule for the runner, not for a test: do not run two `uv run --exact --package <member>` commands in one checkout at the same time. They share one `.venv`, and each one syncs it to its own member. Two of my runs failed for this cause, while another process ran in the same worktree. See "Runner hazard".

The CI estimate for `ubuntu-latest` with 4 cores: the pipeline goes from 10 min 39 s to about 2 min 45 s to 3 min 15 s, and the API from 1 min 43 s to about 25 s. This is the local speedup at `-n 4` (3.3x to 4.0x) applied to the CI times. It is an estimate, not a CI measurement.

## Runs

Each run is a command in `apps/pipeline` or `apps/api`. The script logged the wall time, the tail of the output, and `git status --porcelain` after each run.

| Run | Command | Result |
| --- | --- | --- |
| api_serial | `uv run --exact --package cpc-api pytest -q` | `163 passed in 83.91s` |
| api_auto1 | `uv run --exact --package cpc-api --with pytest-xdist pytest -q -n auto` | `163 passed in 31.00s` |
| api_auto2 | same | `163 passed in 15.30s` |
| api_n4 | same with `-n 4` | `9 passed, 1 error in 2.15s`, see "Runner hazard" |
| api_n4_re1 | same with `-n 4` | `163 passed in 20.92s` |
| api_n4_re2 | same with `-n 4` | `163 passed in 20.46s` |
| pipe_auto1 | `uv run --exact --package cornerstone --with pytest-xdist pytest -q -n auto` | `1435 passed, 3 errors in 46.85s`, see "Runner hazard" |
| pipe_auto2 | same | `1579 passed in 63.61s` |
| pipe_auto_re | same | `1579 passed in 57.39s` |
| pipe_n4a | same with `-n 4` | `1579 passed in 82.52s` |
| pipe_n4b | same with `-n 4` | `1579 passed in 69.67s` |
| pipe_n4_loadfile | same with `-n 4 --dist loadfile` | `1579 passed in 81.50s` |
| pipe_rand | `... --with pytest-xdist --with pytest-randomly pytest -q -n auto -p randomly` | `1579 passed in 50.97s` |
| pipe_serial | `uv run --exact --package cornerstone pytest -q` | `1579 passed, 8 deselected in 275.48s` |

The 8 deselected tests are the `live` tests (`apps/pipeline/pyproject.toml:52-54`, `addopts = "-m 'not live'"`). The xdist runs deselect them too; the xdist summary line does not print the count.

`pytest-randomly` is not a dependency, so the random run takes it with `--with`. The `-q` flag hides the header, so the log has no seed. The random run passed, so no test order dependence showed. A repeat with a printed seed needs no `-q`.

`--dist loadfile` was not faster than the default `--dist load` (81.50 s against 69.67 s to 82.52 s), so the default is enough.

## The tree after the runs

`git status --short` printed nothing after the last run. The `.status` files of the runs held only two lines, `M  .scratch/fast-cycle/MAP.md` and `M  .scratch/fast-cycle/decisions/13-grill-open-pr-rule.md`. Another process staged them, and commit `a8b9218f` at 11:24:22 took them. No test wrote them.

A `find . -newer <marker>` outside `.venv`, `.git`, `__pycache__`, `.pytest_cache`, and `node_modules` found only those two files and some ignored files under `apps/site/`, such as `apps/site/tsconfig.tsbuildinfo` at 11:24:24. Those come from the site part of the prek hook of commit `a8b9218f`, not from pytest. No file under `data/nfl/cache/`, `data/cache/`, `clients/`, or `tests/fixtures/golden/` changed.

## Shared state, one item at a time

No item below breaks under parallel workers. Each item gives the cause and the reason it is safe.

1. **Module fixtures.** `apps/pipeline/tests/conftest.py:213` (`week_8`), `test_golden.py:11` (`built`), `test_analysis.py:673`, `test_week_line.py:45,221,238`, and `test_adjuster_rows.py:193,201,287` have `scope="module"`. Each one writes only under `tmp_path_factory`. xdist gives each worker its own base temp folder: `option_dict["basetemp"] = str(basetemp / name)` (`xdist/workermanage.py:340-341`, pytest-xdist 3.8.0). So two workers never share a folder. The cost: under `--dist load`, a module fixture runs once on each worker that gets a test of the module. The measured times above already hold that cost.
2. **Links into the real client data.** `saved_repo` (`conftest.py:200-210`) links `raw/` and `history/` of a temp repo to the tracked `clients/cpc/data/2026/` (`SAVED`, `conftest.py:197`). A write through a link would change a tracked file. No run changed one, so today the build only reads them. The fixture also gave no conflict in the serial run, so this is not a new risk of xdist.
3. **Golden files.** `test_golden.py` only reads `tests/fixtures/golden/`. The write of the golden copies is in `golden.py:51-57`, and only `make golden` runs it, not pytest.
4. **git on the real repo.** `test_rule_tracker.py:12-16` and `:40-42` run `git rev-parse` and `git ls-files`. `test_rule_readmes.py:116-120` runs `git ls-files`. Each one only reads. The git calls of `test_pipeline.py:753-754` and `test_rule_publish.py:19-22` run in a repo under `tmp_path`.
5. **A uv call inside a test.** `test_cli.py:20` runs `uv run cornerstone --help`. A `uv run` with no `--exact` can install a package into the shared `.venv`, but it never removes one. It passed in every run. A proposal for a later ticket, not needed for xdist: run it with `--exact --package cornerstone`, so it can never change the env of the other workers.
6. **Env vars.** The tests set env vars only with `monkeypatch.setenv` and `monkeypatch.delenv`, such as `apps/api/tests/test_api.py:1010`, `:1024-1025`, `:1305-1316`, and `apps/pipeline/tests/test_rule_publish.py:53-54`. A grep for `os.environ[`, `os.environ.setdefault`, `putenv`, and `os.chdir` in both test folders found nothing. Each xdist worker is its own process, so a change of a global in one worker never reaches another.
7. **Ports.** No test opens a port. The only network code is `httpx.MockTransport` (`test_sleeper.py:64`, `test_cli.py:61`). The port strings in `test_api.py:1200` are origin values in a list.
8. **Order.** The random-order run passed, so no test order dependence showed.

## Runner hazard

`api_n4` and `pipe_auto1` failed with `ModuleNotFoundError: No module named 'fastapi'` at the import of `tests/test_api.py`, `tests/test_adjuster_rows.py`, `tests/test_analysis.py`, and `tests/test_week_line.py`. Both members need `fastapi`, through `cpc-analyzer` (`packages/analyzer/python/pyproject.toml:14`, `apps/pipeline/pyproject.toml:11`). So the env lost `fastapi` for a short time.

The logs show the env change between runs: `Installed 8 packages`, `Uninstalled 3 packages`, `Uninstalled 1 package` on the first line of each log. Another process ran in the same worktree at that time: commit `a8b9218f` at 11:24:22 ran the prek hook, which runs `uv run --exact --package` for the pipeline and for the API. The same commands passed on the next run, on a quiet tree.

This is not an xdist cause, and a serial run has the same risk. It matters for the CI design. The fix: run the pipeline tests and the API tests one after the other in one job, or in two jobs on two runners. Do not run them at the same time in one checkout.

## Proposed fixes

None of the 1742 tests needs a fix. No proposal skips a test, weakens an assertion, or adds `xfail`, per `01-grill-guardrail-rule.md`, point 2.

1. Add `pytest-xdist` to the `dev` group of `apps/pipeline/pyproject.toml` and of `apps/api/pyproject.toml`.
2. Run `pytest -q -n auto` in `make test` of each app. On a Linux runner without `psutil`, `-n auto` falls back to `os.sched_getaffinity`, so it uses the 4 CPUs of the runner (`xdist/plugin.py:25-40`).
3. Keep the default `--dist load`.
4. Optional: change `test_cli.py:20` to `uv run --exact --package cornerstone cornerstone --help`, as in item 5.

## Sources

- pytest-xdist distribution modes, `load`, `loadfile`, `loadscope`, `worksteal`, and "With -n auto, pytest-xdist will use as many processes as your computer has physical CPU cores": https://pytest-xdist.readthedocs.io/en/stable/distribution.html
- pytest-xdist how-to: a session fixture runs once in each worker, "will execute the fixture code more than once"; the `worker_id` fixture; `PYTEST_XDIST_WORKER`; `tmp_path_factory.getbasetemp().parent` is the folder that all workers share: https://pytest-xdist.readthedocs.io/en/stable/how-to.html
- pytest-xdist 3.8.0 source, a base temp folder per worker: `xdist/workermanage.py:340-341`. The CPU count with and without `psutil`: `xdist/plugin.py:25-40`.
- GitHub-hosted runners: `ubuntu-latest` has 4 CPU cores and 16 GB of RAM on a public repo, and 2 cores and 8 GB on a private repo: https://docs.github.com/en/actions/reference/runners/github-hosted-runners
