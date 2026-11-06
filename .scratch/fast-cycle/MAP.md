# Fast cycle: map

App: both.
Spec branch: `fast-cycle`.

## DESTINATION

A spec the size of `midseason-report` goes from the `cpc:implement` start to a green PR in half the time or less: build 2 h or less, review fixes 40 min or less, CI 10 min or less. Every check that runs today still runs, none gets weaker, the Judge replaces the Test verdict comment of Brian, and Brian still merges.

## DECISIONS SO FAR

- A check can move, run in parallel, or use a cache, but never disappears or gets weaker. CI runs every app. `decisions/01-grill-guardrail-rule.md`.
- The orchestrator resolves a merge conflict itself, then runs `make check-fast`. No send-back. `decisions/02-grill-merge-conflicts.md`.
- The review fixes run as parallel fix groups that share no file. `decisions/03-grill-review-fix-groups.md`.
- CI runs one job per app and package, plus a gate job named `check`. `decisions/04-grill-ci-jobs.md`.
- One background `make check` runs during the evidence stage, before the push. `decisions/05-grill-local-full-check.md`.
- The Judge gives each Test verdict from the evidence alone. One fix round, then BLOCKED and no PR. ADR 0026. `decisions/06-grill-judge.md`.
- "Test verdict" now means the Judge's word. The glossary adds **Judge**. `decisions/07-grill-test-verdict-term.md`.
- A FAIL from Brian in a PR comment overrides the Judge. `decisions/08-grill-brian-fail-override.md`.
- PR #13 keeps the old verdict rule. `fast-cycle` merges after PR #13. `decisions/13-grill-open-pr-rule.md`.
- The pipeline and API tests run under `pytest-xdist -n auto` with no test fix. The estimate on CI is about 3 min for the pipeline. `decisions/09-research-parallel-pytest.md`.
- The midseason tests add about 4 min from about 45 repeated builds. A shared session fixture per input cuts them, with the same assertions and the full sim count. `decisions/10-research-midseason-test-time.md`.
- The CI jobs, the Chromium cache, and the deploy triggers are in the spec. `decisions/11-spec-ci-jobs-and-cache.md`.
- The Judge writes `VERDICTS.md` with the blob SHAs it read, and `scripts/verdict.py` reads it and a FAIL of Brian. `decisions/12-spec-judge-record.md`.

## NOT YET SPECIFIED

None.

## OUT OF SCOPE

- A "Blocked by" edge for tickets that touch the same file. Brian chose the smaller change of decision 02 first.
- A review per ticket. It changes more and starts more subagents than decision 03.
- A CI run of only the changed apps. Decision 01 keeps the full check on CI.
