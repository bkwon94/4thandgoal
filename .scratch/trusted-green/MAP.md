# Trusted green: map

App: both.
Spec branch: `trusted-green`.

## DESTINATION

Spec 1, "the loop": each PR that changes code carries checks strong enough that Brian merges a green PR with no second look at the diff. It adds a `verify` skill and its smoke run, a CI re-run of the Red and Green commands, a rule for each flaky test, grade-bar in CI, property tests of the grades, and a differential rebuild of a published week.

The ideas come from "How the Claude Code team thinks about verification" (https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/).

## DECISIONS SO FAR

- This map ends in spec 1, "the loop". Spec 2, "the record", gets its own map after spec 1 merges. `decisions/01-grill-destination-and-seams.md`.
- Verification follows the diff, not the flow: each PR that changes code gets it. A PR of records only gets the plain `Check`. `decisions/01-grill-destination-and-seams.md`.
- The terms Smoke run and Flaky test are in `GLOSSARY.md`. The skill keeps the name `verify` as a Technical Name. `decisions/01-grill-destination-and-seams.md`.
- One `verify` skill at `.claude/skills/verify/` boots the site and the API, with one section per app. `decisions/01-grill-destination-and-seams.md`.
- `4ag:implement` and `4ag:quick` run one smoke run before the Judge. Its screenshots and log go to the Judge as evidence. `decisions/01-grill-destination-and-seams.md`.
- A CI job reads its script from `main`, checks out the red commit and the fix commit, and runs the command of each Red and Green block. `decisions/01-grill-destination-and-seams.md`.
- A CI job rebuilds the latest published week of each client with `build --no-fetch` and diffs it against `clients/<slug>/published/`. `decisions/01-grill-destination-and-seams.md`.
- Hypothesis property tests cover the grades, in the pipeline only. `decisions/01-grill-destination-and-seams.md`.
- `AGENTS.md` holds the rule for a flaky test, and a rule test fails on each retry setting. `decisions/01-grill-destination-and-seams.md`.
- CI runs `check:grade-bar`. It needs no live API, because the test answers each API call with `route.fulfill`. `decisions/01-grill-destination-and-seams.md`.

## NOT YET SPECIFIED

- Does Codex find a skill at `.claude/skills/verify/`, as Claude Code does? `decisions/02-research-codex-repo-skill.md`.
- Does a rebuild with `--no-fetch` give the published files byte for byte, and how long does it take? `decisions/03-research-rebuild-matches-published.md`.
- What does a smoke run drive for a given diff, and does it reuse the evidence runner? `decisions/04-grill-what-smoke-run-drives.md`.
- What shape has the list of approved diffs of the rebuild? `decisions/05-spec-approved-diff-list.md`.
- Which pure functions get property tests, and which properties? `decisions/06-spec-property-test-targets.md`.
- How does the re-run job find the quick file, its commands, and its commits? `decisions/07-spec-red-green-rerun-job.md`.

## OUT OF SCOPE

- Spec 2, "the record": the Proof trailer and its gate with off, observe, and enforce modes, the reliability checklist with triggers read from the diff, and the score of the Judge from a replay of past FAIL items. Spec 2 learns from the misses of spec 1, and its own map starts after spec 1 merges.
- A measure of the rate of fix PRs after a merge. Brian chose no measure. The spec is done when each part ships.
- The weekly `publish`. It pushes to `main` with no PR. The differential rebuild still guards the pipeline code behind it.
- The flaky AT-5 wait-dips test in `analyzer-stage.spec.ts:324`. It goes to its own quick run, so this spec does not wait on it.
