# Design checks and speed: acceptance tests

Spec: `.scratch/design-checks-speed/PRD.md`.

The Test verdict: the Judge gives one for each test in `VERDICTS.md`. The Judge is a fresh subagent that reads only this file and the evidence. The PR merges when every test has PASS and Brian gives no FAIL in a PR comment (ADR 0026). The agent that builds the work records the evidence and gives no Test verdict.

App `root` names the root `Makefile`, the prek hook, and the CI workflows. "All site code" means `apps/site/src` and the `site` folder of each package under `packages/`. A "fixture file" is a file in the fixture folder of the lint rule test, outside the site code.

A timed run starts only when `pgrep -fl 'vitest|bun test|check-fast|pytest'` shows nothing on three checks 30 s apart. The laptop is the M2 Pro with 10 cores of the baseline.

## Tests

AT-1: The lint fails a raw button outside `ui/`
App: site
Stories: 1, 14
Given: a fixture file that renders a JSX `<button>` and is not in `packages/design/site/ui/`.
When: the agent runs the site lint command on the fixture file.
Then: the command exits non-zero, and the output names the element rule, the file, the line of the `<button>`, and the wrapper of `ui/` to use.
Evidence: the command and its full output, with the exit code.

AT-2: The lint fails a raw dialog outside `ui/`
App: site
Stories: 2
Given: a fixture file that renders a JSX `<dialog>` and is not in `packages/design/site/ui/`.
When: the agent runs the site lint command on the fixture file.
Then: the command exits non-zero, and the output names the element rule and the line of the `<dialog>`.
Evidence: the command and its full output, with the exit code.

AT-3: The lint fails a raw color literal
App: site
Stories: 3
Given: a fixture `.tsx` file with `style={{ color: "#ff0000" }}` on one line and `rgb(0 0 0)` in a class string on another line.
When: the agent runs the site lint command on the fixture file.
Then: the command exits non-zero and names the raw color rule once for each of the two lines.
Evidence: the command and its full output, with the exit code.

AT-4: The lint fails an arbitrary color value
App: site
Stories: 4
Given: a fixture file with the class `bg-[color-mix(in_srgb,var(--color-accent)_28%,var(--color-card))]`.
When: the agent runs the site lint command on the fixture file.
Then: the command exits non-zero and names the value rule and the line of the class.
Evidence: the command and its full output, with the exit code.

AT-5: The lint fails an arbitrary spacing value
App: site
Stories: 5
Given: a fixture file with the class `top-[calc(var(--spacing-touch)+2*var(--spacing-sp-2)+1px)]` in a `cn(...)` call.
When: the agent runs the site lint command on the fixture file.
Then: the command exits non-zero and names the value rule and the line of the class.
Evidence: the command and its full output, with the exit code.

AT-6: The lint passes variant, layout, and motion values
App: site
Stories: 7, 8, 9
Given: a fixture file with the classes `data-[state=open]:opacity-100`, `grid-cols-[1fr_auto]`, and `transition-[opacity,transform]`, and no other arbitrary value.
When: the agent runs the site lint command on the fixture file.
Then: the command exits 0.
Evidence: the command and its full output, with the exit code.

AT-7: A one-line ignore with a reason passes
App: site
Stories: 10
Given: the fixture file of AT-5, with a one-line ignore comment for the value rule and a reason after it, on the line above the class.
When: the agent runs the site lint command on the fixture file.
Then: the command exits 0.
Evidence: the fixture file, the command, and its full output, with the exit code.

AT-8: The lint fails a `@ui-sdk` import outside `ui/`
App: site
Stories: 12
Given: a fixture file outside `packages/design/site/ui/` with `import { Drawer } from "@ui-sdk/react"`.
When: the agent runs the site lint command on the fixture file.
Then: the command exits non-zero and names `no-restricted-imports` and the line of the import.
Evidence: the command and its full output, with the exit code.

AT-9: The `@ui-sdk` rule test is gone
App: site
Stories: 12
Given: the Spec branch after the last ticket.
When: the agent lists the tracked files and reads ADR 0035.
Then: `apps/site/src/ui-sdk-rule.test.ts` does not exist, and ADR 0035 names ADR 0038 as the new home of its rule.
Evidence: the output of `git ls-files apps/site/src | grep ui-sdk-rule`, and the changed lines of ADR 0035.

