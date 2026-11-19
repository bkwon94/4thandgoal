# Trusted green: evidence

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests: `.scratch/trusted-green/ACCEPTANCE.md`.
Built from: `a6f88746`, on 2026-11-18. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Recorded at four commits of the Spec branch. AT-1 to AT-4, AT-12 to AT-16, AT-19 to AT-26, and AT-30 to AT-36 are from `62d6b0ef`. Of the files that those tests run, the later commits change only `scripts/rebuild.py`: commit `29f87983` puts back the read of the CLI source to find out if a base has the `facts` command, in place of a run of `cornerstone facts --help`. AT-17, AT-18, AT-27, and AT-28 are from `593295b2`. AT-29 is from `a6f88746`, after the fix of the animation wait of `openPage`. AT-5 to AT-11 are from `7f1a6441`. Each of those runs started its own site server and its own local API on free ports.
Round time: the Spec runs of AT-5, AT-6, AT-7, AT-9, AT-10, and AT-11 took 8 min 37 s, from 12:24:19 to 12:32:56. The AT-11 round took 29.8 s.

## AT-1: Both harnesses find the `verify` skill

App: root
Then: each list names `verify` once, and both resolve to the same `SKILL.md` file.
Files: `evidence/AT-1/codex-skills.txt`, `evidence/AT-1/claude-skill-list.txt`, `evidence/AT-1/claude-skills.txt`, `evidence/AT-1/links.txt`
Observation: The Codex prompt list names `verify` once (file `r38/verify/SKILL.md`). A fresh `claude -p` session at the worktree root names one skill `verify` in its list, and the project skill folder holds `.claude/skills/verify/SKILL.md`. The Codex link has mode 120000, and `realpath` of both paths and the inode of both `SKILL.md` files are the same.

## AT-2: A diff of the analyzer picks its flow

App: site
Then: the pick names the flow "Analyzer" and no other flow.
Files: `evidence/AT-2/diffstat.txt`, `evidence/AT-2/output.txt`
Observation: The diff changes `apps/site/src/app/_routes/analyzer/menu.ts` only. The pick prints one line: `Analyzer`.

## AT-3: A diff of the pipeline picks no flow

App: site
Then: the pick names no flow and says that the rebuild covers the change.
Files: `evidence/AT-3/diffstat.txt`, `evidence/AT-3/output.txt`
Observation: The diff changes `apps/pipeline/README.md` only. The pick prints: "No flow: the diff touches the pipeline only, and the base and head rebuild covers it."

## AT-4: A change to a shared part picks each flow

App: site
Then: the pick names all seven flows: Front door, Passphrase, Week report, Manager page, Analyzer, Power rankings, and Midseason report.
Files: `evidence/AT-4/diffstat.txt`, `evidence/AT-4/output.txt`
Observation: The diff changes `packages/design/site/lib/motion.ts` only. The pick prints seven lines: Front door, Passphrase, Week report, Manager page, Analyzer, Power rankings, Midseason report.

## AT-5: A green smoke run of cpc 2026 week 10

