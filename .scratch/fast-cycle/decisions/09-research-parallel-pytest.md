# 09: Can the pipeline and API tests run under pytest-xdist

Map: `.scratch/fast-cycle/MAP.md`.

**Kind:** research

**Blocked by:** 04

**Status:** done

## Question

Decision 04 runs the pipeline tests in parallel. Some tests may share a file, a cache folder, a golden file, or a fixed port, and then fail at random under `pytest-xdist`. The spec needs to know which tests are safe, what to change, and the time on a CI runner of 4 cores. On local `main`, the 1579 pipeline tests take 4 min 40 s, and no single test dominates.

## Decision

The research decided it on 2026-11-06. The notes are `decisions/09-research-parallel-pytest.notes.md`.

Yes. The pipeline and API tests run under `pytest-xdist` with `-n auto`, and no test needs a fix.

1. Every run on a quiet tree passed, also in random order. No run left a file in the tree.
2. Pipeline, local with 10 cores: 275 s serial, 51 to 64 s with `-n auto`. API: 84 s serial, 15 to 31 s.
3. On CI with 4 cores, the estimate is about 3 min for the pipeline, down from 10 min 39 s, and about 25 s for the API. This is not a CI measurement yet.
4. `--dist loadfile` gave no gain, so the default `load` mode stays.
5. `pytest-xdist` becomes a dev dependency of each member, so the lock file holds it.

One runner hazard: two `uv run --exact --package` runs of different members in one checkout share one `.venv` and break each other. Run the members one after another in one checkout, or in separate CI jobs. Spec ticket 11 holds this.
