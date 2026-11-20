# Design checks and speed: map

App: site.
Spec branch: `design-checks-speed`.
Source: `.handoff/design-system-and-speed.md` and the grill of 2026-11-20.

## DESTINATION

One spec. The hook and CI catch misuse of the design parts, each part has a "use it when" docstring, and each token names its role. Bun runs install, test, check, lint, and fmt, the CI `check` job takes 360 s or less, and `make check-fast` takes half its baseline time.

## DECISIONS SO FAR

- The swap to Bun is in the build: `bun install`, `bun test`, `bun check`, `bun lint`, and `bun fmt`. A research ticket settles how each one works. Brian, 2026-11-20. `decisions/01-research-bun-latest.md`.
- A gap in Bun gets the fastest tool in its place: `tsc` from TypeScript 7, Oxlint, or `oxfmt`. The research ticket records each gap. No gap blocks the spec. Brian, 2026-11-20.
- The speed targets: the CI `check` job goes from about 540 s to 360 s or less. A full `make check-fast` takes half the time of the baseline that ticket 02 measures. Brian, 2026-11-20.
- The code that fails a design check today gets a fix in this spec, with no allowlist. Each raw `<button>` moves to a wrapper of `ui/`. Each repeated arbitrary Tailwind value gets a role token. A true one-off keeps a one-line ignore comment with a reason. Brian, 2026-11-20.
- The "use it when / do not use it when" doc lives in the top docstring of each part file, as two fixed lines that a check can parse. The READMEs keep their "Knows" lists. Brian, 2026-11-20.
- The speed list: the Bun swap, a CI cache of `node_modules`, 4 shards of the unit suite in CI, diff-only tests on a PR with a full run when a config file or the lock file changes, and parallel steps in `make check-fast` with a cap for the hook. Brian, 2026-11-20.

## NOT YET SPECIFIED

- What does the latest Bun do for install with a workspace, test with `happy-dom` and the `vi.*` calls, shards, `--changed`, check, lint with a plugin API, and fmt? `decisions/01-research-bun-latest.md`.
- What are the baseline times of `make check-fast` and of each CI job, and what does `create_app` cost per API test? `decisions/02-research-baseline-times.md`.
- Which design rules ship, and which tool runs each one? `decisions/03-grill-design-rules.md`.
- What role name does each token get that is not a role now? `decisions/04-grill-token-roles.md`.

## OUT OF SCOPE

- The Python tools of the pipeline and the API, such as `pytest` and `ruff`. Bun does not run Python.
- The landmines spike. It stays a Quick Win in the queue, unless ticket 03 takes in its timing rules.
