# Clients: acceptance tests

Spec: `.scratch/clients/PRD.md`.

The Test verdict: only Brian gives one. He writes one PR comment on the Spec branch PR, with one line for each test: the id, then PASS, FAIL, or BLOCKED, then an optional note. The PR merges when every test has PASS (ADR 0020). An agent records the evidence and gives no Test verdict.

NorCal has a dark brand with one set only. So each NorCal screenshot is in the dark theme only, at 375, 768, and 1280 px.

## Tests

AT-1: The CPC week 8 rebuild matches the published week
App: pipeline
Stories: 12, 30
Given: the 2026 week 8 data of `cpc` under `clients/cpc/data/2026/`, and the published 2026 week 8 files from before the move.
When: the agent rebuilds 2026 week 8 for `cpc` with the pipeline command, with no Claude call.
Then: the diff of each rebuilt published file against the published file is empty, except the removed key `is_brian` in each team of `page.json`.
Evidence: the command, its output, and the full diff.

AT-2: The CPC sizes derive from the provider
App: pipeline
Stories: 8
Given: the Sleeper league settings of `cpc` for 2026, and the League config values at commit `003c70c` on `main`.
When: the agent derives the lines, the strength rank, and the star ranks from the League settings.
Then: each derived value equals the old League config value.
Evidence: a table of each value, old and derived, and the command that printed the derived values.

AT-3: The CPC week 8 page looks the same after the move
App: site
Stories: 27, 30
Given: screenshots of `https://cpcfantasy.com/2026/week-08/` taken before the move.
When: the reader opens `https://cpc.4thandgoal.app/2026/week-08/`.
Then: each screenshot matches its screenshot from before the move in a side-by-side look check.
Evidence: screenshots of the week 8 page, before and after, at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-4: An old CPC link redirects to the new host
App: site
Stories: 31
Given: the Redirect Rule on `cpcfantasy.com`.
When: the agent runs `curl -I https://cpcfantasy.com/2026/week-08/`.
Then: the answer is a 301 with `location: https://cpc.4thandgoal.app/2026/week-08/`.
Evidence: the command and its output.

AT-5: CPC keeps the theme button and paints light first
App: site
Stories: 40
Given: a browser with no saved theme choice.
When: the reader opens `https://cpc.4thandgoal.app/2026/week-08/`.
Then: the page paints light and shows the theme button.
Evidence: screenshots of the week 8 page at 375, 768, and 1280 px, in the light theme, then each in the dark theme after a press of the theme button.

AT-6: The CPC export omits the waiver board
App: site
Stories: 4, 29
Given: `clients/cpc/client.toml`, whose package list omits `waiver`.
When: the agent runs the site build with `CLIENT=cpc`.
Then: the export has no `/waiver/` route, and no JS file in the export holds waiver code.
Evidence: the build command, a listing of the export routes, and a search of the export JS for a waiver part name with no match.

AT-7: The CPC Trade Analyzer has no finder
App: site
Stories: 4
Given: `finder = false` under `[values.analyzer]` in `clients/cpc/client.toml`.
When: the reader opens the Trade Analyzer page of `cpc.4thandgoal.app`.
Then: the page shows no finder.
Evidence: screenshots of the Trade Analyzer page at 375, 768, and 1280 px, each in the light theme and the dark theme.

AT-8: No old color name remains in the source
App: site
Stories: 27
Given: the source of `apps/site/` and `packages/*/site/` on the Spec branch.
When: the agent searches the source for the classes and tokens of `red`, `blk`, `gry`, and `wht`, such as `bg-red`, `text-blk`, and `--color-gry`.
Then: the search finds no match.
Evidence: the search command and its empty output.

AT-9: NorCal has its own brand and site name
App: site
Stories: 1, 9, 32, 42
Given: the `norcal` Worker at `norcal.4thandgoal.app` and the 2026 week 8 data of `norcal`.
When: the reader opens `https://norcal.4thandgoal.app/2026/week-08/`.
Then: the masthead shows "NorCal Apex 6" as text, on the dark NorCal brand.
Evidence: screenshots of the week 8 page at 375, 768, and 1280 px, in the dark theme.

AT-10: NorCal has no theme button
App: site
Stories: 39
Given: `clients/norcal/brand.toml`, which has no `[light]` table.
When: the reader opens `https://norcal.4thandgoal.app/2026/week-08/`.
Then: no theme button shows at any width.
Evidence: screenshots of the masthead and the menu at 375, 768, and 1280 px, in the dark theme.

AT-11: The NorCal week has no Median Game chapter
App: both
Stories: 33
Given: the 2026 week 8 data of `norcal`, whose League settings have no median game.
When: the agent builds 2026 week 8 for `norcal`, and the reader opens its week 8 page.
Then: `page.json` has no Median Game chapter, and the page shows none.
Evidence: the build command, the chapter list of `page.json`, and screenshots of the chapter rail at 375, 768, and 1280 px, in the dark theme.

