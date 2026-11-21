# Design checks and speed: evidence

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests: `.scratch/design-checks-speed/ACCEPTANCE.md`.
Built from: `2108f8bc`, on 2026-11-21. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: 1 min for 1 site test.

After the round, fix group n (d4145d31, merged as 5cf24030) changed one test file, `apps/site/src/component-rule.test.ts`. It adds 1 test, so the suite has 1955 tests at 5cf24030; AT-19 and AT-20 show the count at 2108f8bc. AT-21 is recorded again at 5cf24030.

Smoke run: `evidence/smoke/`. Last line of `smoke.log`: "Smoke run: 7 flows, 7 passed, 0 failed".
Background check: `make check` on `2108f8bc` ran from 01:27:04 to 01:48:12 and ended `EXIT 0`.

## AT-1: The lint fails a raw button outside `ui/`

App: site
Then: the command exits non-zero, and the output names the element rule, the file, the line of the `<button>`, and the wrapper of `ui/` to use.
Files: `evidence/AT-1/output.txt`, `evidence/AT-1/fixture.txt`
Observation: The run on `packages/design/lint/fixtures/no-raw-element/outside/raw-button.tsx` ends `exit 1`. The output prints `raw-button.tsx:6:10: error design(no-raw-element)` and names `Button` from `packages/design/site/ui/button.tsx` and `PendingButton` from `packages/design/site/ui/pending-button.tsx`.

## AT-2: The lint fails a raw dialog outside `ui/`

App: site
Then: the command exits non-zero, and the output names the element rule and the line of the `<dialog>`.
Files: `evidence/AT-2/output.txt`, `evidence/AT-2/fixture.txt`
Observation: The run on `no-raw-element/outside/raw-dialog.tsx` ends `exit 1`. The output prints `raw-dialog.tsx:6:10: error design(no-raw-element)` and names `Dialog` from `packages/design/site/ui/dialog.tsx`.

## AT-3: The lint fails a raw color literal

App: site
Then: the command exits non-zero and names the raw color rule once for each of the two lines.
Files: `evidence/AT-3/output.txt`, `evidence/AT-3/fixture.txt`
Observation: The fixture `raw-color/colored.tsx` has `style={{ color: "#ff0000" }}` on line 6 and `className="bg-[rgb(0_0_0)]"` on line 7. Line 7 writes the rgb value with Tailwind underscores, not `rgb(0 0 0)`. It also has an `oklch()` template on line 8. The run ends `exit 1` and prints `design(no-raw-color)` one time each at 6:24, 7:21, and 8:18, plus one `design(no-arbitrary-value)` at 7:22.

## AT-4: The lint fails an arbitrary color value

App: site
Then: the command exits non-zero and names the value rule and the line of the class.
Files: `evidence/AT-4/output.txt`, `evidence/AT-4/fixture.txt`
Observation: The run on `no-arbitrary-value/color.tsx` ends `exit 1`. The output prints `color.tsx:6:29: error design(no-arbitrary-value)` with the class `bg-[color-mix(in_srgb,var(--color-accent)_28%,var(--color-card))]`.

## AT-5: The lint fails an arbitrary spacing value

App: site
Then: the command exits non-zero and names the value rule and the line of the class.
Files: `evidence/AT-5/output.txt`, `evidence/AT-5/fixture.txt`
Observation: The fixture `no-arbitrary-value/spacing.tsx` has the class inside a `cn(...)` call on line 9. The run ends `exit 1` and prints `spacing.tsx:9:30: error design(no-arbitrary-value)` with `top-[calc(var(--spacing-touch)+2*var(--spacing-sp-2)+1px)]`.

## AT-6: The lint passes variant, layout, and motion values

App: site
Then: the command exits 0.
Files: `evidence/AT-6/output.txt`, `evidence/AT-6/fixture.txt`
Observation: The fixture `no-arbitrary-value/allowed.tsx` has only `grid-cols-[1fr_auto]`, `transition-[opacity,transform]`, and `data-[state=open]:opacity-100` as bracket values. The run prints no error and ends `exit 0`.

