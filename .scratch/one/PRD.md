# One: the site and the pipeline become one repo with the One flow

Status: ready-for-agent
Date: 2026-11-03
Repos: the site `cpcfantasyfootball` is the home. The pipeline `cornerstone-fantasy-sleeper-weekly-report` moves in.
Source: the grill session of 2026-11-03. ADRs 0007 to 0010. One's records on `~/repos/zero` branch `one`: `docs/VISION.md`, `.agents/delivery.md`, ADR-0014.
Tickets: 01 to 10, in `issues/`.

## Problem Statement

Brian: "Be like One." In One, an idea goes to a map, the fog clears through research or a grill, specs come out, and each spec is its own branch. The tickets merge into the spec branch, and the spec branch merges to main after its own review.

Our two repos follow part of One. Five gaps remain.

1. Two repos carry one product. Nine features sit in both trackers, with two PRDs and two ticket series. Cross-repo blockers are plain text.
2. Nothing checks the published shape across the two repos. The pipeline models and the site schemas describe it twice.
3. `publish` pushes to a second repo by a hard-coded path.
4. No skill knows our flow. Both `.claude/` folders are empty. Every skill comes from the global config and knows nothing about our tracker or our check.
5. Each ticket merges straight to `main`. No spec branch exists, and no acceptance test decides a merge.

## Solution

1. **One repo** (ADR 0007). The site moves to `apps/site/`. The pipeline moves to `apps/pipeline/` with its full history. The pipeline repo is archived read-only. The trackers, the ADRs, and the glossaries merge at the root, and the ADRs get one series.
2. **One check.** A root `make check` and `make check-fast` run the site, then the pipeline. A diff option runs only the apps with changed files. One prek hook runs the fast check. One CI file runs the full check on each push and each PR.
3. **`main` is the record branch** (ADR 0008). Work lands through a spec branch and one squash PR. `publish` is the one exception. It may push to `main`, but a check fails it if it stages a file outside the site's published data.
4. **Verdicts decide a merge** (ADR 0009). Brian gives PASS, FAIL, or BLOCKED for each acceptance test in one PR comment. A check blocks the merge until every test has PASS.
5. **The plugin `cpc`** holds six skills that know our repo: `plan`, `to-spec`, `to-acceptance`, `to-tickets`, `implement`, and `review`. They call the global skills `grilling`, `domain-modeling`, `research`, `prototype`, `tdd`, and `code-review`.
6. **The tracker stays local markdown** (ADR 0010). A new feature gets a map, decision tickets, a spec, acceptance tests, and tickets.

## User Stories

