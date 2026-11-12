# The audit of the open tickets

Ticket: `.scratch/todoist-queue/issues/01-the-audit-of-the-open-tickets.md`. Date: 2026-11-12.

Three agents checked the 71 open tickets of `main` against the git log, the code, and the memory notes. Each line proposes `done` with a commit, `wontfix` with a reason, or `open` with a label, and a confidence. Brian approves or changes each line. Each named commit passed `git cat-file -e`.


A ticket that shipped and merged gets `done` with its commit, also when a later spec changed that code since. The line says so when that is the case.

## site-pages

- `.scratch/site-pages/issues/01-page-shell.md` (now: ready-for-agent) → done dd18742a, high. The commit "Add the page column shell and the card look on every page" merged in 94f52bea and then in 6486cff5 on `main`.
- `.scratch/site-pages/issues/02-home-page.md` (now: ready-for-agent) → done e753f56e, high. The commit "Put the two short home chapters in one row from the tablet tier" merged in 77173fb4 and 6486cff5; the front door (dc564361) replaced the home page later.
- `.scratch/site-pages/issues/03-rankings-table.md` (now: ready-for-agent) → done 442e8d58, high. The commits 442e8d58 and 4bae5201 merged in ba2fb98a; the site redesign 0a8b8868 replaced the table with the Ladder later.
- `.scratch/site-pages/issues/04-analyzer-form.md` (now: ready-for-agent) → done 230ba6e8, high. The commit "Put the analyzer form in one chapter with two team columns" merged in 69c1c4af and 6486cff5.
- `.scratch/site-pages/issues/05-result-cards.md` (now: ready-for-agent) → done 9e09d472, high. The commit "Group the trade result into five chapters" merged in 841abd72 and 6486cff5.
- `.scratch/site-pages/issues/07-black-card-sweep.md` (now: triage) → wontfix, high. `GLOSSARY.md` now lists "dark chapter" under _Avoid_ and defines "Swap card" as a term, so the rename this ticket asks for goes against the glossary; the three named component files are gone.
- `.scratch/site-pages/issues/08-motion-off-hydration.md` (now: triage) → wontfix, low. The rankings row chevron and `src/lib/motion.ts` are gone since the redesign 0a8b8868, and `useMotionOff` now wraps the Framer `useReducedMotion`; nobody checked the warning again on the current pages.
- `.scratch/site-pages/issues/09-home-test-class-name.md` (now: triage) → done 8159f80b, low. Commit 8159f80b removed the `text-red` `className` assertion; but `apps/site/src/app/page.test.tsx:322` from the front door (dc564361) now reads `className` again, so the last box still fails.
- `.scratch/site-pages/issues/10-playoff-header-wrap.md` (now: triage) → wontfix, high. The redesign 0a8b8868 replaced the rankings table with the Ladder, and no "Playoff %" column header exists in `apps/site/src` or `packages`.

## site-report

- `.scratch/site-report/issues/01-type-scale-measure-and-cards.md` (now: ready-for-agent) → done a6cd647d, high. The commit "Step the type scale per tier, cap the blurbs, and set chapters as cards" merged in 95d57c8d on `main`.
- `.scratch/site-report/issues/02-hero-composition.md` (now: ready-for-agent) → done 322dfbac, high. The commit "Set the game changer hero in two parts from the tablet tier up" merged in 7d82a17e and 95d57c8d.
- `.scratch/site-report/issues/03-grid-chapters.md` (now: ready-for-agent) → done a1cf4831, high. The commit "Put the grid chapters in columns from the tablet tier" merged in 1fc76869 and 95d57c8d.
- `.scratch/site-report/issues/04-wide-chapters.md` (now: ready-for-agent) → done e8211e22, high. The commit "Spread the four wide chapters across the tablet and desktop column" merged in 7bc3743e and 95d57c8d.
- `.scratch/site-report/issues/05-chapter-rail.md` (now: ready-for-agent) → done 04f80802, high. The commit "Add the chapter rail to the week page on a desktop" merged in b799b889 and 95d57c8d.
- `.scratch/site-report/issues/06-week-footer.md` (now: ready-for-agent) → done 52763926, high. The commit "Add the week footer with links to the prior and the next week" merged in 49c735f9 and 95d57c8d.
- `.scratch/site-report/issues/07-accessibility-and-browser-pass.md` (now: ready-for-agent) → done 22311557, high. The commit "Add the browser pass screenshots and tick ticket 07" merged in 95d57c8d after the fixes b117cd7e and 5fcfd7ae.

