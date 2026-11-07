# Faster evidence: evidence

Spec: `.scratch/faster-evidence/PRD.md`. Acceptance tests: `.scratch/faster-evidence/ACCEPTANCE.md`.
Built from: `e91c3153`, on 2026-11-05. The agent gives no Test verdict. Brian gives one for each test.
Round time: 11 min for 26 site tests.

Each site test uses the one round of `pnpm --dir apps/site evidence site-redesign` in `evidence/AT-1/output.txt`, unless its entry names a different run. The runner wrote into `.scratch/site-redesign/evidence/`. The agent copied the named files here, then restored each site-redesign PNG and TXT. No site-redesign `steps.json` changed.

## AT-1: A full round in 15 minutes

App: site
Then: The runner writes the shots of each of those tests and prints a total of 15 min or less. `EVIDENCE.md` of this feature records the line `Round time: <N> min for <M> site tests.`, and names each skipped screenshot test with the reason, such as AT-2 with scripts off.
Files: `evidence/AT-1/output.txt`, `evidence/AT-1/steps-paths.txt`
Observation: The output prints the time of each of the 26 tests and `Total: 26 tests of site-redesign in 662.5 s`, which is 11 min. `time` shows `11:04.15 total`, and the `Round time` line is above.

The skipped site-redesign screenshot tests, each with its reason:

- AT-1: it needs a page with no stored theme choice and a screen recording. The runner always sets `cpc.theme`.
- AT-2: scripts off.
- AT-7: a screen recording of the motion.
- AT-8: a screen recording with reduced motion on.
- AT-21: a screen recording of the sheet as it closes three ways.
- AT-26: the error state needs an API that fails. No verb makes the API fail.
- AT-36: the font files blocked, with the network log.
- AT-39: the system setting light. The runner always sets `cpc.theme`.

The site-redesign tests AT-13, AT-23, AT-34, AT-35, AT-37, AT-40, and AT-41 ask for no screenshot.

## AT-2: The light shot is light

App: site
Then: `1280-light.png` shows the light set, with a light background. `1280-dark.png` shows the dark set.
Files: `evidence/AT-2/steps.json`, `evidence/AT-2/1280-light.png`, `evidence/AT-2/1280-dark.png`
Observation: The files come from site-redesign AT-14, whose `steps.json` holds only `route: "/"`. `1280-light.png` shows the CPC home page on a light gray page with white cards, and `1280-dark.png` shows it on a near-black page with dark cards.

## AT-3: A full-page shot shows each section

App: site
Then: The full-page shot at 375 px shows Standings, Next week, and the footer, each with its text. No section shows blank.
Files: `evidence/AT-3/steps.json`, `evidence/AT-3/output.txt`, `evidence/AT-3/375-light.png`, `evidence/AT-3/375-dark.png`
Observation: No site-redesign test has only the week 8 route, so a temp slug ran it and was then deleted. Each 375 x 6706 shot shows every chapter with text, including the Standings table, the Next week text and matchups, and the footer card "Previous Week 7".

## AT-4: A missing path shows the site 404

App: site
Then: Each shot shows the 404 page of the site: "ERROR // PAGE NOT FOUND", a big "404", and the buttons "Go to Week 8" and "Go Home". No shot shows a plain server 404 page.
Files: `evidence/AT-4/steps.json`, `evidence/AT-4/cpc-375-light.png`, `evidence/AT-4/cpc-375-dark.png`, `evidence/AT-4/cpc-768-light.png`, `evidence/AT-4/cpc-768-dark.png`, `evidence/AT-4/cpc-1280-light.png`, `evidence/AT-4/cpc-1280-dark.png`, `evidence/AT-4/norcal-375-light.png`, `evidence/AT-4/norcal-375-dark.png`, `evidence/AT-4/norcal-768-light.png`, `evidence/AT-4/norcal-768-dark.png`, `evidence/AT-4/norcal-1280-light.png`, `evidence/AT-4/norcal-1280-dark.png`
Observation: Each of the 12 shots shows the site 404 card with "ERROR // PAGE NOT FOUND", a big "404", "Go to Week 8", and "Go Home", inside the site shell. The committed `steps.json` of site-redesign AT-32 also sets `clients: ["cpc", "norcal"]`, so the shots cover both clients.

## AT-5: Named shots, a tap, and the URL

App: site
Then: The folder holds `before-<width>-<theme>.png` and `after-tap-<width>-<theme>.png` for each width and theme. Each `url-<width>-<theme>.txt` holds a URL that ends in `/2026/week-07/`. The `steps.json` sits beside the shots.
Files: `evidence/AT-5/file-list.txt`, `evidence/AT-5/steps.json`, `evidence/AT-5/url-1280-dark.txt`, `evidence/AT-5/before-1280-dark.png`, `evidence/AT-5/after-tap-1280-dark.png`
Observation: The run wrote 6 `before-*`, 6 `after-tap-*`, and 6 `url-*` files beside `steps.json`, and each URL is `http://127.0.0.1:4173/2026/week-07/`. `before-1280-dark.png` shows the open strip with WK 08 marked, and `after-tap-1280-dark.png` shows the week 7 page.

## AT-6: A narrowed list takes only its shots

