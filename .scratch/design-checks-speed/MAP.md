# Design checks and speed: map

App: site.
Spec branch: `design-checks-speed`.
Source: `.handoff/design-system-and-speed.md` and the grill of 2026-11-20.

## DESTINATION

One spec. The hook and CI catch misuse of the design parts, each part has a "use it when" docstring, and each token names its role. Bun runs test, check, and fmt, Oxlint runs the lint, the CI `check` job takes 360 s or less, and `make check-fast` takes half its baseline time.

## DECISIONS SO FAR

- The swap to Bun is in the build: `bun test`, `bun check`, `bun lint`, and `bun fmt`. A research ticket settles how each one works. Brian, 2026-11-20. `decisions/01-research-bun-latest.md`.
- A gap in Bun gets the fastest tool in its place: `tsc` from TypeScript 7, Oxlint, or `oxfmt`. The research ticket records each gap. No gap blocks the spec. Brian, 2026-11-20.
- The speed targets: the CI `check` job goes from about 540 s to 360 s or less. A full `make check-fast` takes half the time of the baseline that ticket 02 measures. Brian, 2026-11-20.
- The code that fails a design check today gets a fix in this spec, with no allowlist. Each raw `<button>` moves to a wrapper of `ui/`. Each repeated arbitrary Tailwind value gets a role token. A true one-off keeps a one-line ignore comment with a reason. Brian, 2026-11-20.
- The "use it when / do not use it when" doc lives in the top docstring of each part file, as two fixed lines that a check can parse. The READMEs keep their "Knows" lists. Brian, 2026-11-20.
- The speed list: the Bun swap, a CI cache of `node_modules`, 4 shards of the unit suite in CI, diff-only tests on a PR with a full run when a config file or the lock file changes, and parallel steps in `make check-fast` with a cap for the hook. Brian, 2026-11-20.
- The look tokens have two tiers: a scale step and a role token. The spacing scale stays a scale. Three role tokens, `--color-accent-wash`, `-chosen`, and `-hover`, replace the chip washes. `--oc-dur` and `--es-dur` are runtime values, not tokens. Brian, 2026-11-20. `decisions/04-grill-token-roles.md`.
- Bun v1.4.5 has `check` (a port of TypeScript 7, 0.22 s against 1.16 s for `tsc`), `fmt`, `test --shard`, and `test --changed`. `bun lint` is canary only, so Oxlint runs the lint, with an ESLint-style plugin that moves to `bun lint` later. `bun test` ran 11 sample files in 0.60 s, against 3.25 s for Vitest. `decisions/01-research-bun-latest.md`.
- pnpm stays the installer. Bun runs on the `node_modules` that pnpm installs. Brian, 2026-11-20. `decisions/05-grill-bun-install-path.md`.
- The tests move to native `bun:test` calls plus one helper for `stubGlobal` and `stubEnv`, in happy-dom. The files move in batches on the spec branch, and `main` gets one swap. CI shards and runs `--changed` on a PR. The measured time sets the shard count. Brian, 2026-11-20. `decisions/06-grill-bun-test-port.md`.
- The baselines: a full `make check-fast` takes 195 s, and Vitest is 138 s of it. The CI run takes 754 s, and site-browser sets it at 746 s. `create_app` costs 4 ms per call, so the shared API app drops. `decisions/02-research-baseline-times.md`.
- Five design rules ship in one Oxlint config and a local plugin at `packages/design/lint/`: the `@ui-sdk` import, no raw color, no raw `<button>` or `<dialog>`, no arbitrary color or spacing value (32 uses), and the part docstring lines. The landmines rules stay out. `decisions/03-grill-design-rules.md`.

## NOT YET SPECIFIED

- What is the CI target, given a run of 754 s set by site-browser? `decisions/07-grill-ci-target.md`.

## OUT OF SCOPE

- The move from pnpm to `bun install`. Brian keeps pnpm for now. It is a follow-up after this spec.
- The Python tools of the pipeline and the API, such as `pytest` and `ruff`. Bun does not run Python.
- The landmines spike. It stays a Quick Win in the queue, after this spec merges, because its rules know Vitest names that this spec removes.