## site-api

- `.scratch/site-api/issues/10-prompt-caching.md` (now: ready-for-agent) → done 6b0e1faf, high. Every box is ticked; "Cache the system prompt on every Claude call" is on `main`, and `apps/pipeline/tests/test_writer.py` asserts the `cache_control` shape and the `1h` TTL.
- `.scratch/site-api/issues/13-word-ban-gaps.md` (now: ready-for-agent) → wontfix, high. Manager brain c133eb89 deleted `analysis.py`, `prompts/analysis.md`, and the rubric, so the prose check this ticket extends is gone.
- `.scratch/site-api/issues/14-ruff-config.md` (now: ready-for-agent) → done eb429ecf, high. "Merge ruff-baseline: a ruff config at 120 columns and a clean baseline" is on `main`, and `make check` of the pipeline and the API runs `ruff check src tests` in CI.
- `.scratch/site-api/issues/15-suggested-counters.md` (now: ready-for-agent) → open needs-triage, low. `packages/analyzer/site/form/analyze-result.tsx` still shows "No counters yet.", and the manager-brain PRD puts counters out of scope; the letter-step method of the ticket died with the rubric, so it needs a new design if Brian still wants it.
- `.scratch/site-api/issues/16-clamp-one-step.md` (now: in-progress) → done e164732c, high. "Clamp the adjuster sum to one step" merged in da7ee83f on `main`; later manager brain c133eb89 removed the rubric and `CLAMP_STEPS`.
- `.scratch/site-api/issues/17-grade-limits.md` (now: in-progress) → done 59f8dcce, high. `GRADES_PER_MINUTE = 5` and `GRADES_PER_DAY = 20` are in `packages/analyzer/python/src/analyzer/tunables.py`, and site-speed 590268f8 did the "Try again in N hours" follow-up; the API now deploys on green.
- `.scratch/site-api/issues/21-team-name-once-per-blurb.md` (now: ready-for-agent) → done ed455b93, high. "Name a team at most once per blurb and per side analysis" is on `main`, and `repeat_failure` and `TWO_TEAM_CHAPTERS` still sit in `packages/facts`; the weekly build reads the prompts from `main`.

## site-foundation

- `.scratch/site-foundation/issues/01-tiers-and-page-column.md` (now: ready-for-agent) → done be975af5, high. The commit "Size the page column per tier and span the masthead" merged in a5559600 on `main`.
- `.scratch/site-foundation/issues/02-destinations-and-menu-sheet.md` (now: ready-for-agent) → done f1c3f09e, high. The commit "Add the menu button and the menu sheet to the masthead" merged in 6a480aec and a5559600.
- `.scratch/site-foundation/issues/03-desktop-row-and-past-weeks-popover.md` (now: ready-for-agent) → done ed7c1d80, high. The commit "Add the desktop row and the Past weeks popover to the menu" merged in a5559600; the redesign 0a8b8868 changed the menu later.
- `.scratch/site-foundation/issues/04-compact-bar.md` (now: ready-for-agent) → done 911899bf, high. The commit "Add the compact bar to the menu" merged in a5559600; the redesign 0a8b8868 changed the menu later.
- `.scratch/site-foundation/issues/05-accessibility-and-browser-pass.md` (now: ready-for-agent) → done 4e9c6b87, high. The commit "Add the browser pass of the accessibility ticket" and the tick a98dd105 merged in a5559600.

## site-speed

- `.scratch/site-speed/issues/01-teams-prefetch-and-skeleton.md` (now: ready-for-agent) → done 590268f8, high. The commit merged in 84d3fabb on `main`, and `packages/analyzer/site/lib/teams-store.ts` and `waitText` in `api.ts` hold the behavior now.
- `.scratch/site-speed/issues/03-lock-the-form-during-a-grade.md` (now: ready-for-agent) → done 4e2015b6, high. The commit "Lock the trade form while a grade runs" merged in 2dcfda4c on `main`, and `grade-bar.tsx` sets `aria-busy` and "Grading…".

## Count

- done: 25
- wontfix: 4
- open: 1
## rankings