App: site
Then: the log shows each of the seven flows as passed, with shots at 390x660 in WebKit and 1280x800, in the light theme.
Files: `evidence/AT-5/command.txt`, `evidence/AT-5/exit.txt`, `evidence/AT-5/output-build-error.txt`, `evidence/AT-5/output.txt`, `evidence/AT-5/shots.txt`, `evidence/AT-5/smoke/analyzer/390-light.png`, `evidence/AT-5/smoke/api.log`, `evidence/AT-5/smoke/front-door/390-light.png`, `evidence/AT-5/smoke/manager-page/1080-light.png`, `evidence/AT-5/smoke/manager-page/1280-light.png`, `evidence/AT-5/smoke/manager-page/390-light.png`, `evidence/AT-5/smoke/manager-page/810-light.png`, `evidence/AT-5/smoke/midseason-report/1280-light.png`, `evidence/AT-5/smoke/midseason-report/390-light.png`, `evidence/AT-5/smoke/passphrase/1280-light.png`, `evidence/AT-5/smoke/passphrase/390-light.png`, `evidence/AT-5/smoke/power-rankings/1280-light.png`, `evidence/AT-5/smoke/power-rankings/390-light.png`, `evidence/AT-5/smoke/smoke.log`, `evidence/AT-5/smoke/week-report/1080-light.png`, `evidence/AT-5/smoke/week-report/1280-light.png`, `evidence/AT-5/smoke/week-report/390-light.png`, `evidence/AT-5/smoke/week-report/810-light.png`
Observation: The run at `7f1a6441` exits 0. It started its own site server on port 61556 and its own local API on port 61557 ("site http://127.0.0.1:61556, API http://127.0.0.1:61557"), and wrote the API log to `smoke/api.log`. `smoke/smoke.log` ends with "Smoke run: 7 flows, 7 passed, 0 failed". It has one `PASS` line for each flow and size: 390x660 webkit for each flow, 1280x800 chromium for Passphrase, Week report, Manager page, Power rankings, and Midseason report, and 810x980 and 1080x740 for the layout flows Week report and Manager page. Examples: "PASS Front door 390x660 webkit in 56.5 s", "PASS Analyzer 390x660 webkit in 32.5 s", "PASS Week report 1280x800 chromium in 3.5 s". Each shot file ends in `-light.png`. The Front door 390 shot shows the question "who has the best roster", the answer "As of today, Teehee has the best roster in the league", the line "Checked", and a "Power rankings" chip. The Week report 1280 shot shows the full week 10 page, with the title "Lil Fridge by 2.86" and the chapter rail on the left. The Analyzer 390 shot shows the read "Pass" for The Blue Tent. Front door and Analyzer call Claude, so each has a 390 shot only. `output-build-error.txt` holds a first try on ports 61504 and 61505. It stopped on the Next.js `SecurityFatalError` before any flow ran, and the run in `output.txt` followed it.

## AT-6: A failed `expect` fails the smoke run

App: site
Then: the run exits red, and the log names the flow "Week report" and the failed `expect`.
Files: `evidence/AT-6/command.txt`, `evidence/AT-6/exit.txt`, `evidence/AT-6/output-build-error.txt`, `evidence/AT-6/output.txt`, `evidence/AT-6/seed.txt`, `evidence/AT-6/smoke/api.log`, `evidence/AT-6/smoke/smoke.log`, `evidence/AT-6/smoke/week-report/fail-1080-light.png`, `evidence/AT-6/smoke/week-report/fail-1280-light.png`, `evidence/AT-6/smoke/week-report/fail-390-light.png`, `evidence/AT-6/smoke/week-report/fail-810-light.png`
Observation: The seed is a `--steps` file in the scratch folder, as `seed.txt` says: `{ "Week report": [{ "expect": "text=Week 99" }] }`. No tracked file changed. The run exits 1. It used site port 62156 and API port 62157, and wrote `smoke/api.log`. Each of the 4 `FAIL` lines of `smoke.log` names the flow and a size, for example `FAIL Week report 390x660 webkit: step 4 {"expect":"text=Week 99"}: the expect failed: "text=Week 99" is not visible after 5000 ms`. The log ends with "Smoke run: 1 flow, 0 passed, 1 failed". The fail shot at 390 shows the week 10 hero with the title "Lil Fridge by 2.86" and no "Week 99" text. `output-build-error.txt` holds a first try on ports 62141 and 62142 that stopped on the Next.js `SecurityFatalError`.

## AT-7: An API error fails the smoke run

App: site
Then: the run exits red, and the log names the failed request to the API.
Files: `evidence/AT-7/command.txt`, `evidence/AT-7/exit.txt`, `evidence/AT-7/output-build-error.txt`, `evidence/AT-7/output.txt`, `evidence/AT-7/smoke/analyzer/fail-390-light.png`, `evidence/AT-7/smoke/smoke.log`
Observation: The run used the option `--no-api` (`command.txt`). No API ran. A server held the free port 62262 and ended each connection. The site used port 62261. The run exits 1. `smoke.log` names the failed requests: `FAIL Analyzer 390x660 webkit: API error: GET http://127.0.0.1:62262/clients/cpc/teams?season=2026 failed: The network connection was lost.` and the same for `/clients/cpc/eggs/board`. It then shows the click on "Pick Your Team" that timed out: `locator.click: Timeout 120000ms exceeded`. The log ends with "Smoke run: 1 flow, 0 passed, 1 failed". The fail shot shows the Trade Analyzer page with the red line "The API did not answer. Try again." and a "Try Again" button. `output-build-error.txt` holds a first try on ports 62246 and 62247 that stopped on the Next.js `SecurityFatalError`.

