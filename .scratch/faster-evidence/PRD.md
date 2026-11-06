# Faster evidence: one scripted run for the shots of each site test

Status: ready-for-agent
Date: 2026-11-05
Apps: both. The site gets an evidence runner on Playwright that reads a step list for each test and takes its shots. The pipeline side is the API: it reads its rate limit from the environment. The skill `cpc:implement` changes its evidence guide to use both.
Spec branch: `faster-evidence`.
Source: the map `.scratch/faster-evidence/MAP.md` and decision tickets 01 to 04. ADR 0020.
Tickets: none yet. `cpc:to-tickets` writes them.

## Problem Statement

Brian waits on the evidence more than on the code. On 2026-11-05 the site-redesign evidence took 60 to 90 minutes in round 0 and about 40 minutes in round 1. Each fix subagent took only 10 to 15 minutes.

The cause is the instrument. An agent drives `agent-browser` one call at a time: about 7 calls for each screenshot and about 40 for each site test. Each analyzer test also waits 61 s, because the local API allows 10 requests a minute.

The evidence guide has three faults too:

1. It sets light with `removeItem('cpc.theme')`. Dark is now the default, so that "light" shot is dark.
2. It takes a full-page shot with no scroll first. A section that reveals on scroll stays hidden in the shot.
3. It serves the export with `python3 -m http.server`. A missing path gets the server's own 404 page, not the `404.html` of the site that the Worker gives.

## Solution

The agent writes one small JSON step list for each site test. One command takes every shot of every site test of the feature. The agent then only looks at the shots and writes the Observations.

The light shot is light, the full-page shot shows each section, and a missing path shows the site's `404.html`. The analyzer tests run with no wait on the rate limit, against the real API. A full round of site evidence takes 15 minutes or less.

## User Stories

1. As Brian, I want a full round of site evidence in 15 minutes or less, so that I wait less on the evidence than on the code.
2. As Brian, I want the light shot to show the light theme, so that I can give a verdict on the light theme.
3. As Brian, I want each full-page shot to show every section, so that a section that reveals on scroll is not blank.
4. As Brian, I want a missing path to show the site's `404.html`, so that the evidence of a 404 test matches the Worker.
5. As Brian, I want to read the steps of a test beside its shots, so that I know what the agent did to get each shot.
6. As Brian, I want each test to give only the shots its Evidence line names, so that I look at no extra files before a verdict.
7. As Brian, I want the time of each round in `EVIDENCE.md`, so that I can see the 15 minutes hold.
8. As Brian, I want the API in an evidence run to stay real, so that the evidence uses real data with no mock (ADR 0020).
9. As Brian, I want production to keep the limit of 10 requests a minute, so that one browser cannot loop the API and run up the Claude bill.
10. As the evidence agent, I want one command for all the site tests of a feature, so that I make one call, not about 40 for each test.
11. As the evidence agent, I want a fixed set of six verbs, so that a step list cannot fail with a syntax error or a missed `await`.
12. As the evidence agent, I want a step list with only `route`, so that a test with no action needs no steps.
13. As the evidence agent, I want a `shot` verb with a name, so that one test can take a shot before and after a tap or a scroll.
14. As the evidence agent, I want a `url` verb, so that a test that checks the URL after a tap records it.
15. As the evidence agent, I want a `wait` verb, so that an analyzer test waits for the verdict before its shot.
16. As the evidence agent, I want a clear error that names the file and the step, so that I fix a wrong step list in one try.
17. As the evidence agent, I want the runner to build each client one time, so that two clients in one feature do not overwrite one build.
18. As the evidence agent, I want to use `agent-browser` for a test whose step no verb covers, so that one odd test does not block the round.
19. As the review agent, I want to run the same step list again after a fix, so that new evidence in review is one command.
20. As the review agent, I want to run only the tests I name, so that a review round records new evidence only for the fixed tests.
21. As a reader of the repo, I want "Evidence" in `GLOSSARY.md`, so that the word has one meaning in the skills and the tracker.

## Implementation Decisions

**The step list (decision 01).** A site test names its steps in `evidence/AT-<n>/steps.json`, beside its shots. `cpc:implement` writes it at the evidence stage and commits it with the shots. `cpc:review` runs the same file again after a fix. The file holds:

- `route`: the path under the site root, such as `/2026/week-08/`.
- `steps`: an optional list. Each step has one verb: `click` with a selector, `fill` with a selector and a value, `scroll` with a selector or `"end"`, `wait` with a selector, `"url"`, or a time in ms, `shot` with a name, and `url`. With no `shot` step, the runner takes one shot after the last step.
- `widths`: optional. The default is 375, 768, and 1280.
- `themes`: optional. The default is light and dark.
- `clients`: optional. The default is `cpc`.