AT-10: The lint fails a part with no use lines
App: site
Stories: 17
Given: a fixture part file that exports a component and has a top docstring with no `Use it when:` line.
When: the agent runs the site lint command on the fixture file.
Then: the command exits non-zero and names the doc rule and the file.
Evidence: the command and its full output, with the exit code.

AT-11: The lint passes on all site code
App: site
Stories: 3, 4, 5, 11, 15, 16
Given: the Spec branch after the last ticket.
When: the agent runs the full site lint on all site code.
Then: the command exits 0 with no warning of a design rule.
Evidence: the command and its full output, with the exit code.

AT-12: No raw button and no hand copy of the band height remain
App: site
Stories: 1, 6
Given: the Spec branch after the last ticket.
When: the agent searches all site code outside `ui/` and outside test files for `<button` and for `calc(var(--spacing-touch)+2*var(--spacing-sp-2)+1px)`.
Then: neither search finds a match. Each of the 8 files that had a raw `<button>` on 2026-11-20 now uses a wrapper of `ui/`.
Evidence: the two search commands and their output, and the diff stat of the 8 files.

AT-13: The lint config holds no allowlist
App: site
Stories: 11
Given: the Spec branch after the last ticket.
When: the agent reads the Oxlint config and lists each ignore comment of a design rule in all site code.
Then: the config ignores only build output, test fixtures, and generated files, and names no source file of the site. Each ignore comment has a reason on the same line.
Evidence: the config file, and a search for the ignore comments with its output.

AT-14: The hook blocks a commit with a raw button
App: root
Stories: 1, 13
Given: a scratch branch from the Spec branch, with one site file changed to add a raw `<button>`.
When: the agent stages the file and runs `git commit`.
Then: the hook fails, the commit does not land, and the output names the element rule and the file.
Evidence: the command, the hook output, and `git log -1 --oneline` before and after.

AT-15: Each part file has its two use lines
App: site
Stories: 15, 16, 18
Given: the Spec branch after the last ticket.
When: the agent reads the top docstring of each component file of `packages/design/site/ui/` and `packages/design/site/parts/`.
Then: each one has a `Use it when:` line and a `Do not use it when:` line, and the README of each folder still has its "Knows" list.
Evidence: a table of each file with its two lines, and the "Knows" heading of each README.

AT-16: The chips look the same with the role tokens
App: site
Stories: 19, 20
Given: the front door of `cpc` with the 2026 week 10 data, with a site answer and its chips shown, on `main` and on the Spec branch.
When: the agent opens the front door and hovers one chip on a fine pointer.
Then: each chip at rest, chosen, and in hover has the same fill on both branches.
Evidence: screenshots of the chips on both branches at 375, 768, and 1280 px, each in the light theme and the dark theme, and the computed `background-color` of one chip in each state.

AT-17: The chips use the role tokens and no `dark:` fill
App: site
Stories: 19, 20
Given: the Spec branch after the last ticket.
When: the agent reads the chip classes of the front door site answer and the dark block of `apps/site/src/app/globals.css`.
Then: the chips use `--color-accent-wash`, `--color-accent-wash-chosen`, and `--color-accent-wash-hover`, with no `dark:bg-[` class. The dark block sets each of the three tokens.
Evidence: the chip class lines, and the token lines of the light block and the dark block.

AT-18: The glossary defines a role token and a scale step
App: root
Stories: 22
Given: the Spec branch after the last ticket.
When: the agent reads the Site language section of `GLOSSARY.md`.
Then: it has the terms **Role token** and **Scale step**, each with one meaning and an _Avoid_ line.
Evidence: the two entries, quoted.

AT-19: `bun test` runs the site suite, and Vitest is gone
App: site
Stories: 23, 28
Given: the Spec branch after the last ticket.
When: the agent runs the site unit tests through `make check-site-unit`.
Then: the run uses `bun test` and exits 0. No `package.json` of the workspace names `vitest`, and `apps/site/vitest.config.mts` does not exist.
Evidence: the command and the end of its output, a search of each `package.json` for `vitest`, and `git ls-files apps/site | grep vitest`.

AT-20: The test count did not drop
App: site
Stories: 24, 25
Given: the count of 1,775 tests in 183 files that Vitest ran on `main` at the base of the Spec branch.
When: the agent runs the full site suite with `bun test` on the Spec branch.
Then: the pass count equals 1,775, plus each test that a ticket added and minus each test that a ticket removed on purpose. Each added or removed test is named with its ticket. No test is skipped.
Evidence: the Vitest summary line on `main`, the `bun test` summary line on the Spec branch, and the list of added and removed tests.

