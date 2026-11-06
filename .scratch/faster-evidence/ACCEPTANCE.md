# Faster evidence: acceptance tests

Spec: `.scratch/faster-evidence/PRD.md`.

The Test verdict: only Brian gives one. He writes one PR comment on the Spec branch PR, with one line for each test: the id, then PASS, FAIL, or BLOCKED, then an optional note. The PR merges when every test has PASS (ADR 0020). An agent records the evidence and gives no Test verdict.

Every site test runs the runner on the real site-redesign tests, with `2026` week 8 and the export of both clients, CPC and NorCal. The runner writes into `.scratch/site-redesign/evidence/`. The evidence agent copies the files that a test names into `.scratch/faster-evidence/evidence/AT-<n>/`. The agent commits each new `steps.json` of site-redesign, because it is a real example for the next spec. Then the agent restores each PNG of site-redesign with `git restore`, so the PR holds no churn in binary files.

The round time counts the runner total only, as the runner prints it. The time of the agent to write the Observations depends on the model, so a script cannot check it.

## Tests

AT-1: A full round in 15 minutes
App: site
Stories: 1, 7, 10
Given: A `steps.json` for each of the 21 site-redesign tests that ask for screenshots, each narrowed to its Evidence line.
When: The agent runs `pnpm --dir apps/site evidence site-redesign` one time.
Then: The runner writes the shots of all 21 tests and prints a total of 15 min or less. `EVIDENCE.md` of this feature records the line `Round time: <N> min for 21 site tests.`
Evidence: The full command output with the time of each test and the total, the list of the 21 `steps.json` paths, and the `Round time` line.

AT-2: The light shot is light
App: site
Stories: 2
Given: A `steps.json` for the home page of CPC with only `route: "/"`.
When: The runner takes its shots.
Then: `1280-light.png` shows the light set, with a light background. `1280-dark.png` shows the dark set.
Evidence: `1280-light.png` and `1280-dark.png` of the home page.

AT-3: A full-page shot shows each section
App: site
Stories: 3
Given: A `steps.json` for the week 8 page of CPC with only `route: "/2026/week-08/"`.
When: The runner takes its shots.
Then: The full-page shot at 375 px shows Standings, Next week, and the footer, each with its text. No section shows blank.
Evidence: `375-light.png` and `375-dark.png` of the week 8 page.

AT-4: A missing path shows the site 404
App: site
Stories: 4, 12
Given: The `steps.json` of site-redesign AT-32 with only `route: "/2026/week-99/"`.
When: The runner takes its shots.
Then: Each shot shows the 404 page of the site: "ERROR // PAGE NOT FOUND", a big "404", and the buttons "Go to Week 8" and "Go Home". No shot shows a plain server 404 page.
Evidence: Shots of the 404 page at 375, 768, and 1280 px, each in the light theme and the dark theme, and the `steps.json`.

AT-5: Named shots, a tap, and the URL
App: site
Stories: 5, 13, 14
Given: The `steps.json` of site-redesign AT-10, with a `shot` named `before`, a `click` on week 7 in the strip, a `wait` for the URL, a `shot` named `after-tap`, and a `url` step.
When: The runner takes its shots.
Then: The folder holds `before-<width>-<theme>.png` and `after-tap-<width>-<theme>.png` for each width and theme. Each `url-<width>-<theme>.txt` holds a URL that ends in `/2026/week-07/`. The `steps.json` sits beside the shots.
Evidence: The file list of the folder, the `steps.json`, one `url-*.txt`, and `before-1280-dark.png` and `after-tap-1280-dark.png`.

AT-6: A narrowed list takes only its shots
App: site
Stories: 6
Given: The `steps.json` of site-redesign AT-9 with `widths: [768, 1280]`.
When: The runner takes its shots.
Then: The folder holds 4 PNG files for each shot: 768 and 1280, each in light and dark. It holds no file with 375 in its name.
Evidence: The file list of the folder and the `steps.json`.

AT-7: Two clients, one build each
App: site
Stories: 17
Given: A `steps.json` for the home page with `clients: ["cpc", "norcal"]`.
When: The runner takes its shots, in the same run as AT-1.
Then: The output shows one build of CPC and one build of NorCal for the whole run. Each file name starts with `cpc-` or `norcal-`, and each shot shows the brand of its client.
Evidence: The build lines of the command output, the file list, and `cpc-1280-dark.png` and `norcal-1280-dark.png`.

