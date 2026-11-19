# 04: What a smoke run drives

Map: `.scratch/trusted-green/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

A smoke run boots the site and the API and drives the flow that a change touches. Brian decides how `verify` picks the flows from a diff: a list of flows with paths and expected results, as the article suggests, or the routes the diff touches. Brian also decides if `verify` reuses the evidence runner (`apps/site/e2e/evidence.ts`) and `make -C apps/api api-evidence`, and which files go to the Judge.

## Decision

Brian accepted each recommendation on 2026-11-18.

1. **The flow list.** `.claude/skills/verify/flows.json` lists each flow: a name, the code paths it covers as globs, a route, its steps, and the expected result. The globs of the diff pick the flows. The agent may add steps for the change, but each picked flow always runs. A diff of the pipeline only picks no flow, because the differential rebuild covers it.
2. **One runner.** `verify` drives each flow with the evidence runner and its `steps.json` shape. The step list gains the verb `expect`: an assertion that a text or an element is visible. The spec flow may use `expect` in its evidence too.
3. **What fails a smoke run.** A step that finds no element, an `expect` that does not hold, a page error, a console error, an API response of 4xx or 5xx, or an overlap of two elements. A failed smoke run counts as a red check. It gets one fix round, then a stop.
4. **Real Claude calls.** No mock. The flow list marks each flow that calls Claude. A smoke run runs each such flow once, at one width.
5. **Viewports.** 390x660 iPhone WebKit and 1280x800 desktop, in the light theme, with the overlap assert. A flow marked as a layout change adds 810x980 and 1080x740 iPad. The evidence runner keeps its own defaults for acceptance tests.
6. **The Judge.** A red smoke run stops the flow before the Judge. A green smoke run writes its shots and log to `evidence/smoke/` in a spec, or names them in a `Smoke:` block of a quick file. The spec Judge may open them for any test. The quick Judge gets a third question for each item that touches the site or the API: "Does the smoke run show the changed flow at work?"

New fog: which flows the first flow list holds. Ticket 08.
