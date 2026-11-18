---
name: verify
description: Boot the site and the local API of this repo, and drive each flow of the flow list in a smoke run, the way a person uses the app. Use before the Judge of a spec or a quick run, or when Brian asks to see that a change works in the running app.
argument-hint: '[<flow name> ...]'
---

# Verify

A smoke run drives the flows of the site through the evidence runner, in WebKit at 390x660 and in Chromium at 1280x800, in the light theme. It calls the real local API. A green run shows that the change works in the running app. A red run is a red check: one fix round, then a stop.

The flow list is `flows.json` beside this file. Each flow has a name, the globs of the code it covers, a route, its steps in the step-list shape of the evidence runner, and its expected results. The route `{latest-week}` opens the latest published week of the client.

## Site

Run each command at the root of the worktree. Put Node 24 or later first on PATH.

1. Start the local API in its evidence mode in the background: `make -C apps/api api-evidence`.
2. Run the smoke run: `pnpm --dir apps/site smoke --out <smoke folder> [<flow name> ...]`.
3. Read the last line of the log. "Smoke run: N flows, N passed, 0 failed" is a green run.
4. Stop the local API.

The smoke run builds the export of the client against the local API, serves it on port 4173, and runs each flow at each size. With no flow name, it runs each flow of the list. Add `--client <slug>` for a client other than `cpc`.

The smoke folder gets `smoke.log` and one folder of shots per flow. A shot is `<width>-light.png`, or `<shot name>-<width>-light.png` for a `shot` step. A failed flow also gets `fail-<width>-light.png`, a shot of the page as it failed.

A flow fails on each of these causes. Each line of the log names the flow, the size, and the cause:

- A step that finds no element in 10 s.
- An `expect` step whose element is not visible in 5 s.
- A page error or a console error.
- An API response of 4xx or 5xx, or a failed request to the API.
- An overlap of two visible texts. The log names the two elements.

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