AT-21: The tests use the native `bun:test` calls
App: site
Stories: 26
Given: the Spec branch after the last ticket.
When: the agent searches all site test files for `vi.` and for an import from `vitest`.
Then: neither search finds a match.
Evidence: the two search commands and their output.

AT-22: The stub helper restores each value
App: site
Stories: 27
Given: two tests in one file. The first test calls `stubGlobal` on `fetch` and `stubEnv` on one env name. The second test reads both.
When: the agent runs the file with `bun test`.
Then: the second test sees the real `fetch` and the real env value, and both tests pass.
Evidence: the test file, the command, and its output.

AT-23: `bun check` fails on a type error
App: site
Stories: 29, 30
Given: a scratch copy of the Spec branch with one site file changed to assign a number to a `string`.
When: the agent runs the site type check script.
Then: the script runs `next typegen` first, then `bun check`, and exits non-zero with the file and the line of the error.
Evidence: the command and its full output, with the exit code.

AT-24: The format check fails on a file out of format
App: site
Stories: 31, 32
Given: a scratch branch from the Spec branch, with one site file changed so that its class list is out of order and one line has the wrong indent.
When: the agent stages the file and runs `git commit`.
Then: the hook fails on the format check and names the file. The commit does not land.
Evidence: the command, the hook output, and `git log -1 --oneline` before and after.

AT-25: pnpm stays the installer with the same versions
App: root
Stories: 33
Given: the Spec branch after the last ticket.
When: the agent compares `pnpm-lock.yaml` on the Spec branch with `main`.
Then: no version of a package that `main` already locks has changed. The only new entries are the new tools of the spec, such as Oxlint and happy-dom. No `bun.lock` exists.
Evidence: the list of changed entries of the lock diff, and `git ls-files | grep bun.lock`.

AT-26: A full `make check-fast` takes 97 s or less
App: root
Stories: 34, 36, 47
Given: the Spec branch after the last ticket, on the quiet laptop of the baseline.
When: the agent runs a full `make check-fast` with no `BASE` and no `STAGED` two times.
Then: each run exits 0, and each wall-clock time is 97 s or less, against the baseline of 195 s.
Evidence: the command, the start and end time of each run, and the end of each output.

AT-27: The hook passes under the load of two commits
App: root
Stories: 35
Given: two worktrees of the Spec branch, each with one staged change to a site test file.
When: the agent runs `git commit` in both worktrees at the same time.
Then: both hooks pass, and no site test fails on its 5 s timeout.
Evidence: the two hook outputs, with their start times.

AT-28: The whole CI run takes 360 s or less
App: root
Stories: 37, 42, 44, 45, 47
Given: the Spec branch after the last ticket.
When: CI runs the full check on 3 pushes of the Spec branch.
Then: the median time from the start of the first job to the end of the last job is 360 s or less, against the baseline of 754 s. No job takes more than 360 s.
Evidence: the 3 run IDs, the time of each job of each run, and the median.

AT-29: The shard counts come from measured times
App: root
Stories: 38, 43
Given: the Spec branch after the last ticket.
When: the agent reads the CI workflow and the evidence of the ticket that set each shard count.
Then: the unit suite and Playwright each run in a matrix of `n` shards, and the evidence gives the time with `n` shards and with fewer shards. The serial Playwright projects run with one worker.
Evidence: the matrix lines of the workflow, the timed runs for each count, and the worker setting of the serial projects.

AT-30: A small PR runs only the tests the diff can reach
App: root
Stories: 39
Given: a PR from a scratch branch of the Spec branch that changes one file under `packages/rankings/site/`.
When: CI runs the unit check of the PR.
Then: the unit job runs `bun test` with `--changed`, and the count of test files that run is less than the full count.
Evidence: the run ID, and the lines of the job log with the command and the file count.

AT-31: A change to the lock file runs the full suite
App: root
Stories: 40
Given: a PR from a scratch branch of the Spec branch that changes `pnpm-lock.yaml` and no source file.
When: CI runs the unit check of the PR.
Then: the unit job runs the full suite with no `--changed`.
Evidence: the run ID, and the lines of the job log with the command and the file count.

AT-32: A push runs the full suite
App: root
Stories: 41
Given: a push to the Spec branch.
When: CI runs the unit check of the push.
Then: the unit job runs the full suite with no `--changed`. The condition in the workflow gives a push to `main` the same full run.
Evidence: the run ID, the lines of the job log with the command, and the condition lines of the workflow.