AT-8: Analyzer tests do not wait on the limit
App: both
Stories: 8, 15
Given: The local API runs with `make -C apps/api api-evidence`. The `steps.json` of site-redesign AT-20 and AT-21 each `wait` for the verdict before the shot.
When: The runner takes the shots of AT-20 and then AT-21, back to back.
Then: No request gets a 429. Each shot shows a real verdict from the API. Each test takes less than 61 s in the output.
Evidence: The output lines of AT-20 and AT-21 with their times, the API log with no 429, and one verdict shot of each test.

AT-9: Production keeps 10
App: pipeline
Stories: 9
Given: The local API runs with `make -C apps/api api`, with `CORNERSTONE_RATE_LIMIT_PER_MINUTE` unset.
When: The reader sends 11 requests to `/teams?season=2026` within one minute from one address.
Then: Requests 1 to 10 answer 200, and request 11 answers 429. `apps/api/fly.toml` does not set `CORNERSTONE_RATE_LIMIT_PER_MINUTE`.
Evidence: The command and the status code of each of the 11 requests, and the output of `grep -c CORNERSTONE_RATE_LIMIT_PER_MINUTE apps/api/fly.toml`.

AT-10: A bad step list stops before any shot
App: site
Stories: 11, 16
Given: A temp `steps.json` with the step `{"tap": "text=Week 7"}`.
When: The agent runs the runner on it.
Then: The run stops before the first shot, with an error that names the path of the file and the step `tap`. No PNG is written.
Evidence: The command output and the file list of the folder after the run.

AT-11: Only the named tests run
App: site
Stories: 19, 20
Given: The `steps.json` files of AT-1.
When: The agent runs `pnpm --dir apps/site evidence site-redesign AT-32`.
Then: The output names AT-32 only, and only `evidence/AT-32/` gets new files.
Evidence: The command output and `git status --short .scratch/site-redesign/evidence/` after the run.

AT-12: The guide teaches the runner
App: site
Stories: 18
Given: The branch `faster-evidence` after the last ticket.
When: The reader opens `.claude/plugin/skills/implement/evidence.md`.
Then: The guide teaches `steps.json`, the one command, `make api-evidence` before an analyzer test, and the `Round time` line of `EVIDENCE.md`. Its `agent-browser` fallback sets light with `setItem('cpc.theme','light')` and scrolls before a full-page shot.
Evidence: `git diff main -- .claude/plugin/skills/implement/evidence.md`.

AT-13: The glossary has Evidence
App: site
Stories: 21
Given: The branch `faster-evidence` after the last ticket.
When: The reader opens the Workflow section of `GLOSSARY.md`.
Then: It holds the term **Evidence**: the files and the observation that show what the finished work does for one acceptance test. The term says it holds no Test verdict.
Evidence: `git diff main -- GLOSSARY.md`.

AT-14: Out of scope: no change to cpc:review and no worktree per client
App: site
Stories: none
Given: The branch `faster-evidence` after the last ticket.
When: The reader compares it with `main`, and lists the worktrees after the AT-1 run.
Then: `git diff main -- .claude/plugin/skills/review` is empty. `git worktree list` shows no worktree that the runner made.
Evidence: The output of both commands.

## Trace

Story 1: AT-1
Story 2: AT-2
Story 3: AT-3
Story 4: AT-4
Story 5: AT-5
Story 6: AT-6
Story 7: AT-1
Story 8: AT-8
Story 9: AT-9
Story 10: AT-1
Story 11: AT-10
Story 12: AT-4
Story 13: AT-5
Story 14: AT-5
Story 15: AT-8
Story 16: AT-10
Story 17: AT-7
Story 18: AT-12
Story 19: AT-11
Story 20: AT-11
Story 21: AT-13
Out of scope "A split of the evidence by client into two worktrees": AT-14
Out of scope "A change to `cpc:review`": AT-14
Out of scope "A prototype of the runner": no test. Reason: a prototype leaves no trace in the branch.
Out of scope "A pipeline test": no test. Reason: the spec does not change the pipeline evidence, and AT-12 shows the guide.
Out of scope "The daily grade limit of the analyzer": no test. Reason: an agent cannot build it by mistake from this spec.

## Revisions

- 2026-11-05: AT-9 sends its requests to `/teams?season=2026`, not `/teams`. The route answers 422 with no season. Brian approved.