The agent narrows `widths`, `themes`, and `clients` only to match the Evidence line of the test. A step with an unknown verb, or a file with an unknown key, stops the run before the first shot. The error names the file and the step.

**The shot names.** A shot is `<width>-<theme>.png`, as now. A named shot is `<name>-<width>-<theme>.png`. A test with more than one client puts the client first: `<client>-<name>-<width>-<theme>.png`. The `url` verb writes `url-<width>-<theme>.txt`.

**The runner.** The runner is a third Playwright project of the site, `evidence`, beside `rules` and `floor`. It is a project, not a plain script, so it reuses the floor's static server and its page opener with no copy. The map named a script; a project is the same command for the agent and keeps one server.

- One command runs it for a feature, such as `pnpm --dir apps/site evidence <slug>`. An optional list of test ids runs only those tests.
- For each client that a step list names, the runner builds the client one time, serves its export, and takes the shots of every test of that client. Then it builds the next client.
- The server answers a missing path with `404.html`, as the Worker does.
- The theme opens through the shipped boot script with `cpc.theme` set to `light` or `dark`. Light is `setItem('cpc.theme','light')`, never `removeItem`.
- Before each full-page shot, the runner scrolls the page to the end and back to the top, so each section that reveals on scroll is shown.
- The runner prints the time of each test and the total of the round.

**The evidence guide.** `.claude/plugin/skills/implement/evidence.md` teaches the step list and the one command for a site test. It keeps `agent-browser` as the fallback for a test whose step no verb covers, with the theme fix and the scroll pass. It tells the agent to start the local API with the evidence limit before an analyzer test.

**The rate limit setting (decision 02).** The API reads `CORNERSTONE_RATE_LIMIT_PER_MINUTE` from its settings. The default is 10. Fly never sets it, so production keeps 10. A new make target `api-evidence` runs the local API with a limit of 600. The API stays real: real Sleeper data, real grades, real Claude calls.

**The time of a round (decision 03).** The runner prints the time of each test and the total. `EVIDENCE.md` gets one line under `Built from`: `Round time: <N> min for <M> site tests.`

**The glossary term (decision 04).** `GLOSSARY.md` gets the term **Evidence** in the Workflow section: the files and the observation that show what the finished work does for one acceptance test. It holds no Test verdict. _Avoid_: proof, result, QA output.

## Testing Decisions

A good test checks what a reader sees: the files the runner writes and what they show, or the answer of the API. It does not check how the runner walks its steps.

The seams, from the highest down:

1. **The runner on a small real folder.** A test serves a small real folder with a `404.html` and a page that reveals a section on scroll. It runs step lists through the runner. It checks the file names, that the light shot is light, that a section that reveals on scroll is visible, that `url` writes the URL, that a missing path gives the `404.html`, and that a bad step list stops with an error that names the file and the step. Prior art: `floor-rules.spec.ts`, which proves the floor's server and page opener the same way.
2. **The API limit.** `test_api.py` already proves the limit of 10. A new test sets `CORNERSTONE_RATE_LIMIT_PER_MINUTE` and checks that the app allows that count, then answers 429. A second test checks the default of 10 with the value unset.
3. **The full round.** The acceptance tests run the runner on the real site-redesign tests of week 8, for both clients, and record the round time. This proves the 15 minutes on real work.

The step list itself has no unit test. Seam 1 covers each verb and each error.

## Out of Scope

- A split of the evidence by client into two worktrees. The runner builds one client, shoots its tests, then builds the next, for about 1 minute per client. Only a parallel run of the clients needs the split, and that adds a port clash.
- A change to `cpc:review`. It already reuses the evidence guide and records new evidence only for the fixed tests.
- A prototype of the runner. Brian checks the runner output when he gives the test verdicts.
- A pipeline test. Its evidence is one command and its output, and it is fast now.
- The daily grade limit of the analyzer. The evidence of the site redesign did not hit it. If an evidence run hits it, that is a later ticket.

## Further Notes

- The runner writes shots only. The agent still looks at each shot and writes each Observation. The test verdict stays with Brian (ADR 0020).
- Of the 41 site-redesign tests, 40 are site tests and 21 ask for screenshots. At 15 minutes, a round gives each site test about 22 s, so the build and the analyzer waits must stay small.