- `.scratch/rankings/pipeline/issues/01-the-formula.md` (now: ready-for-agent) → done 78f58d42, high. The merge of `rankings-formula` holds 47a53dd4 "Add the power rankings formula", and the formula lives now in `packages/rankings`.
- `.scratch/rankings/pipeline/issues/02-season-file-command-publish.md` (now: ready-for-agent) → done 49aeb86c, high. The merge of `rankings-file` holds 601be8e3 "Write the season file of power rankings", and later specs extend the file.
- `.scratch/rankings/pipeline/issues/03-the-rankings-chapter.md` (now: ready-for-agent) → done 2e6a4bf7, high. The merge of `rankings-chapter` holds 24a14a34 "Add the rankings chapter with one blurb per team".
- `.scratch/rankings/pipeline/issues/04-streaks-margins-in-the-formula.md` (now: ready-for-agent) → done ce1e0abf, high. The merge of `rankings-form` holds c393978f "Add form streak, median games, and margin to ranks".
- `.scratch/rankings/site/issues/01-reader-and-route.md` (now: ready-for-agent) → done db0fbf3, high. The commit sits on `main` through the merge c6f2db70, and `_routes/rankings/` exists now.
- `.scratch/rankings/site/issues/02-expandable-blurb-row.md` (now: ready-for-agent) → done a68024d, high. The commit sits on `main` through the merge c6f2db70.
- `.scratch/rankings/site/issues/03-home-chapter.md` (now: ready-for-agent) → done 746a5d0, high. Commit 746a5d01 "Add the power rankings chapter to the home page" sits on `main`; site-redesign and front-door later replaced the home page.

## waiver

- `.scratch/waiver/pipeline/issues/09-usage-floor-for-ranked-buckets.md` (now: needs-triage) → wontfix, low. Front-door ticket 15 (071b6021, squash dc564361) shipped the rest-of-season-projection rule; the snap and touches floor is a code screen, which the memory note `no-math-filters` rejects for a later Jev add judgment.
- `.scratch/waiver/pipeline/issues/10-price-flat-per-position.md` (now: needs-triage) → open needs-triage, high. `price.py` still sets the floor from the last win at the position, and `drops.py` still writes "{n} points a week higher" at a margin of 1; front-door ticket 15 says a real price waits for a later waiver spec.
- `.scratch/waiver/pipeline/issues/11-behind-injury-needs-a-starter.md` (now: needs-triage) → done dc564361, high. Front-door ticket 15 commit 071b6021 added `every_above_out` in `packages/waiver/python/src/waiver/buckets.py` with the out-backup test.
- `.scratch/waiver/site/issues/01-the-route-behind-the-flag.md` (now: ready-for-agent) → done c80b0073, high. "Merge waiver-01: the waiver route behind the flag" is on `main`, and every box is checked; clients later removed the flag.
- `.scratch/waiver/site/issues/02-the-war-chest-look.md` (now: ready-for-agent) → done 6b9265bb, high. "Merge waiver-02: the War chest look" is on `main`, and every box is checked.

## next-week-byes

- `.scratch/next-week-byes/pipeline/issues/06-two-chapters-fell-to-templates-in-the-week-7-rebuild.md` (now: backlog) → open needs-triage, low. No team-count fact and no players-in-scope brief exist, and `facts/writer.py` still allows two attempts; no later spec names the issue, so it may no longer matter.
- `.scratch/next-week-byes/site/issues/01-byes-on-the-next-week-games.md` (now: ready-for-agent) → done 9d9ecc86, high. The ticket is a pointer to pipeline ticket 01, which is done in "Merge next-week-byes: players on bye in the Next Week preview".
- `.scratch/next-week-byes/site/issues/02-bye-facts-and-the-next-week-range.md` (now: ready-for-agent) → done 9d9ecc86, high. The ticket is a pointer to pipeline ticket 02, which is done in the same merge.
- `.scratch/next-week-byes/site/issues/03-roast-as-the-default-register.md` (now: ready-for-agent) → done 9d9ecc86, high. The ticket is a pointer to pipeline ticket 03, which is done in the same merge.
- `.scratch/next-week-byes/site/issues/04-the-bye-line-in-the-game-card.md` (now: ready-for-agent) → done 15f11610, high. "Merge next-week-byes: the bye subtitle in the next-week card" is on `main`, and every box is checked.