AT-33: The pipeline runs in two jobs
App: root
Stories: 44
Given: the Spec branch after the last ticket.
When: CI runs the full check on a push.
Then: one job runs the parallel pipeline tests and another job runs the serial pipeline tests. Each one exits 0 in 360 s or less.
Evidence: the run ID, and the name, the command, and the time of each pipeline job.

AT-34: Each CI job uses a free runner
App: root
Stories: 46
Given: the Spec branch after the last ticket.
When: the agent reads each `runs-on` line of the CI workflows.
Then: each job uses a standard GitHub runner, such as `ubuntu-latest`, and no larger runner or paid service.
Evidence: each `runs-on` line of the workflows.

AT-35: ADR 0038 records the move to Bun
App: root
Stories: 48
Given: the Spec branch after the last ticket.
When: the agent reads `docs/adr/0038-the-site-checks-run-on-bun-and-oxlint.md` and the ADR index.
Then: the ADR says why the checks run on Bun and Oxlint and why pnpm stays, and the index lists it.
Evidence: the ADR, quoted, and its row of the index.

AT-36: The move does not touch `bun install`
App: root
Stories: none
Given: the Spec branch after the last ticket.
When: the agent searches the root `Makefile`, the CI workflows, and the hook config for `bun install` and `bun i`.
Then: no search finds a match, and each install step still runs `pnpm install`.
Evidence: the search commands and their output, and each install line of the workflows.

AT-37: The landmines rules are not in the lint
App: root
Stories: none
Given: the Spec branch after the last ticket.
When: the agent reads the Oxlint config and each `package.json`.
Then: no file names `landmines`, `no-fixed-sleep`, `no-flake-masking`, or `no-unsignaled-poll`.
Evidence: a search for each name and its output.

AT-38: The spacing scale keeps its names
App: site
Stories: 21
Given: the Spec branch after the last ticket.
When: the agent compares the spacing tokens of `apps/site/src/app/globals.css` with `main`.
Then: `--spacing-sp-0` to `--spacing-sp-6` exist with the same values as on `main`.
Evidence: the token lines on both branches.

AT-39: CI adds no `node_modules` cache
App: root
Stories: none
Given: the Spec branch after the last ticket.
When: the agent reads the CI workflows.
Then: no step caches a `node_modules` folder. The pnpm store cache of `setup-node` stays as on `main`.
Evidence: each cache step of the workflows.

## Trace

Story 1: AT-1, AT-12, AT-14
Story 2: AT-2
Story 3: AT-3, AT-11
Story 4: AT-4, AT-11
Story 5: AT-5, AT-11
Story 6: AT-12
Story 7: AT-6
Story 8: AT-6
Story 9: AT-6
Story 10: AT-7
Story 11: AT-11, AT-13
Story 12: AT-8, AT-9
Story 13: AT-14
Story 14: AT-1
Story 15: AT-11, AT-15
Story 16: AT-11, AT-15
Story 17: AT-10
Story 18: AT-15
Story 19: AT-16, AT-17
Story 20: AT-16, AT-17
Story 21: AT-38
Story 22: AT-18
Story 23: AT-19
Story 24: AT-20
Story 25: AT-20
Story 26: AT-21
Story 27: AT-22
Story 28: AT-19
Story 29: AT-23
Story 30: AT-23
Story 31: AT-24
Story 32: AT-24
Story 33: AT-25
Story 34: AT-26
Story 35: AT-27
Story 36: AT-26
Story 37: AT-28
Story 38: AT-29
Story 39: AT-30
Story 40: AT-31
Story 41: AT-32
Story 42: AT-28
Story 43: AT-29
Story 44: AT-28, AT-33
Story 45: AT-28
Story 46: AT-34
Story 47: AT-26, AT-28
Story 48: AT-35
Out of scope "the move from pnpm to `bun install`": AT-25, AT-36
Out of scope "the landmines timing rules": AT-37
Out of scope "a rename of the spacing scale": AT-38
Out of scope "the `node_modules` cache in CI": AT-39
Out of scope "the Python tools of the pipeline and the API": no test. Reason: the spec changes no Python tool, and AT-33 shows the pipeline jobs still run `pytest`.
Out of scope "`bun lint`": no test. Reason: AT-11 shows the lint runs through Oxlint, and `bun lint` does not exist in a release build.

## Revisions

None yet.
