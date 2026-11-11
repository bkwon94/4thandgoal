# 01: The report's first build

Spec: `.scratch/midseason-report/PRD.md`. Acceptance tests AT-1, AT-4, AT-47, AT-48, and AT-49.

**App:** pipeline

**What to build:** Brian runs `make midseason CLIENT=cpc WEEK=8`, and the build folder of the season holds `midseason.json` with the state of the league: each team's full record, points for and against, the streak, and the playoff odds. The two packages `sim` and `midseason` exist, each with its README of Knows, Ports, and Does not do. A client that takes `midseason` without `sim` fails the config check.

**Blocked by:** none.

**Status:** done

- [x] `make midseason CLIENT=cpc WEEK=8` writes `midseason.json` to the build folder of the season and nothing to `published/`.
- [x] Points for is the sum of the weekly scores: Maye d'force B with U shows 900.65.
- [x] `test_layers.py` passes, and `midseason` and `sim` import only `league` and `facts`.
- [x] The config check fails a client with `midseason` and no `sim`, and names `sim`.
- [x] The weekly `make build CLIENT=cpc WEEK=8` does not change the report files.

## Comments
- Closed by the merge of PR #13.