## manager-pages

- `.scratch/manager-pages/pipeline/issues/12-drop-awards-from-managers-entry.md` (now: ready-for-agent) → open ready-for-agent, high. `awards` and `saved_awards` still sit in `packages/managers/python/src/managers/`, and `MANAGERS_SCHEMA_VERSION` is still 1.
- `.scratch/manager-pages/pipeline/issues/13-grade-test-gaps.md` (now: ready-for-agent) → open ready-for-agent, low. `test_manager_grade.py` has no rank 4 against 3 edge and no hole-cost floor test; `GRADE_SPARE_RANK` no longer exists, so that box needs a rewrite.
- `.scratch/manager-pages/site/issues/01-the-past-week-keeps-every-rostered-player.md` (now: ready-for-agent) → done 62b61cca, high. The ticket copies pipeline ticket 01, done in "Merge manager-pages-01: the past week keeps every rostered player".
- `.scratch/manager-pages/site/issues/02-the-managers-file-and-publish.md` (now: ready-for-agent) → done 003d45bb, high. The ticket copies pipeline ticket 02, done in "Write the managers file per season and publish it" under merge 3d6dff1c.
- `.scratch/manager-pages/site/issues/11-the-bench-sentence-and-the-odds-change-words.md` (now: ready-for-agent) → open ready-for-human, high. `season-so-far.tsx` still writes two "Your" sentences and `changeWords` still writes "up 5"; the ticket says Brian picks the words.

## modular

- `.scratch/modular/pipeline/issues/20-remove-the-chart-parameter-of-context.md` (now: ready-for-agent) → open ready-for-agent, high. `packages/week/python/src/week/sheet/base.py` still takes `chart: ChartValues | None` and sets `self.chart`, and no code reads it.
- `.scratch/modular/site/issues/12-the-fixtures-carry-every-as-of-key-the-api-sends.md` (now: ready-for-agent) → open ready-for-agent, low. Both fixtures now hold `no_chart` and `no_chart_note`, but the null test still uses a hand edit and the schema header names no API commit.

## win-win

- `.scratch/win-win/site/issues/06-shared-api-call-hook.md` (now: ready-for-agent) → done 15e288c6, low. "Move the hooks into src/hooks and add useRequest" moved the abort and stale-run guard into one hook for both forms, but the timeout and the 401 handling stay in each caller by choice.

## agent-habits