## AT-8: An overlap fails the smoke run

App: site
Then: the run exits red, and the log names the two elements that overlap.
Files: `evidence/AT-8/command.txt`, `evidence/AT-8/exit.txt`, `evidence/AT-8/output-build-error.txt`, `evidence/AT-8/output.txt`, `evidence/AT-8/seed.diff`, `evidence/AT-8/seed.txt`, `evidence/AT-8/smoke/api.log`, `evidence/AT-8/smoke/smoke.log`, `evidence/AT-8/smoke/week-report/1080-light.png`, `evidence/AT-8/smoke/week-report/1280-light.png`, `evidence/AT-8/smoke/week-report/390-light.png`, `evidence/AT-8/smoke/week-report/810-light.png`, `evidence/AT-8/smoke/week-report/fail-1080-light.png`, `evidence/AT-8/smoke/week-report/fail-1280-light.png`, `evidence/AT-8/smoke/week-report/fail-390-light.png`, `evidence/AT-8/smoke/week-report/fail-810-light.png`
Observation: No step verb sets a style. The agent seeded one CSS rule, `[data-hero-slot="eyebrow"] { position: relative; top: 48px; }`, in `globals.css` of a scratch detached worktree of `7f1a6441`, as `seed.txt` and `seed.diff` say. The run ran there, so the Spec worktree has no tracked change. It ran at the same time as the AT-5 run of the Spec worktree, on its own ports: site 61692 and API 61693, with the log in `smoke/api.log`. The run exits 1. Each of the 4 `FAIL` lines of `smoke.log` reads `overlap: <h1> "Lil Fridge by 2.86" and <div> "Week 10 // Matchup of the Week"`. The log ends with "Smoke run: 1 flow, 0 passed, 1 failed". The fail shot at 1280 shows the eyebrow text drawn across the title "Lil Fridge by 2.86". `output-build-error.txt` holds a first try on ports 61576 and 61577 that stopped on the Next.js `SecurityFatalError`.

## AT-9: A layout flow adds the iPad sizes

App: site
Then: the Week report has shots at 390x660, 810x980, 1080x740, and 1280x800, and the Passphrase flow has shots at 390x660 and 1280x800 only.
Files: `evidence/AT-9/command.txt`, `evidence/AT-9/exit.txt`, `evidence/AT-9/output-build-error.txt`, `evidence/AT-9/output.txt`, `evidence/AT-9/shots.txt`, `evidence/AT-9/smoke/api.log`, `evidence/AT-9/smoke/passphrase/1280-light.png`, `evidence/AT-9/smoke/passphrase/390-light.png`, `evidence/AT-9/smoke/smoke.log`, `evidence/AT-9/smoke/week-report/1080-light.png`, `evidence/AT-9/smoke/week-report/1280-light.png`, `evidence/AT-9/smoke/week-report/390-light.png`, `evidence/AT-9/smoke/week-report/810-light.png`
Observation: The run exits 0. It used site port 62538 and API port 62539, with the log in `smoke/api.log`. `shots.txt` lists `390-light.png`, `810-light.png`, `1080-light.png`, and `1280-light.png` for week-report, and `390-light.png` and `1280-light.png` only for passphrase. `smoke.log` reads "PASS Week report 390x660 webkit", "PASS Week report 810x980 webkit", "PASS Week report 1080x740 webkit", "PASS Week report 1280x800 chromium", "PASS Passphrase 390x660 webkit", and "PASS Passphrase 1280x800 chromium", then "Smoke run: 2 flows, 2 passed, 0 failed". The Passphrase 390 shot shows the sheet "What is the league passphrase?" over a dimmed chat. The Week report 810 shot shows the week 10 page with the hero "Lil Fridge by 2.86". `output-build-error.txt` holds a first try on ports 62507 and 62508 that stopped on the Next.js `SecurityFatalError`.

