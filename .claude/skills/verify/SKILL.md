---
name: verify
description: Boot the site and its own local API of this repo, and drive each flow of the flow list in a smoke run, the way a person uses the app. Use before the Judge of a spec or a quick run, or when Brian asks to see that a change works in the running app.
argument-hint: '[<flow name> ...]'
---

# Verify

A smoke run drives the flows of the site through the evidence runner, in WebKit at 390x660 and in Chromium at 1280x800, in the light theme. A layout flow adds the iPad sizes 810x980 and 1080x740 in WebKit. A flow that calls Claude runs once, in WebKit at 390x660, so a smoke run costs a few cents. It calls the real local API. A green run shows that the change works in the running app. A red run is a red check: one fix round, then a stop.

The flow list is `flows.json` beside this file. Each flow has a name, the globs of the code it covers, a route, its steps in the step-list shape of the evidence runner, its expected results, the flag `claude` for a flow that calls Claude, and the flag `layout` for a flow whose layout changes with the width. The route `{latest-week}` opens the latest published week of the client. In a route, `{season}` gives the season of that week.

The flow list holds seven flows: Front door, Passphrase, Week report, Manager page, Analyzer, Power rankings, and Midseason report. It holds no flow of the egg board, because the board writes to a live store.

## Pick the flows

The globs of the diff since the merge base pick the flows. Do not pick the flows by hand.

1. Run `pnpm --dir apps/site pick --base main`. Use the spec branch as the base for a ticket branch.
2. Read the output. It lists one flow name per line, or it says why it picks no flow.

A change to a shared part picks each flow. The shared parts are the design package, the league package, the shell and the lib of the site, the client build, the package files, the smoke run, and this skill. `SHARED_GLOBS` in `apps/site/scripts/flow-pick.mjs` lists them. A diff that matches no glob picks no flow. A diff of the pipeline only picks no flow, because the base and head rebuild covers it. To try the pick on some files with no diff, name the files after the options.

## Site

Run each command at the root of the worktree. Put Node 24 or later first on PATH.

1. Run the smoke run of the picked flows: `pnpm --dir apps/site smoke --out <smoke folder> <flow name> ...`.
2. Read the last line of the log. "Smoke run: N flows, N passed, 0 failed" is a green run.

Do not start an API first. The smoke run starts its own site server and its own local API, each on a free port. The API is `make -C apps/api api-evidence` with that port, and it allows only the origin of that site server. The run builds the export of the client against that API, and runs each flow at each size. It stops the API and the server at the end, also after a failure. With no flow name, it runs each flow of the list. Add `--client <slug>` for a client other than `cpc`.

Two sessions in two worktrees can run a smoke run at the same time. A call of a page to a local server that is not the site or the API of its run fails the flow, with the cause `foreign local call`. One checkout runs one smoke run at a time, because each run builds into the one `apps/site/out/` and `apps/site/.next/` of that checkout.

The API runs in its own env, `.venv-api-evidence/` at the root, so its `uv run --exact` does not change the shared `.venv` under a check. The first run of a checkout installs that env, which takes a few more seconds.

To test the site with the local API stopped, add `--no-api`. The run then starts no API. Its build calls a free port that ends each connection at once.

The smoke folder gets `smoke.log`, `api.log`, the output of the API of the run, and one folder of shots per flow. A shot is `<width>-light.png`, or `<shot name>-<width>-light.png` for a `shot` step. A failed flow also gets `fail-<width>-light.png`, a shot of the page as it failed.

A step of a flow that calls Claude waits up to 120 s for its element, because one answer of Claude takes up to a minute. The local API needs `ANTHROPIC_API_KEY` and `TYPESAFE_API_KEY` in its env for these flows. The API of the run gets the env of the smoke run, so source `~/.secrets` in the same shell before `pnpm smoke`. Never print a key.

A flow fails on each of these causes. Each line of the log names the flow, the size, and the cause:

- A step that finds no element in 10 s.
- An `expect` step whose element is not visible in 5 s.
- A page error or a console error. The load log of a failed file of another host, such as a headshot of the CDN of Sleeper, does not count, because the site swaps the image for its default.
- An API response of 4xx or 5xx, or a failed request to the API.
- An overlap of two visible texts. The log names the two elements. A screen-reader text and the leading of one paragraph do not count.

### Add steps for the change

Do not drop a picked flow. To cover the change, add steps to a flow with `--steps <file>`. The file maps a flow name to the steps that go after the steps of the flow:

```json
{ "Week report": [{ "click": "a[href='#standings']" }, { "expect": "text=Standings" }] }
```

The verbs are `click`, `fill`, `scroll`, `wait`, `expect`, `shot`, and `url`, as in the evidence runner. `expect` takes a Playwright selector. For a text, write `text=<text>`.

## API

The smoke run does not test the API alone. A flow that calls the API fails on each API response of 4xx or 5xx, so the flows of the site cover the routes of the API that the site calls.

## Pipeline

A diff of the pipeline only needs no smoke run. The base and head rebuild covers it.
