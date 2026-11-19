# 02: A set result in the sim package

Spec: `.scratch/season-sim/PRD.md`. Acceptance tests AT-11, AT-12, and AT-13. Decisions 01, 03, and 07.

**App:** pipeline

**What to build:** The sim takes a list of set results of Your team: for each week, a win or a loss, and above or below the median. In a league with no median game, a set result is a win or a loss. In a playoff week, a set result holds a bracket game whose two teams are set. The sim holds each set result with the "Your score first" draw with a weight of decision 07, and returns `effective_runs`. The same inputs and set results give the same output, by the fixed seed. The level of a team does not change for an injury.

**Blocked by:** 01.

**Status:** done

- [x] On the inputs of `cpc` 2026 week 10, Bo Girds set to lose week 11 and miss the median gives playoff odds within 1.5 points of an exact rejection reference (AT-11).
- [x] Two runs with the same set results give equal output, byte for byte (AT-12).
- [x] The level mean of each team is its season average shrunk with 5 weeks of weight, with no injury term (AT-13).
- [x] A set result in a league with no median game and a set bracket game each have a test.
- [x] The sim returns `effective_runs`, and a run with no set result has `effective_runs` equal to `runs`.
- [x] `make check-fast` passes.

## Comments

Closes with the squash merge of the spec PR: `season-sim-02` (`658f36c9`) merged into `season-sim` as `a69dbbe3` on 2026-11-18.
AT-11, AT-12, and AT-13 have PASS in `.scratch/season-sim/VERDICTS.md`.
The builder did not count the files it read; the ticket commits changed 6 files: apps/pipeline/src/cornerstone/season_sim.py, apps/pipeline/tests/test_sim.py, packages/sim/python/src/sim/published.py, packages/sim/python/src/sim/season.py, packages/sim/python/tests/rejection.py, packages/sim/python/tests/test_season.py.