## AT-7: A one-line ignore with a reason passes

App: site
Then: the command exits 0.
Files: `evidence/AT-7/output.txt`, `evidence/AT-7/fixture.txt`
Observation: The fixture `no-arbitrary-value/ignored.tsx` is the AT-5 class with `// oxlint-disable-next-line design/no-arbitrary-value -- a one-off offset that no token names` on line 9, above the class on line 10. The run prints no error and ends `exit 0`.

## AT-8: The lint fails a `@ui-sdk` import outside `ui/`

App: site
Then: the command exits non-zero and names `no-restricted-imports` and the line of the import.
Files: `evidence/AT-8/output.txt`, `evidence/AT-8/fixture.txt`
Observation: The run on `packages/design/lint/fixtures/outside/top-band.tsx` ends `exit 1`. The output prints `top-band.tsx:5:1: error eslint(no-restricted-imports): '@ui-sdk/react' import is restricted`.

## AT-9: The `@ui-sdk` rule test is gone

App: site
Then: `apps/site/src/ui-sdk-rule.test.ts` does not exist, and ADR 0035 names ADR 0038 as the new home of its rule.
Files: `evidence/AT-9/output.txt`
Observation: `git ls-files apps/site/src | grep ui-sdk-rule` prints nothing and ends `exit 1`, and `ls` of the file reports "No such file". `git diff main -- docs/adr/0035*` replaces the rule-test line with a line about `no-restricted-imports` in `.oxlintrc.json` that ends "ADR 0038 moved the rule there from a rule test."

## AT-10: The lint fails a part with no use lines

App: site
Then: the command exits non-zero and names the doc rule and the file.
Files: `evidence/AT-10/output.txt`, `evidence/AT-10/fixture.txt`
Observation: The run on `packages/design/lint/fixtures/use-lines/parts/no-use-line.tsx` ends `exit 1`. The output prints `no-use-line.tsx:1:1: error design(use-lines): The top docstring has no line that starts with "Use it when:".`

## AT-11: The lint passes on all site code

App: site
Then: the command exits 0 with no warning of a design rule.
Files: `evidence/AT-11/output.txt`
Observation: `pnpm --dir apps/site lint` runs with no `LINT_FILES`, so oxlint gets `--deny-warnings` on `apps/site packages/*/site` plus the plugin files. It prints no diagnostic line and ends `exit 0`.

## AT-12: No raw button and no hand copy of the band height remain

App: site
Then: neither search finds a match. Each of the 8 files that had a raw `<button>` on 2026-11-20 now uses a wrapper of `ui/`.
Files: `evidence/AT-12/output.txt`
Observation: Both searches of `apps/site/src` and `packages/*/site`, outside `/ui/` and test files, print nothing and end `exit 1`. At the merge base `05d7e805` (2026-11-20), 12 front-door files had a raw `<button>`, not 8. The output gives the diff stat of all 12 files, and each file now imports `Button` from `@cpc/design/ui/button`.

## AT-13: The lint config holds no allowlist

App: site
Then: the config ignores only build output, test fixtures, and generated files, and names no source file of the site. Each ignore comment has a reason on the same line.
Files: `evidence/AT-13/output.txt`, `evidence/AT-13/generated.txt`
Observation: The `ignorePatterns` of `.oxlintrc.json` hold `**/.next/**`, `**/out/**`, `apps/site/public/**`, `apps/site/test-results/**`, `apps/site/src/generated/**`, `apps/site/src/app/(client)/**`, and `apps/site/next-env.d.ts`. The search finds 24 `oxlint-disable-next-line design/no-arbitrary-value` comments, and 0 of them have no ` -- <reason>` on the same line. `generated.txt` shows where each pattern comes from: `apps/site/src/app/(client)/` and `apps/site/src/generated/` are folders that `apps/site/scripts/client-build.mjs` empties and writes on each build (lines 139 to 141 and 486 to 495), the root `.gitignore` lists both under "The client build of the site writes these", and git tracks 0 files in either; `apps/site/test-results/` is git-ignored; `apps/site/next-env.d.ts` is the file that Next.js writes, with the line "This file should not be edited".