1. As Brian, I want one repo for the site and the pipeline, so that one spec covers a feature that touches both.
2. As Brian, I want the pipeline history kept, so that `git log` and `git blame` still explain old pipeline code.
3. As Brian, I want the old pipeline repo archived read-only, so that no agent commits to it by mistake.
4. As Brian, I want the Tuesday weekly build to run from the merged repo, so that the week 9 report ships on time.
5. As Brian, I want `publish` to copy files inside one repo, so that no step depends on a second checkout at a fixed path.
6. As Brian, I want `publish` to stage only the published data, so that it never commits half-done work from `main`.
7. As Brian, I want the GitHub Pages deploy to run only when site files change, so that a pipeline change does not deploy the site.
8. As Brian, I want the Fly API to deploy from the pipeline folder, so that api.cpcfantasy.com keeps working.
9. As Brian, I want the daily refresh workflow to keep running, so that the API stays warm.
10. As an agent, I want one `make check` at the root, so that I run every rule with one command.
11. As an agent, I want a diff option on the check, so that a ticket runs only the checks for the apps it touched.
12. As an agent, I want one prek hook installed, so that a commit with a broken rule fails before it lands.
13. As an agent, I want one CI file, so that the hook and CI run the same check.
14. As an agent, I want one ADR series, so that "ADR 0005" names one decision, not two.
15. As an agent, I want one glossary at the root, so that a term has one meaning across the site and the pipeline.
16. As an agent, I want one `state.md` with an `App` column, so that I find the next ticket for any feature in one file.
17. As an agent, I want the nine shared features kept in `site/` and `pipeline/` subfolders, so that every old "Blocked by" line stays true.
18. As an agent, I want the tracker checks to read the merged paths, so that `state.md` stays true after the move.
19. As an agent, I want one CLAUDE.md at the root, so that I learn both apps from one file.
20. As an agent, I want each app to keep its own short CLAUDE.md, so that I get the app commands when I work in that folder.
21. As Brian, I want `cpc:plan` to turn an idea into a map, so that the unknowns are visible before any spec.
22. As Brian, I want `cpc:plan` to skip the map when no fog exists, so that a small idea goes straight to one spec.
23. As Brian, I want each fog item to become a decision ticket of one kind, so that I know if it needs a grill, research, a prototype, or a spec.
24. As Brian, I want `cpc:plan` to clear one decision ticket per session, so that each session ends with one recorded decision.
25. As Brian, I want `cpc:to-spec` to write the spec in our PRD format, so that every spec reads the same.
26. As Brian, I want `cpc:to-acceptance` to write numbered acceptance tests, so that I approve what "done" means before the build.
27. As Brian, I want site acceptance tests to name the widths and the theme, so that the evidence matches ADR 0001.
28. As Brian, I want pipeline acceptance tests to name a real week, so that the evidence is real output and not a fake.
29. As Brian, I want `cpc:to-tickets` to write tickets with "Blocked by" lines and a `state.md` row, so that the next ticket is always clear.
30. As Brian, I want `cpc:implement` to build each ticket in its own worktree on a ticket branch, so that tickets do not collide.
31. As Brian, I want `cpc:implement` to merge each ticket into the spec branch only after the check passes, so that the spec branch stays green.
32. As Brian, I want `cpc:implement` to run `code-review` on the spec branch and fix the findings, so that I do not read the diff.
33. As Brian, I want `cpc:implement` to record evidence for each acceptance test with no verdict, so that the verdict stays mine.
34. As Brian, I want `cpc:implement` to open one PR from the spec branch to `main`, so that one spec is one merge.
35. As Brian, I want `cpc:review` to do one round of PR feedback per run, so that each run has a clear end.
36. As Brian, I want a check that reads my verdict comment, so that a spec cannot merge with a FAIL or a missing test.
37. As Brian, I want each `cpc` skill to stop if a global skill it calls is missing, so that it never guesses a step.
38. As Brian, I want the plugin turned on in the repo settings, so that every session in the repo has the `cpc` skills.
39. As Brian, I want open features to finish on the new branch model, so that no feature runs two flows at once.
40. As Brian, I want every open ticket branch merged or deleted before the move, so that no branch is stranded on old paths.

## Implementation Decisions