## AT-10: A flow that calls Claude runs once

App: site
Then: the flow has shots at one width only, and the API log shows one grade call.
Files: `evidence/AT-10/api-grade-lines.txt`, `evidence/AT-10/command.txt`, `evidence/AT-10/exit.txt`, `evidence/AT-10/output-build-error.txt`, `evidence/AT-10/output.txt`, `evidence/AT-10/shots.txt`, `evidence/AT-10/smoke/analyzer/390-light.png`, `evidence/AT-10/smoke/api.log`, `evidence/AT-10/smoke/smoke.log`
Observation: The run exits 0. It used site port 62644 and API port 62645, with the log in `smoke/api.log`. `smoke.log` reads "PASS Analyzer 390x660 webkit in 18.1 s" and "Smoke run: 1 flow, 1 passed, 0 failed". `shots.txt` lists one shot, `smoke/analyzer/390-light.png`. It shows the read "Pass" for The Blue Tent. `api-grade-lines.txt` holds one `POST /clients/cpc/analyze HTTP/1.1" 200 OK`, with the line `Press of analyze for cpc: time=3.2s cost=$0.0000 claude_calls=0`. The `claude_calls=0` line means a saved grade in the result cache of this worktree, `<repo>/data/cache/results/cpc/`, answered the call. No Claude call ran. `output-build-error.txt` holds a first try on ports 62626 and 62627 that stopped on the Next.js `SecurityFatalError`.

## AT-11: The acceptance defaults of the evidence runner stay

App: site
Then: the round takes shots at 375, 768, and 1280 px, each in the light theme and the dark theme.
Files: `evidence/AT-11/1280-dark.png`, `evidence/AT-11/1280-light.png`, `evidence/AT-11/375-dark.png`, `evidence/AT-11/375-light.png`, `evidence/AT-11/768-dark.png`, `evidence/AT-11/768-light.png`, `evidence/AT-11/command.txt`, `evidence/AT-11/exit.txt`, `evidence/AT-11/output-build-error.txt`, `evidence/AT-11/output.txt`, `evidence/AT-11/shots.txt`, `evidence/AT-11/steps.json`
Observation: `steps.json` holds only the route `/2026/week-10/`. The run exits 0. `output.txt` prints "site http://127.0.0.1:62742, API http://127.0.0.1:62743, API log /var/folders/bz/st0_2tgs66q70nd0m5w3gq3c0000gq/T/evidence-api-N2VEUa/api.log". It then prints "AT-11 /2026/week-10/ cpc: 6 shots in 24.4 s" and "Total: 1 test of trusted-green in 29.8 s". `shots.txt` lists `375-light.png`, `375-dark.png`, `768-light.png`, `768-dark.png`, `1280-light.png`, and `1280-dark.png`. The 375 dark shot shows the week 10 page in a narrow column on a dark page. The 1280 light shot shows the week 10 page on a pale page with the chapter rail on the left. `output-build-error.txt` holds a first try on ports 62723 and 62724 that stopped on the Next.js `SecurityFatalError`.

## AT-12: `4ag:implement` runs a smoke run before the Judge

App: root
Then: the test passes, and the skill names a smoke run after the last ticket, the smoke folder of the evidence, and a stop on a red run before the Judge.
Files: `evidence/AT-12/output.txt`, `evidence/AT-12/lines.txt`
Observation: The unittest run of `scripts/test_skill_smoke.py` lists 12 tests, each `ok`, and exits 0. The lines show the smoke run after the last ticket (SKILL.md 39, 49) and the folder `evidence/smoke/` and the stop before the Judge (evidence.md 33-43).

## AT-13: The quick Judge gets a third question

App: root
Then: the test passes, `format.md` names the `Smoke:` block and the `Rebuild:` block, and the Judge brief holds "Does the smoke run show the changed flow at work?"
Files: `evidence/AT-13/output.txt`, `evidence/AT-13/lines.txt`
Observation: The same unittest run lists 12 tests, each `ok`, and exits 0. `format.md` has `Smoke:` at line 31 and `Rebuild:` at line 35. `judge.md` line 62 holds the third question.