## AT-14: The hook blocks a commit with a raw button

App: root
Then: the hook fails, the commit does not land, and the output names the element rule and the file.
Files: `evidence/AT-14/output.txt`
Observation: The probe added `<button type="button">probe</button>` to `apps/site/src/app/_routes/analyzer/home.tsx`, and `git commit -m "probe"` ran with the hook. The output shows `make check-fast STAGED=1....Failed`, `apps/site/src/app/_routes/analyzer/home.tsx:16:7: error design(no-raw-element)`, `exit 1`, and `git log -1 --oneline` = `2108f8bc` before and after. The probe ran on the Spec branch itself, not on a scratch branch. The file was put back, and `git status --short` no longer lists it.

## AT-15: Each part file has its two use lines

App: site
Then: each one has a `Use it when:` line and a `Do not use it when:` line, and the README of each folder still has its "Knows" list.
Files: `evidence/AT-15/table.md`, `evidence/AT-15/readme-knows.txt`
Observation: The table lists 32 component files: 12 in `ui/` and 20 in `parts/`, with the `.test.tsx` files left out. Each row has a `Use it when:` line and a `Do not use it when:` line, with no `-` cell. Both `packages/design/site/ui/README.md` and `packages/design/site/parts/README.md` have `## Knows` on line 3, with a list under it.

## AT-16: The chips look the same with the role tokens

App: site
Then: each chip at rest, chosen, and in hover has the same fill on both branches.
Files: `evidence/AT-16/steps.json`, `evidence/AT-16/runner.txt`, `evidence/AT-16/<375|768|1280>-<light|dark>.png`, `evidence/AT-16/main-<375|768|1280>-<light|dark>.png`, `evidence/AT-16/hover-<w>-<theme>.png`, `evidence/AT-16/main-hover-<w>-<theme>.png`, `evidence/AT-16/computed.txt`, `evidence/AT-16/main-computed-raw.txt`, `evidence/AT-16/spec-computed-raw.txt`, `evidence/AT-16/chips.sh.txt`, `evidence/AT-16/steps.txt`
Observation: The chip is the Season Sim Tool tile of the site answer to "what tools are there", for Lil Fridge on cpc week 10. Its states are the tile at rest, its icon circle (the chosen wash), and the tile in hover on a fine pointer. `computed.txt` shows the same `background-color` on main `182ade52` and on the Spec head `2108f8bc` for all 3 states, at all 3 widths, in both themes: light rest is `color(srgb 0.972157 0.920392 0.916471)`, and dark rest is `rgb(38, 38, 38)`. The shots of the two branches show the same chip fills; the Spec `375-light.png` from the runner is 399 px wide with a blank strip at the right edge, and the Spec runner shots lack the "1 new" badge of the Trade Wire that the main shots show.

## AT-17: The chips use the role tokens and no `dark:` fill

App: site
Then: the chips use `--color-accent-wash`, `--color-accent-wash-chosen`, and `--color-accent-wash-hover`, with no `dark:bg-[` class. The dark block sets each of the three tokens.
Files: `evidence/AT-17/output.txt`
Observation: `site-answer.tsx` uses `bg-accent-wash-chosen` on line 69, `hover-fine:bg-accent-wash-hover` on line 73, and `bg-accent-wash` with `hover-fine:bg-accent-wash-hover` on line 132. A search for `dark:bg-[` in that file finds nothing, and the only `dark:` class is `dark:border-rule` on line 132. `globals.css` sets the three tokens on lines 258 to 260 of `@theme static`, and again on lines 366 to 368 of `.dark`.

## AT-18: The glossary defines a role token and a scale step