- **The order of the move.** First clear the open ticket branches in both repos. Then move the site into `apps/site/` in one commit. Then add the pipeline with `git subtree add` under `apps/pipeline/`. The site moves first so that `git log --follow` keeps one rename per file.
- **The day of the move.** The move lands on a Wednesday or a Thursday. The weekly build runs on Tuesday, and a week must pass between the move and a build.
- **The weekly job.** The LaunchAgent `com.briankwon.cornerstone-weekly` and `bin/cornerstone-build` hold the old pipeline path. Both change to the merged path. The agent is unloaded and loaded again after the change.
- **`publish`.** It copies into the site's published-data folder in the same repo. It no longer takes a second checkout. It stages only that folder, then commits and pushes `main`. The site Makefile targets that need the local API change to point at the pipeline folder.
- **Deploy paths.** The Pages workflow builds from `apps/site/` and runs on changes there. The Fly config and its Dockerfile build from `apps/pipeline/`. The daily refresh workflow moves into the root workflows.
- **The root check.** A root Makefile has `check` and `check-fast`. Each runs the site target, then the pipeline target, and fails on the first failure. A diff option takes a base branch and runs only the apps with changed files. A change at the root runs both apps.
- **The rule tests.** The tracker rules in both apps change to read the root `state.md` and the root `.scratch/`. One more rule checks the `publish` exception. One more rule checks the verdict comment. They report in the existing rule-report shape of each app.
- **The records.** The pipeline ADRs 0001 to 0010 and the site ADRs 0001 to 0010 merge into one series. The site ADRs 0007 to 0010 are the One records. A map file lists each old number and its new number. Each old number in a doc or a ticket gets its new number. The glossaries merge into one root `GLOSSARY.md`. A term with two meanings is a conflict, and the ticket stops and names it.
- **The tracker.** One root `.scratch/`. The nine shared features keep `site/` and `pipeline/` subfolders with no renumbering. Other old features move as they are. One `docs/agents/state.md` gets an `App` column. One `docs/agents/issue-tracker.md` describes the old shape and the new shape.
- **The new feature shape.** A map with the sections DESTINATION, DECISIONS SO FAR, NOT YET SPECIFIED, and OUT OF SCOPE. Decision tickets of the kind grill, research, prototype, or spec. A spec. An acceptance file with tests `AT-<n>`. Tickets.
- **The branch model.** `main` is the record branch. A spec branch is `<slug>`. A ticket branch is `<slug>-<NN>`, local, in a worktree. A ticket merges into the spec branch with `git merge --no-edit`. The spec PR merges as a squash.
- **The verdict comment.** One PR comment with one line per test: the test id, then PASS, FAIL, or BLOCKED, then an optional note. A CI job reads the comment and the acceptance file. It fails if a test has no line or a line is not PASS.
- **The plugin.** `cpc` lives in `.claude/plugin/` with a manifest, and the repo marketplace file names it. The repo settings turn it on. Each skill ports the idea of its source, not the text. It drops the Atrium labels, the Temporal cluster path, `check:judge`, and the portal checks.
- **This spec runs on today's flow.** The new flow does not exist until this spec is done. So each ticket here merges to `main` as today. The first feature after this spec uses the full flow.

## Testing Decisions

- A good test checks behavior a user or an agent sees: a command exit code, a file on disk, a rule report. It does not check how a script is written.
- **The one seam is the root `make check`.** Every new rule is a rule test that it runs: the tracker rule, the `publish` rule, and the verdict rule. Prior art: `src/tracker-rule.test.ts` in the site, `tests/test_rule_tracker.py` in the pipeline, and the rule-report shape in each app.
- **The `publish` rule** gets a test with a real git repo in a temp folder. One commit stages only the published data and passes. One stages a file outside it and fails. Prior art: the site test that reads week 7 from a temp folder.
- **The verdict rule** gets tests with real acceptance files and real comment text: all PASS passes. A FAIL, a BLOCKED, or a missing test fails.
- **The move is proved by real runs**, not by unit tests:
  - `make check` passes at the root.
  - `pnpm build` and `pnpm check:export` pass in the site folder.
  - `make publish` for week 8 with no push changes no files, because week 8 is already published.
  - The Fly deploy works from the pipeline folder, and the API answers.
  - The Pages deploy works from `main`.
- **The skills** are proved by one dry run each in a throwaway feature. `cpc:plan` writes a map and a decision ticket. `cpc:to-acceptance` writes an acceptance file. `cpc:implement` merges one ticket into a spec branch and opens a draft PR.

## Out of Scope

- A check that compares the pipeline models with the site schemas. It is fog for the first map after this spec.
- GitHub Issues as the tracker. ADR 0010 records why.
- A path where a ticket builds with no session, like the Temporal cluster in One.
- The map, the decision tickets, and the acceptance file for the open features. Their specs already exist.
- A new repo name or a new domain.

## Further Notes

- The verdict check is new, and it may have gaps in its first run. The first spec after this one is its real test.
- The PIPE Makefile comment says `.scratch` is untracked by design, but git tracks it. The tracker ticket fixes the comment.
- Neither prek hook is installed today. The check ticket installs the root hook.