AT-12: The NorCal standings count one game a week
App: both
Stories: 34
Given: the 2026 week 8 data of `norcal`.
When: the agent builds 2026 week 8 for `norcal`, and the reader opens the standings.
Then: the wins and the losses of each team add up to 8.
Evidence: the standings fields of `page.json` for each team, and screenshots of the standings at 375, 768, and 1280 px, in the dark theme.

AT-13: NorCal has no DEF
App: both
Stories: 35
Given: the NorCal roster slots, which have no DEF slot.
When: the agent builds 2026 week 8 for `norcal`, and the reader opens the week 8 page.
Then: the pool and the leaders in `page.json` and on the page hold no DEF.
Evidence: the positions of the pool and the leaders in `page.json`, and screenshots of the leaders at 375, 768, and 1280 px, in the dark theme.

AT-14: The NorCal projections use full PPR
App: pipeline
Stories: 36
Given: the 2026 week 8 data of `norcal`, with 1.0 reception points.
When: the agent builds 2026 week 8 for `norcal`.
Then: the projection of one named WR on a NorCal roster equals his Sleeper `pts_ppr` value for week 8.
Evidence: the WR, his projection in the published file, and the `pts_ppr` value in the raw Sleeper data.

AT-15: The NorCal Trade Analyzer has the finder
App: site
Stories: 37
Given: `finder = true` under `[values.analyzer]` in `clients/norcal/client.toml`.
When: the reader opens the Trade Analyzer page of `norcal.4thandgoal.app`.
Then: the page shows the finder.
Evidence: screenshots of the Trade Analyzer page at 375, 768, and 1280 px, in the dark theme.

AT-16: The NorCal menu is a bar
App: site
Stories: 38
Given: `layout = "bar"` under `[menu]` in `clients/norcal/client.toml`, with no `items`.
When: the reader opens `https://norcal.4thandgoal.app/2026/week-08/`.
Then: the menu shows as a bar, with the items in the order of the package list.
Evidence: screenshots of the menu at 375, 768, and 1280 px, in the dark theme.

AT-17: Each text pair of each brand passes WCAG AA
App: site
Stories: 41
Given: `clients/cpc/brand.toml` and `clients/norcal/brand.toml`.
When: the agent runs the contrast test of the brands.
Then: the output lists each text pair of each set of `cpc` and `norcal` with a ratio of 4.5 or more.
Evidence: the command and its output.

AT-18: A site build with no `CLIENT` fails
App: site
Stories: 3
Given: a shell with no `CLIENT` env value.
When: the agent runs `pnpm build` in `apps/site/`.
Then: the build exits non-zero with a message that names `CLIENT`.
Evidence: the command, its output, and its exit code.

AT-19: A pipeline build with no client fails
App: pipeline
Stories: 3
Given: the 2026 week 8 data of `cpc`.
When: the agent runs the week build command with no client slug.
Then: the command exits non-zero with a message that names the client slug.
Evidence: the command, its output, and its exit code.

AT-20: An unknown key in `client.toml` fails the check
App: both
Stories: 6
Given: a copy of `clients/cpc/client.toml` with the extra key `finderr = true` under `[values.analyzer]`.
When: the agent runs the check of the client files, in the site build and in the pipeline.
Then: each check fails with a message that names `finderr` and the file.
Evidence: each command and its output.

AT-21: A menu item for an omitted package fails the check
App: both
Stories: 4, 6
Given: a copy of `clients/cpc/client.toml` with the menu item `{ package = "waiver" }`, and no `waiver` in the package list.
When: the agent runs the check of the client files, in the site build and in the pipeline.
Then: each check fails with a message that names the menu item and `waiver`.
Evidence: each command and its output.

AT-22: A stale exported schema fails the check
App: both
Stories: 7
Given: a new package value in the pydantic model of `analyzer`, with no new export of its JSON Schema.
When: the agent runs the full check.
Then: the check fails with a message that names the stale schema file of `analyzer`.
Evidence: the command and its output.

AT-23: A client with only `week` builds a week with no rankings
App: site
Stories: 4, 26
Given: a test client whose package list is `["week"]`.
When: the agent runs the site build for that client.
Then: the export has a week page with no rankings chapter, and no rankings route.
Evidence: the build command, a listing of the export routes, and the chapter list of the built week page.

AT-24: The full check builds each client
App: both
Stories: 10
Given: the client folders `clients/cpc/` and `clients/norcal/`.
When: the agent runs the full check at the root.
Then: the output shows a site build of `cpc` and a site build of `norcal`, each with success.
Evidence: the command and the lines of its output for each build.