- `.scratch/agent-habits/site/issues/03-close-the-site-tickets-whose-merge-main-proves.md` (now: ready-for-agent) → wontfix, low. The repo-wide ticket audit of todoist-queue does this sweep for every feature, and the ticket-close flow of 1d7bfc0d (#33) closes tickets at the spec merge. The named features (rankings, site-foundation, site-report, and others) still show ready-for-agent tickets, so the sweep itself is not done yet.

## analyzer-multi-team

- `.scratch/analyzer-multi-team/issues/10-headshot-strip-gap.md` (now: triage) → done 0a8b8868, low. The site redesign (#11) rebuilt `PlayerChip` in `packages/analyzer/site/form/analyze-result.tsx` with `-mx-sp-2 -mt-sp-2 self-stretch` so the headshot fills the chip. No screenshot confirms the gap is gone.
- `.scratch/analyzer-multi-team/issues/11-to-tag-truncates.md` (now: triage) → wontfix, high. The site redesign 0a8b8868 removed the `Select` To picker and `defaultTo` from `trade-form.tsx`, so the truncated trigger no longer exists.
- `.scratch/analyzer-multi-team/issues/12-finder-and-waiver-pickers.md` (now: triage) → open needs-triage, low. `TeamPicker` still serves `trade-finder.tsx` and the waiver page, but the target `Select` is gone since 0a8b8868, so the ticket must name a new target, such as the team sheet.
- `.scratch/analyzer-multi-team/issues/13-cli-parsed-side-type.md` (now: triage) → wontfix, high. Manager brain c133eb89 (#25) deleted `_trade_side`, `_proposed_sides`, `_routed`, and the `analyze` command from `cli.py`.

## front-door

- `.scratch/front-door/issues/12-buy-low.md` (now: needs-triage) → open ready-for-agent, low. No buy-low code exists, and `front-door-lineup` PRD story 50 keeps the sell list only. Brian deferred buy low on 2026-11-10, so he may prefer `needs-triage` until he picks a spec.

## known-games

- `.scratch/known-games/issues/08-the-site-renders-the-known-games-line.md` (now: ready-for-agent) → done 631f2395, high. The merge "known-games-08: the as-of line shows the known games" is on `main`, and `analyze-result.test.tsx` pins the exact line "Stats through week 6, plus 13 week 7 games, 2 in progress · Snaps pending for 9 games".
- `.scratch/known-games/issues/10-followups-from-the-final-review.md` (now: needs-triage) → open needs-triage, low. No commit after 5b935d74 touches the three items, and `finder_search.py` still calls `season_rank` through `stats_through`, which includes the known games (item 3). Items 1 and 2 may be partly covered by the WOPR rows in the cache key and the stale `stats` flag in `snapshot.py`.

## live-refetch

- `.scratch/live-refetch/issues/01-the-live-api-rewrites-patched-weeks.md` (now: needs-triage) → open needs-triage, low. No commit after acab9e52 adds a patch file or a write guard in `packages/league`. The risk may have shrunk now that week 9 is no longer the latest week, so Brian must decide if it still matters.

## one

- `.scratch/one/issues/11-rename-the-pipeline-chapter-to-prose-block.md` (now: ready-for-agent) → open ready-for-agent, high. `apps/pipeline/src/cornerstone` holds 72 `chapter` names and `rewrite --chapter` stays, and `GLOSSARY.md` line 225 still says the code names it `chapter`. Its blocker 05 is done.

## tone

- `.scratch/tone/issues/09-leftovers-after-the-second-rewrite.md` (now: ready-for-human) → done 80a8a7bb, high. Commit "Fix the four tone habits left after the second rewrite" and fix 958c1ee are on `main`, and week 6 is published with the "in an upset" closer. Only the box "Brian publishes" was open, and weeks 6 to 9 are live.
- `.scratch/tone/issues/10-remove-names-is-case-sensitive.md` (now: ready-for-agent) → open ready-for-agent, low. `remove_names` in `packages/facts/python/src/facts/verifier.py` still runs `re.sub` with no `re.IGNORECASE`. The scope-team-word skip of 28fd4d8e may already hide the "Behold the lamb" failure, so the fix may have a small effect.
- `.scratch/tone/issues/11-facts-command.md` (now: ready-for-agent) → open ready-for-agent, high. `apps/pipeline/src/cornerstone/cli.py` has no `facts` subparser, and no commit adds one.

## trade-grade-v3

- `.scratch/trade-grade-v3/issues/05-rebuild-week-6.md` (now: built) → wontfix, high. Commit 011f46d0 made the trade chapter a recap with no grade and stopped the chart fetch in the weekly build. No published page of weeks 6 to 9 holds a grade.

## week-8-fixes

- `.scratch/week-8-fixes/issues/07-the-readmes-name-the-module-an-agent-needs.md` (now: ready-for-agent) → open needs-triage, low. No README holds the lines the ticket asks for, and no `data/README.md` exists. The clients and package moves changed the target paths and the `CLAUDE.md` step 2 line, so the ticket needs new paths before an agent builds it.
- `.scratch/week-8-fixes/issues/08-the-scoring-component-fact-names-the-component.md` (now: ready-for-agent) → open ready-for-agent, high. `COMPONENT_WORDS` in `packages/rankings/python/src/rankings/chapter.py` still maps `scoring` to "scoring", and `tests/test_sheet.py` still expects "5th in scoring".

## Count

- done: 3
- wontfix: 4
- open: 9

## Approved

Brian approved this audit on 2026-11-12, with these changes to the proposals above:

- `site-pages` 09 stays open as `ready-for-agent`, because its last box fails again.
- Brian kept only the tickets that fix a real bug or change what a manager sees. The six kept tickets are `tone` 10, `week-8-fixes` 08, `manager-pages` site 11, `site-pages` 09, `manager-pages` pipeline 12, and `modular` 20.
- Every other proposed `open` ticket closes as `wontfix`.
- `front-door` 12, buy low, closes as `wontfix` and moves to the Ideas section of the queue.

The result: 44 done, 21 wontfix, 6 open.