## AT-14: The re-run job passes a true quick file

App: root
Then: the script exits 0 and names each item as held.
Files: `evidence/AT-14/output.txt`, `evidence/AT-14/quick-file.md`
Observation: In a temp git repo, the Red command exits 1 with `AssertionError: add(2, 2) gave 5` and the Green command exits 0. The script prints `item 1 (add gives the sum): held`, `Each item held.`, and exits 0. Item 2 is text only and the script skips it.

## AT-15: A fake red fails the re-run job

App: root
Then: the script exits 1 and names the item whose red commit did not fail.
Files: `evidence/AT-15/output.txt`, `evidence/AT-15/quick-file.md`
Observation: The Red line names the fix commit. The Red command exits 0 there. The script prints `FAIL item 1 (add gives the sum): the Red command passed at ...`, and exits 1.

## AT-16: A missing failure line fails the re-run job

App: root
Then: the script exits 1 and names the item and the missing line.
Files: `evidence/AT-16/output.txt`, `evidence/AT-16/quick-file.md`
Observation: The Red block quotes `AssertionError: add(2, 2) gave 7 apples`. The command prints `AssertionError: add(2, 2) gave 5`. The script prints `FAIL item 1 (add gives the sum): the Red output has no line ...` and exits 1.

## AT-17: A PR with no quick file passes the re-run job

App: root
Then: the job passes with the note "no quick file".
Files: `evidence/AT-17/job-log.txt`
Observation: The log is of run 44451360322 of `rerun.yml` on PR #70 at head `593295b2`, with conclusion success. Lines 347 and 348 print "Note: main has no scripts/rerun.py or scripts/scope.py yet, so this run checks no loop and passes." and then "no quick file".

## AT-18: The re-run job reads its script from `main`

App: root
Then: the step checks out the script from the default branch, and the log shows a pass with a note while `main` has no re-run script.
Files: `evidence/AT-18/workflow-lines.txt`, `evidence/AT-18/job-log.txt`
Observation: Lines 35 to 43 of `rerun.yml` check out `ref: ${{ github.event.repository.default_branch }}` into `rerun-main` with a sparse checkout of `scripts/rerun.py` and `scripts/scope.py`. The job log shows that step with `ref: main`, then the note "main has no scripts/rerun.py or scripts/scope.py yet, so this run checks no loop and passes", and the run of PR #70 at `593295b2` ends in success.

## AT-19: A build saves its inputs before the first Claude call

App: pipeline
Then: the build stops at the first Claude call, and the week folder holds a new nflverse extract, a slow-source file, and a news file.
Files: `evidence/AT-19/output.txt`, `evidence/AT-19/sizes.txt`
Observation: With only PATH and HOME set, `build --no-fetch` of cpc week 10 fetches nflverse and Sleeper news, then stops in `anthropic` `messages.parse` with "Could not resolve authentication method" and exit 1. The week folder then holds `raw/nflverse.json` (682864 bytes), `raw/slow_sources.json` (527161 bytes), and `raw/news.json` (5756 bytes), all untracked and timed 22:01 local, just after the run start.

## AT-20: A facts-only rebuild gives the same facts each time

App: pipeline
Then: both runs give the same sha256 of `facts.json`, and neither run makes a network call.
Files: `evidence/AT-20/run-1.txt`, `evidence/AT-20/run-2.txt`, `evidence/AT-20/no-network.sb`, `evidence/AT-20/network-probe.txt`
Observation: Both runs under `env -i` and the `(deny network*)` sandbox exit 0 and give sha256 `92c5d4bbcc577e533f342783aecf1344b99665d29278330636130b58070102bf`, and each logs "facts-only rebuild of week 10 reads .../raw/nflverse.json, .../raw/slow_sources.json, .../raw/news.json, the clock of verify.json, and the research of facts.json". A `curl` under the same profile fails with "Could not resolve host" and exit 6.

## AT-21: No change of code gives no diff