AT-25: The generated site files stay out of git
App: site
Stories: 29
Given: a clean worktree of the Spec branch.
When: the agent runs the site build with `CLIENT=cpc`.
Then: `git status --short` prints nothing.
Evidence: each command and its output.

AT-26: The publish stages only the data of the client
App: pipeline
Stories: 11
Given: the built 2026 week 8 of `cpc`.
When: the agent runs the publish step for `cpc` up to the stage, with no push.
Then: `git diff --cached --name-only` lists only paths under `clients/cpc/published/2026/`.
Evidence: the commands and their output.

AT-27: The API serves each client by its path
App: pipeline
Stories: 2, 15
Given: the API deploy at `api.4thandgoal.app`.
When: the agent calls `GET https://api.4thandgoal.app/clients/norcal/teams` and `GET https://api.4thandgoal.app/clients/cpc/teams`.
Then: the first answer lists each NorCal team, 12 by assumption, and the second lists each CPC team.
Evidence: each command, the team names of each answer, and the real NorCal team count.

AT-28: The old API path answers as CPC
App: pipeline
Stories: 31
Given: the API deploy, with its cert for `api.cpcfantasy.com`.
When: the agent calls `GET https://api.cpcfantasy.com/teams`.
Then: the answer lists each CPC team.
Evidence: the command and the team names of the answer.

AT-29: The rate limit of the grades counts per client
App: pipeline
Stories: 16
Given: a local API run with a low grade limit in the test env.
When: the agent sends grades for `cpc` past its limit, then one grade for `norcal`.
Then: the `cpc` grade past the limit answers 429, and the `norcal` grade answers 200.
Evidence: the env values, each request, and each status code.

AT-30: A bad `client.toml` stops the API at start
App: pipeline
Stories: 17
Given: a copy of the client folders where `clients/norcal/client.toml` has no `timezone`.
When: the agent starts the API locally over that copy.
Then: the start exits non-zero with a message that names the file and `timezone`.
Evidence: the command, its output, and its exit code.

AT-31: An undeclared import between packages fails the check
App: pipeline
Stories: 18, 19, 20, 21
Given: a test line in `apps/api/` that imports `waiver`, which the API does not list as a dependency.
When: the agent runs the API check with `uv run --exact --package` and the API package name.
Then: the check fails with `ModuleNotFoundError` for `waiver`.
Evidence: the command and its output.

AT-32: A change in one language checks both languages of the package
App: both
Stories: 22, 23
Given: a diff that changes one line in `packages/waiver/python/` only.
When: the agent runs the check of the diff.
Then: the check runs the Python of `waiver`, the site side `@cpc/waiver`, and each package and app that depends on `waiver`.
Evidence: the command and the list of what the check ran.

AT-33: A client folder holds no code
App: both
Stories: none
Given: the folder `clients/` on the Spec branch.
When: the agent searches `clients/` for files that end in `.py`, `.ts`, `.tsx`, `.js`, or `.mjs`.
Then: the search finds no file.
Evidence: the search command and its empty output.

## Trace

Story 1: AT-9
Story 2: AT-27
Story 3: AT-18, AT-19
Story 4: AT-6, AT-7, AT-21, AT-23
Story 5: no test. Reason: a README default is a doc, and review checks it.
Story 6: AT-20, AT-21
Story 7: AT-22
Story 8: AT-2
Story 9: AT-9
Story 10: AT-24
Story 11: AT-26
Story 12: AT-1
Story 13: no test. Reason: the manual steps are a process, not a behavior of the work.
Story 14: no test of its own. Reason: AT-1 reads the shared returns file.
Story 15: AT-27
Story 16: AT-29
Story 17: AT-30
Story 18: AT-31
Story 19: AT-31
Story 20: AT-31
Story 21: AT-31
Story 22: AT-32
Story 23: AT-32
Story 24: no test of its own. Reason: structure, and AT-1 shows no change in output.
Story 25: no test of its own. Reason: structure, and AT-1 shows no change in output.
Story 26: AT-23
Story 27: AT-3, AT-8
Story 28: no test. Reason: no second provider exists to test the port.
Story 29: AT-6, AT-25
Story 30: AT-1, AT-3
Story 31: AT-4, AT-28
Story 32: AT-9
Story 33: AT-11
Story 34: AT-12
Story 35: AT-13
Story 36: AT-14
Story 37: AT-15
Story 38: AT-16
Story 39: AT-10
Story 40: AT-5
Story 41: AT-17
Story 42: AT-9
Out of scope "A client that swaps one part for its own code": AT-33

## Revisions

- 2026-11-04: AT-7, AT-15, and AT-20 name `[values.analyzer]`, not `[packages.analyzer]`. The old shape is not valid TOML. Brian chose the name.
