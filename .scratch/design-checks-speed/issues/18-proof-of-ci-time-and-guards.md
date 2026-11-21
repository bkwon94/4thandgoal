# 18: Proof: the CI time and the out of scope guards

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-11, AT-28, AT-34, AT-36, AT-37, and AT-39.

**App:** root

**What to build:** The whole CI run takes 360 s or less, and no job takes more than 360 s. Each CI job uses a free standard runner. The spec added no `bun install`, no landmines rule, and no `node_modules` cache.

**Blocked by:** 04, 05, 06, 07, 14, 15, 16, and 17

**Status:** done

- [x] The median of 3 full CI runs of the spec branch is 360 s or less, and no job takes more than 360 s.
- [x] The lint of all site code exits 0.
- [x] Each `runs-on` line names a standard runner.
- [x] No `bun install` appears in the root `Makefile`, the workflows, or the hook config.
- [x] No file names a landmines rule.
- [x] No CI step caches a `node_modules` folder.

## Evidence

Date: 2026-11-21. Spec branch head: 4d5f4d13. Worktree branch: design-checks-speed-18.

### CI time

Three runs of `check.yml` with `workflow_dispatch`, one after the other. Each run has conclusion success. Total is `createdAt` to `updatedAt`. Job time is `startedAt` to `completedAt`. Both come from `gh run view <id> --json createdAt,updatedAt,jobs`.

| Run id | Total | Slowest job |
| --- | --- | --- |
| 44873662117 | 351 s | 342 s, site-browser (7) |
| 44874144251 | 315 s | 305 s, api |
| 44874592510 | 315 s | 304 s, site-browser (4) |

The median total is 315 s. The limit is 360 s. The slowest job of all 3 runs is 342 s. The limit is 360 s. The per-job times are in tickets 16 and 17.

### Lint of all site code

Command: `cd apps/site && pnpm lint`. Exit code: 0. The last line of output is the oxlint command line, and oxlint printed no warning and no error. The same lint ran in CI as `==> lint: ok` in the jobs 136753507714, 136755001704, and 136756394754.

### The `runs-on` lines

Command: `git grep -n "runs-on" -- .github`. Each of the 16 lines reads `runs-on: ubuntu-latest`: 8 in `check.yml` (lines 30, 50, 105, 203, 234, 258, 283, 311), 2 in `deploy-api.yml`, 2 in `deploy-sites.yml`, and 1 each in `rebuild.yml`, `refresh.yml`, `rerun.yml`, and `verdict.yml`. `ubuntu-latest` is a free standard runner.

### No `bun install`

Command: `git grep -n "bun install" -- Makefile .github .pre-commit-config.yaml`. The hook config is `.pre-commit-config.yaml`. Output: empty. Exit code: 1.

### No landmines rule

Command: `git grep -n -i landmine -- ':!.scratch'`. Output: empty. Exit code: 1.

### No `node_modules` cache

Command: `git grep -n -E "node_modules|cache" -- .github`. No line names `node_modules`. The caches are:

- `cache: pnpm` of `actions/setup-node`, which caches the pnpm store.
- `actions/cache` of `~/.cache/ms-playwright` and `~/.cache/apt-archives`.
- `enable-cache: true` of `setup-uv`, keyed on `uv.lock`.

## Comments

The merge: `342e25c0` merged into `design-checks-speed` on 2026-11-21; review fixes on fix branches a to n; Judge fix round on AT-13 (evidence only).
The proof: `make check-fast BASE=main` passed at each merge, 3 green CI runs on 4d5f4d13 gave a median of 315 s, and the Judge gave PASS to AT-1 to AT-39.
Read at least 5 files: AGENTS.md, apps/site/AGENTS.md, .scratch/design-checks-speed/PRD.md, .scratch/design-checks-speed/ACCEPTANCE.md, .scratch/design-checks-speed/issues/18-proof-of-ci-time-and-guards.md.
Closes with the squash merge of the spec PR.