App: pipeline
Then: the output reports 0 diffs for each client.
Files: `evidence/AT-21/output.txt`
Observation: With two checkouts of 62d6b0ef as base and head, the output shows "0 diffs" for `facts.json`, `page.json`, `topics.json`, and `waiver.json` of both cpc and norcal week 10. The last line is "rebuild diff: 0 diffs, 0 listed, 0 not listed, 0 listed but not changed", and the exit code is 0.

## AT-22: An unlisted change of output fails

App: pipeline
Then: the run exits 1, and the output names cpc, `waiver.json`, and the JSON path of the score.
Files: `evidence/AT-22/seed.diff`, `evidence/AT-22/output.txt`
Observation: The seed adds 0.01 to `best_adds[0].board_score` in `render.py` for cpc only. The output shows "changed but not listed: cpc waiver.json $.buckets.best_adds[0].board_score", norcal has 0 diffs, and the exit code is 1.

## AT-23: A listed change of output passes

App: pipeline
Then: the run exits 0 and prints the listed diff with its reason.
Files: `evidence/AT-23/REBUILD.md`, `evidence/AT-23/output.txt`
Observation: With the seed of AT-22 and `--approved REBUILD.md`, the output shows "$.buckets.best_adds[0].board_score  (approved: The seeded change adds 0.01 to the top waiver score of cpc.)". The last line is "rebuild diff: 1 diffs, 1 listed, 0 not listed, 0 listed but not changed", and the exit code is 0.

## AT-24: A listed path that does not change fails

App: pipeline
Then: the run exits 1, and the output names the extra path as listed but not changed.
Files: `evidence/AT-24/REBUILD.md`, `evidence/AT-24/output.txt`
Observation: The list adds "- norcal page.json $.week: ..." to the list of AT-23, and `$.week` exists in norcal `page.json` with the value 10. The output shows "listed but not changed: norcal page.json $.week" and "1 listed but not changed", and the exit code is 1.

## AT-25: The first PR runs the render diff only

App: pipeline
Then: the run diffs the render only, prints "render only", and exits 0 when the render has no diff.
Files: `evidence/AT-25/output.txt`, `evidence/AT-25/base.txt`
Observation: The base is a checkout of `main` at b9231a41, which is the merge base of the Spec branch and has no `scripts/rebuild.py`. The output shows "render only: the base has no facts-only rebuild", lists only `page.json`, `topics.json`, and `waiver.json` with 0 diffs for both clients, and the exit code is 0.

## AT-26: The render diff is fast

App: pipeline
Then: the output reports 0 diffs, and the run takes under 60 s in total.
Files: `evidence/AT-26/output.txt`, `evidence/AT-26/render-diff.sh`
Observation: The script runs `page-json` of cpc and norcal week 10 in a base and a head checkout of 62d6b0ef with the saved facts, then diffs the render files by JSON path. The output shows "0 diffs" for each of the six files, and `time` shows "real 0m7.017s".

## AT-27: Eight property tests pass

App: pipeline
Then: the output lists eight properties as passed: score range and weight sum, letter order, thin depth, league scale, roster ranks, position ranks, star ranks, and handcuff value.
Files: `evidence/AT-27/managers.txt`, `evidence/AT-27/league.txt`, `evidence/AT-27/analyzer.txt`
Observation: The run is in a fresh detached worktree of 593295b2, after `uv sync --all-packages`. `test_properties_grade.py` shows each of 8 tests as passed, with the summary "8 passed": weights sum to 100, score in 0 to 100, letter order, letter is A to D, thin depth, league scale, roster ranks, and position ranks. The star-rank file and the handcuff-value file each show 1 test as passed, with the summary "1 passed", and each of the three files ends with exit 0.

## AT-28: A property test catches a seeded bug

App: pipeline
Then: the test fails, and the output shows a counterexample with two scores and their letters.
Files: `evidence/AT-28/seed.diff`, `evidence/AT-28/output.txt`
Observation: In a fresh detached worktree of 593295b2, the agent deleted each `.hypothesis` folder, then seeded `if score == 80: return "B"` in `grade_letter`. The letter-order test ends with "1 failed" and exit 1 and the line "AssertionError: score 79.0 gives A and score 80.0 gives B", with the counterexample `low=79.0, step=1.0` under "Failing explicit example". The agent then restored `grade.py` and removed the worktree.