App: site
Then: The folder holds 4 PNG files for each shot: 768 and 1280, each in light and dark. It holds no file with 375 in its name.
Files: `evidence/AT-6/file-list.txt`, `evidence/AT-6/steps.json`
Observation: The run wrote 16 PNG files: 4 for each of the shots `top` and `scrolled` of each client, at 768 and 1280 in light and dark, and none with 375. The folder also holds committed 375 files in `cpc/` and `norcal/` from the earlier site-redesign round, which the runner did not write.

## AT-7: Two clients, one build each

App: site
Then: The output shows one build of CPC and one build of NorCal for the whole run. Each file name starts with `cpc-` or `norcal-`, and each shot shows the brand of its client.
Files: `evidence/AT-7/build-lines.txt`, `evidence/AT-7/file-list.txt`, `evidence/AT-7/steps.json`, `evidence/AT-7/cpc-1280-dark.png`, `evidence/AT-7/norcal-1280-dark.png`
Observation: The test is site-redesign AT-6 "The brand of each client", and the round output holds only `build cpc: 4.7 s` and `build norcal: 4.2 s`. Each of the 12 new files starts with `cpc-` or `norcal-`, and the shots show "Cornerstone Fantasy Football League" with red accents, and "NorCal Apex 6" with orange accents.

## AT-8: Analyzer tests do not wait on the limit

App: both
Then: No request gets a 429, and the API log shows no request waits on the limit. Each shot shows a real verdict from the API.
Files: `evidence/AT-8/output-lines.txt`, `evidence/AT-8/api.log`, `evidence/AT-8/grep-429.txt`, `evidence/AT-8/AT-24-steps.json`, `evidence/AT-8/AT-25-steps.json`, `evidence/AT-8/AT-24-result-1280-dark.png`, `evidence/AT-8/AT-25-1280-dark.png`
Observation: AT-24 took 62.0 s and AT-25 took 86.9 s, and the API log of `make -C apps/api api-evidence` holds 112 status lines, each 200, with no 429. Both shots show a real verdict "No" for Bo Girds with the fairness text and each side, and the AT-25 shot holds three teams.

## AT-9: Production keeps 10

App: pipeline
Then: Requests 1 to 10 answer 200, and request 11 answers 429. `apps/api/fly.toml` does not set `CORNERSTONE_RATE_LIMIT_PER_MINUTE`.
Files: `evidence/AT-9/output.txt`, `evidence/AT-9/api.log`
Observation: With `make -C apps/api api` and the value unset, requests 1 to 10 answered 200 and request 11 answered 429. `grep -c CORNERSTONE_RATE_LIMIT_PER_MINUTE apps/api/fly.toml` printed `0`.

## AT-10: A bad step list stops before any shot

App: site
Then: The run stops before the first shot, with an error that names the path of the file and the step `tap`. No PNG is written.
Files: `evidence/AT-10/output.txt`, `evidence/AT-10/steps.json`
Observation: The run stopped with `.../tmp-fe-badstep/evidence/AT-10/steps.json: step 1 {"tap":"text=Week 7"}: unknown verb "tap"`, before any build or shot. The folder after the run held only `steps.json`, and the temp slug was then deleted.

## AT-11: Only the named tests run

App: site
Then: The output names AT-32 only, and only `evidence/AT-32/` gets new files.
Files: `evidence/AT-11/output.txt`
Observation: The output names only AT-32, once for each client, with `Total: 1 test of site-redesign in 33.4 s`. `git status --short` after the run lists only 12 new PNG files under `AT-32/`.

## AT-12: The guide teaches the runner

App: site
Then: The guide teaches `steps.json`, the one command, `make api-evidence` before an analyzer test, and the `Round time` line of `EVIDENCE.md`. Its `agent-browser` fallback sets light with `setItem('cpc.theme','light')` and scrolls before a full-page shot.
Files: `evidence/AT-12/diff.txt`
Observation: The diff adds the step list with its keys and verbs, the command `pnpm --dir apps/site evidence <slug>`, `make -C apps/api api-evidence` before an analyzer test, and the `Round time` line. The fallback sets light with `localStorage.setItem('cpc.theme','light')` and scrolls to the end and back before the `--full` shot.

## AT-13: The glossary has Evidence

App: site
Then: It holds the term **Evidence**: the files and the observation that show what the finished work does for one acceptance test. The term says it holds no Test verdict.
Files: `evidence/AT-13/diff.txt`
Observation: The diff adds **Evidence** after **Test verdict**: "The files and the observation that show what the finished work does for one acceptance test. It holds no Test verdict."

## AT-14: Out of scope: no change to cpc:review and no worktree per client

App: site
Then: `git diff main -- .claude/plugin/skills/review` is empty. `git worktree list` shows no worktree that the runner made.
Files: `evidence/AT-14/review-diff.txt`, `evidence/AT-14/worktree-before.txt`, `evidence/AT-14/worktree-after.txt`
Observation: The review diff is empty. The list after the round shows four new `midseason-report-fix-a` to `-d` worktrees, no `midseason-report-10` and `-12`, and a new head on `midseason-report`. Another session made these changes at the same time. No worktree has a client name or the runner's slug.