App: root
Then: it has the terms **Role token** and **Scale step**, each with one meaning and an _Avoid_ line.
Files: `evidence/AT-18/output.txt`
Observation: Both entries are on lines 253 to 259 of `GLOSSARY.md`, inside "## Site language". Each has one meaning line and an `_Avoid_` line: "Semantic token, alias, design variable" for Role token, and "Primitive, base token, raw value" for Scale step. Each term heading shows up one time.

## AT-19: `bun test` runs the site suite, and Vitest is gone

App: site
Then: the run uses `bun test` and exits 0. No `package.json` of the workspace names `vitest`, and `apps/site/vitest.config.mts` does not exist.
Files: `evidence/AT-19/check-site-unit.txt`, `evidence/AT-19/vitest-search.txt`
Observation: `make check-site-unit` ran `bun test --isolate --parallel=10`, printed "Ran 1954 tests across 203 files", "==> test: ok", and exit code 0. The grep of the 11 tracked `package.json` files for `vitest` and `git ls-files apps/site | grep vitest` both exit 1 with no match, and `ls apps/site/vitest.config.mts` reports no such file.

## AT-20: The test count did not drop

App: site
Then: the pass count equals 1,775, plus each test that a ticket added and minus each test that a ticket removed on purpose. Each added or removed test is named with its ticket. No test is skipped.
Files: `evidence/AT-20/main-vitest.txt`, `evidence/AT-20/spec-ci-bun.txt`, `evidence/AT-20/spec-local-bun.txt`, `evidence/AT-20/changes.txt`
Observation: Vitest on `main` gives "Tests 1775 passed" in 183 files at 1fc0a06e (run 44656282511) and "Tests 1898 passed" in 192 files at the merge base 05d7e805 (run 44860949058, the #84 merge into the Spec branch). `bun test` on the Spec branch gives "1954 pass, 0 fail" across 203 files in CI (job 136753507714) and locally with 0 skipped. The per-file table shows 191 files with the same count and a net change of +56 from 13 files (1898 + 56 = 1954), each test named with its ticket or review-fix branch; the 5 tests of `ui-sdk-rule.test.ts` are removed by ticket 01.

## AT-21: The tests use the native `bun:test` calls

App: site
Then: neither search finds a match.
Files: `evidence/AT-21/output.txt`
Observation: At 5cf24030, over 203 site test files, the search for `\bvi\.`, the search for an import from `vitest`, and the search for any `vitest` text each exit 1 with no match. At 2108f8bc the `\bvi\.` search found one comment line in `apps/site/src/component-rule.test.ts:34` that named `vi.mock`; fix group n changed that comment and its regex to `mock.module`.

## AT-22: The stub helper restores each value

App: site
Then: the second test sees the real `fetch` and the real env value, and both tests pass.
Files: `evidence/AT-22/stubs.test.ts`, `evidence/AT-22/stubs.ts`, `evidence/AT-22/output.txt`
Observation: The first test stubs `fetch`, `HOME`, and an unset env name; the second test expects the real `fetch`, the real `HOME`, and no unset name. `bun test ./test/stubs.test.ts` prints "2 pass, 0 fail", exit code 0, and the JUnit report names both tests with 0 failures.

## AT-23: `bun check` fails on a type error

App: site
Then: the script runs `next typegen` first, then `bun check`, and exits non-zero with the file and the line of the error.
Files: `evidence/AT-23/output.txt`
Observation: In a scratch worktree with `export const probeLabel: string = 42;` added to `apps/site/src/lib/routes.ts`, `pnpm typecheck` runs `next typegen && bun check --no-script`. It prints "Types generated successfully", then an error at `file="src/lib/routes.ts" line="30"` code TS2322 "Type 'number' is not assignable to type 'string'", and exits 1.

## AT-24: The format check fails on a file out of format

App: site
Then: the hook fails on the format check and names the file. The commit does not land.
Files: `evidence/AT-24/output.txt`, `evidence/AT-24/class-order-only.txt`
Observation: On a scratch branch, the class list of `not-found.tsx` is reversed and one line has 3 extra spaces. `git commit` prints "make check-fast STAGED=1 ... Failed", the fmt step names `apps/site/src/app/not-found.tsx`, "1 file needs formatting", and "==> fmt: FAILED", and `git log -1 --oneline` reads 2108f8bc before and after. A second file shows that the class order change alone also fails `fmt:check`.

## AT-25: pnpm stays the installer with the same versions

App: root
Then: no version of a package that `main` already locks has changed. The only new entries are the new tools of the spec, such as Oxlint and happy-dom. No `bun.lock` exists.
Files: `evidence/AT-25/lock-diff.txt`, `evidence/AT-25/versions.txt`
Observation: The packages section goes from 538 to 483 entries: 85 removed, 30 added. The added entries are oxlint and its 19 bindings, happy-dom, `@happy-dom/global-registrator`, `@types/bun`, `bun-types`, `@types/ws`, `ws`, `@types/whatwg-mimetype`, `buffer-image-size`, `entities@7.0.1`, and `whatwg-mimetype@3.0.0`; the last two are names that `main` locks at 8.1.0 and 5.0.0. Seventeen versions that `main` locks are gone while their name stays at another version, each one a dependency of vite, vitest, or jsdom on `main` (for example `lightningcss@1.33.0`, `undici@8.12.3`, `lru-cache@11.5.3`). The importers section only adds oxlint, happy-dom, and `@types/bun` and drops vitest, jsdom, and `@vitejs/plugin-react`; `packageManager` `pnpm@10.12.4`, Node `>=22`, `.nvmrc` 22, and the workflow `node-version: 22` lines show no diff with `main`; `.bun-version` (1.4.5) is new, and `git ls-files | grep bun.lock` exits 1.

## AT-26: A full `make check-fast` takes 97 s or less

App: root
Then: each run exits 0, and each wall-clock time is 97 s or less, against the baseline of 195 s.
Files: `evidence/AT-26/quiet-1.txt`, `evidence/AT-26/run-1.txt`, `evidence/AT-26/quiet-2.txt`, `evidence/AT-26/run-2.txt`
Observation: Each run started after three empty pgrep checks 30 s apart. Run 1 went from 11:00:51 to 11:02:00, 69 s, exit code 0, with load averages 2.47 3.90 3.84 at start. Run 2 went from 11:03:10 to 11:04:14, 64 s, exit code 0, with load averages 5.18 5.53 4.61 at start. Both runs cover scripts, site (1954 tests), pipeline, api, and each package.

## AT-27: The hook passes under the load of two commits

App: root
Then: both hooks pass, and no site test fails on its 5 s timeout.
Files: `evidence/AT-27/setup.txt`, `evidence/AT-27/quiet-run1.txt`, `evidence/AT-27/hook-wt-a-run1.txt`, `evidence/AT-27/hook-wt-b-run1.txt`, `evidence/AT-27/quiet-run2.txt`, `evidence/AT-27/hook-wt-a-run2.txt`, `evidence/AT-27/hook-wt-b-run2.txt`, `evidence/AT-27/quiet-run3.txt`, `evidence/AT-27/run3-hook-setup.txt`, `evidence/AT-27/hook-wt-a-run3.txt`, `evidence/AT-27/hook-wt-b-run3.txt`, `evidence/AT-27/cleanup.txt`
Observation: In three paired runs the two `git commit` calls start at the same second (11:05:46, 11:08:26, 11:10:54), and each hook prints "Passed" with exit code 0 in 73 to 74 s. Runs 1 and 2 show only that line, because prek hides the output of a passed hook. Run 3 uses the repo hook config plus `verbose: true`; there each worktree runs `bun test --isolate --parallel=3` with "1954 pass, 0 fail", and a search of both run 3 outputs for "timed out", "timeout", or "(fail)" counts 0.

## AT-28: The whole CI run takes 360 s or less

App: root
Then: the median time from the start of the first job to the end of the last job is 360 s or less, against the baseline of 754 s. No job takes more than 360 s.
Files: `evidence/AT-28/ci-times.txt`, `evidence/AT-28/head-diff.txt`
Observation: Runs 44873662117, 44874144251, and 44874592510 on 4d5f4d13 succeed; they are `workflow_dispatch` runs, not pushes. The start of the first job to the end of the last job takes 347, 311, and 311 s, median 311 s; createdAt to updatedAt takes 351, 315, and 315 s, median 315 s. The slowest job is 342 s, site-browser (7) of run 44873662117. From 4d5f4d13 to 2108f8bc only 4 ticket files change.

## AT-29: The shard counts come from measured times

App: root
Then: the unit suite and Playwright each run in a matrix of `n` shards, and the evidence gives the time with `n` shards and with fewer shards. The serial Playwright projects run with one worker.
Files: `evidence/AT-29/workflow-and-config.txt`, `evidence/AT-29/shard-times.txt`, `evidence/AT-29/ci-workers.txt`
Observation: `check.yml` has `site-unit` with `shard: [1]` and `site-browser` with `shard: [1, 2, 3, 4, 5, 6, 7]`. Ticket 15 gives unit shard times for 1 to 5 shards and picks 1 shard: with 4 workers that is 46.7 s, against 33.8 s with 2 shards. Ticket 16 gives a model for 1 to 5 shards, the CI times with 5 and 6 shards, and the model for 6 and 7 shards with the chosen 7. In `playwright.config.ts`, `floor-timing` and `eggs` have `workers: 1`, and the CI log of site-browser (7) shows "Running 1 test using 1 worker, shard 7 of 7".

## AT-30: A small PR runs only the tests the diff can reach

App: root
Then: the unit job runs `bun test` with `--changed`, and the count of test files that run is less than the full count.
Files: `evidence/AT-30/run.txt`, `evidence/AT-30/lines.txt`, `evidence/AT-30/site-unit.log`
Observation: Draft PR #86 from the scratch branch `design-checks-speed-at30` into `design-checks-speed` changed one line of `packages/rankings/site/chapters/power-rankings.tsx` (commit 79396d75). Its `pull_request` run 44921047505 ran `bun test --isolate --parallel=4 --shard=1/1 --timings=bun-test-timings.json --changed=HEAD^1` in the `site-unit` job, and Bun printed "--changed: 5 changed files, running 1/203 test files" and "Ran 25 tests across 1 file". The PR was closed and its branch deleted after the run.

## AT-31: A change to the lock file runs the full suite

App: root
Then: the unit job runs the full suite with no `--changed`.
Files: `evidence/AT-31/run.txt`, `evidence/AT-31/lines.txt`, `evidence/AT-31/site-unit.log`
Observation: Draft PR #87 from the scratch branch `design-checks-speed-at31` into `design-checks-speed` added one blank line at the end of `pnpm-lock.yaml` and changed no other file (commit 3e0c2825). Its `pull_request` run 44921052646 ran `bun test --isolate --parallel=4 --shard=1/1 --timings=bun-test-timings.json` with no `--changed` in the `site-unit` job, printed "The run takes the full suite.", and printed "--shard=1/1: running 203/203 test files". The PR was closed and its branch deleted after the run.

## AT-32: A push runs the full suite

App: root
Then: the unit job runs the full suite with no `--changed`. The condition in the workflow gives a push to `main` the same full run.
Files: `evidence/AT-32/workflow.txt`, `evidence/AT-32/run.txt`
Observation: The `on:` block of `check.yml` has `push: branches: [main]`, `pull_request`, `workflow_dispatch`, and `workflow_call`, so a push to the Spec branch starts no run: the Spec branch has 0 push runs and 9 dispatch runs. `BUN_TEST_BASE` is `HEAD^1` only when `github.event_name == 'pull_request'`, else empty. The evidence run 44873662117 is a `workflow_dispatch` run, not a push run; its site-unit job shows `BUN_TEST_BASE:` empty, `bun test --isolate --parallel=4 --shard=1/1 --timings=bun-test-timings.json` with no `--changed`, "The run takes the full suite.", and "Ran 1954 tests across 203 files".

## AT-33: The pipeline runs in two jobs

App: root
Then: one job runs the parallel pipeline tests and another job runs the serial pipeline tests. Each one exits 0 in 360 s or less.
Files: `evidence/AT-33/pipeline-jobs.txt`, `evidence/AT-33/head-diff.txt`
Observation: Each of the 3 dispatch runs on 4d5f4d13 has two `pipeline-parallel` shard jobs that run `PYTEST_SHARD=<i>/2 ... pytest -q -n auto -m 'not live and not serial'` with "877 passed" each, and one `pipeline-serial` job that runs `pytest -q -p no:xdist -m 'serial and not live'` with "2 passed, 1764 deselected". All succeed. The parallel jobs take 259, 264, 197, 194, 233, and 268 s, and the serial job takes 43, 45, and 37 s.

## AT-34: Each CI job uses a free runner

App: root
Then: each job uses a standard GitHub runner, such as `ubuntu-latest`, and no larger runner or paid service.
Files: `evidence/AT-34/output.txt`
Observation: All 16 `runs-on` lines of the 7 workflows read `runs-on: ubuntu-latest`. A search for larger, self-hosted, macOS, Windows, or paid runner names exits 1 with no match.

## AT-35: ADR 0038 records the move to Bun

App: root
Then: the ADR says why the checks run on Bun and Oxlint and why pnpm stays, and the index lists it.
Files: `evidence/AT-35/output.txt`
Observation: ADR 0038 says that Vitest took 138 s of a 195 s `make check-fast`, that Bun runs the same tests 3 to 5 times faster and ships `bun check` and `bun fmt`, and that Oxlint runs the lint until `bun lint` leaves canary. It says pnpm stays because the move of the lock to `bun.lock` failed and Bun picked fresh versions. `docs/adr/README.md` line 42 lists 0038.

## AT-36: The move does not touch `bun install`

App: root
Then: no search finds a match, and each install step still runs `pnpm install`.
Files: `evidence/AT-36/output.txt`
Observation: The searches for `bun install`, `bun i`, and `bun add` in `Makefile`, `.github`, `.pre-commit-config.yaml`, and the site `package.json` files exit 1 with no match. The 4 install steps of the workflows each run `pnpm install --frozen-lockfile`: `check.yml` lines 94 and 136, `deploy-sites.yml` line 105, and `rerun.yml` line 94.

## AT-37: The landmines rules are not in the lint

App: root
Then: no file names `landmines`, `no-fixed-sleep`, `no-flake-masking`, or `no-unsignaled-poll`.
Files: `evidence/AT-37/output.txt`
Observation: The search for each of the four names in `.oxlintrc.json`, each `package.json`, and `packages/design/lint` exits 1 with no match. One search of all tracked files outside `.scratch` also exits 1.

## AT-38: The spacing scale keeps its names

App: site
Then: `--spacing-sp-0` to `--spacing-sp-6` exist with the same values as on `main`.
Files: `evidence/AT-38/output.txt`
Observation: Both branches have `--spacing-sp-0` to `--spacing-sp-6` at lines 72 to 78 with 2, 4, 8, 12, 16, 20, and 24 px. A diff of the two sets of lines without the indent is empty and exits 0; only the indent changes, from 4 to 2 spaces.

## AT-39: CI adds no `node_modules` cache

App: root
Then: no step caches a `node_modules` folder. The pnpm store cache of `setup-node` stays as on `main`.
Files: `evidence/AT-39/output.txt`
Observation: `git grep node_modules -- .github` exits 1. The 4 `setup-node` steps keep `cache: pnpm` with `cache-dependency-path: pnpm-lock.yaml`, as on `main`. The other caches are the Playwright browsers, the apt archives, and the `setup-uv` cache. The only cache lines that differ from `main` are the `setup-uv` `enable-cache: true` lines of the new `pipeline-serial` job.