## AT-29: CI runs grade-bar

App: root
Then: the log shows the grade-bar project as passed in the norcal pass, and the job ends in under 25 min.
Files: `evidence/AT-29/job-log-lines.txt`, `evidence/AT-29/job-time.txt`, `evidence/AT-29/job-log-full.txt`
Observation: The job `site-browser` of `Check` run 44456293426 on PR #70 at head `a6f88746` shows, after `==> site check:floor: norcal`, a second `==> site build: norcal` and then `==> site check:grade-bar-export: norcal`, with three `[grade-bar]` tests marked ✓ and "3 passed (2.6s)". `job-time.txt` shows the conclusion success, from 04:08:58Z to 04:19:45Z, which is 10 min 47 s.

## AT-30: A retry setting fails the rule test

App: root
Then: the rule test fails on the seeded copy and names the file, and it passes on the clean config.
Files: `evidence/AT-30/seed.diff`, `evidence/AT-30/output.txt`
Observation: On the scratch copy with `retries: 1`, `scripts/retry_rule.py` prints `apps/site/playwright.config.ts sets a Playwright retries value above 0` and exits 1. On the clean copy and on the clean Spec worktree root, it prints nothing and exits 0.

## AT-31: `AGENTS.md` states the flaky-test rule

App: root
Then: it says to fix the cause of a flaky test or to delete it with the reason in the commit, and that a second run is never the fix.
Files: `evidence/AT-31/lines.txt`
Observation: `AGENTS.md` lines 83-84 read: "A flaky test gets a fix of its cause, or a delete with the reason in the commit. A second run is never the fix." Line 84 adds a no-retry rule.

## AT-32: A PR of records only skips the heavy checks

App: root
Then: the script prints "records only", and it selects no smoke run, no re-run, and no rebuild.
Files: `evidence/AT-32/commit.txt`, `evidence/AT-32/output.txt`
Observation: `scripts/scope.py c9b6282c^ c9b6282c` prints `records only` and `selects: none`, and exits 0. The commit changes 9 files under `.scratch/` and `GLOSSARY.md`.

## AT-33: ADR 0037 records the rule

App: root
Then: it states that each PR that changes code carries a smoke run, a re-run of its loop, and a base and head rebuild.
Files: `evidence/AT-33/lines.txt`
Observation: `docs/adr/0037-each-pr-of-code-carries-a-smoke-run-a-rerun-and-a-rebuild.md` line 4 says each PR that changes code carries three checks. Lines 9-11 list the smoke run, the re-run of the loop, and the base and head rebuild.

## AT-34: Out of scope: the flow list has no egg board

App: site
Then: no flow names the route of the egg board.
Files: `evidence/AT-34/routes.txt`
Observation: The seven flow routes are `/`, `/`, `{latest-week}`, `/{season}/managers/`, `/analyze/`, `/rankings/`, `/midseason/{season}/`. None is `/eggs/`, and `grep -i egg` of `flows.json` finds no line.

## AT-35: Out of scope: no Proof trailer and no commit gate

App: root
Then: the diff adds no trailer check and no commit gate.
Files: `evidence/AT-35/output.txt`
Observation: The diff of `.pre-commit-config.yaml` is empty (`prek.toml` does not exist). The diff of `Makefile` and `scripts/changed_apps.py` is empty. The diff of `scripts/` adds 9 files, which are scope, rerun, rebuild, retry_rule, and their tests, and a grep of that diff for trailer, Proof, or commit-msg finds nothing.

## AT-36: Out of scope: no Claude in the rebuild or the re-run

App: root
Then: neither workflow names `ANTHROPIC_API_KEY` or `TYPESAFE_API_KEY`.
Files: `evidence/AT-36/output.txt`
Observation: `grep` for both key names in `rebuild.yml` and `rerun.yml` prints nothing and exits 1. Each file has 0 lines with `secrets.`.
