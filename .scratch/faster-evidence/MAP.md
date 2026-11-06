# Faster evidence: map

App: both.
Spec branch: `faster-evidence`.

## DESTINATION

One spec makes the evidence stage of `cpc:implement` and `cpc:review` take one scripted run for each site test, not about 40 `agent-browser` calls. The goal: Brian waits less on the evidence than on the code, and a full round of site evidence takes 15 minutes or less, not 60 to 90.

The spec holds three parts:

1. A script `apps/site/scripts/evidence-shots.mjs`. One Playwright run takes a test id, a route, and an optional action, and saves 3 widths x 2 themes.
2. A fix to `.claude/plugin/skills/implement/evidence.md`. Light is `setItem('cpc.theme','light')`. A scroll pass comes before each full-page shot. The local server answers a missing path with `404.html`, as the Worker does.
3. A setting for the rate limit of the local API, for evidence runs only. The API stays real, so this is no mock.

## DECISIONS SO FAR

None.

## NOT YET SPECIFIED

- How does a test name its clicks and inputs before a shot? `decisions/01-grill-action-form.md`.
- What is the name and the guard of the rate limit setting? `decisions/02-spec-rate-limit-setting.md`.
- How do we measure the 15 minutes of a round? `decisions/03-spec-measure-round-time.md`.
- What does the glossary term "Evidence" say? `decisions/04-spec-evidence-term.md`.

## OUT OF SCOPE

- A split of the evidence by client into two worktrees. The script builds one client, shoots its tests, then builds the next, for about 1 minute per client. Only a parallel run of the clients needs the split, and that adds a port clash.
- A change to `cpc:review`. It already reuses `implement/evidence.md` and records new evidence only for the fixed tests.
- A prototype of the script. Brian checks the script output when he gives the test verdicts.
