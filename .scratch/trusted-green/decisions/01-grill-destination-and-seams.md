# 01: The destination and the seams

Map: `.scratch/trusted-green/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

Which spec does this map end in, which PRs does it cover, and which seams move?

## Decision

Brian decided each item in two grill rounds on 2026-11-18.

1. **Destination.** This map ends in spec 1, "the loop". Spec 2, "the record", holds the Proof trailer and its gate, the reliability checklist, and the score of the Judge. It gets its own map after spec 1 merges, because it learns from the misses of spec 1.
2. **Measure.** None. Brian chose no rate of fix PRs. The spec is done when each part ships.
3. **Scope.** Verification follows the diff, not the flow. Each PR that changes code gets it, whatever skill opened it. A PR of records only, such as `.scratch/` or `docs/`, gets the plain `Check`. The weekly `publish` has no PR, so it is out.
4. **App.** `both`. The API counts with the pipeline, because it imports the pipeline.
5. **Terms.** The skill keeps the name `verify` as a Technical Name, so Claude finds it as the article describes. `GLOSSARY.md` gets Smoke run and Flaky test. The Proof trailer waits for the map of spec 2.
6. **Slug.** `trusted-green`.
7. **Where `verify` lives.** One skill at `.claude/skills/verify/`, with one section per app. The flow of the analyzer needs the site and the API up at the same time. Ticket 02 checks Codex.
8. **When the smoke run happens.** `4ag:implement` and `4ag:quick` run it once, after the last build step and before the Judge. Its screenshots and log go to the Judge as evidence. It is too slow for the commit hook.
9. **The Red and Green re-run.** A CI job reads its script from `main`, like `verdict.yml`. It checks out the red commit and the fix commit and runs the command of the quick file on each. The builder then cannot fake a Red or Green block, and a change cannot edit the check that judges it. Ticket 07 sets the details.
10. **The differential rebuild.** A CI job runs on each PR that changes the pipeline, the API, or a package. It rebuilds the latest published week of each client with `build --no-fetch` and diffs it against `clients/<slug>/published/`. A change of output on purpose needs a list of approved diffs. Tickets 03 and 05 set the details.
11. **Property tests.** Hypothesis, in the pipeline only. Ticket 06 picks the functions.
12. **The flaky-test rule.** The rule goes in `AGENTS.md`. A rule test fails on each retry setting: `retries` in a Playwright config, `pytest-rerunfailures`, or `retry` in a Vitest config. The AT-5 wait-dips flake goes to its own quick run.
13. **grade-bar in CI.** CI runs `check:grade-bar`. It needs no live API, because `apps/site/e2e/grade-bar.spec.ts:44` answers each API call with `route.fulfill`.

An ADR may be due at spec time for item 3, the rule that verification follows the diff. `4ag:to-spec` decides.
