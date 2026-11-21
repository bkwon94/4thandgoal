# 05: How the workspace moves from pnpm to `bun install`

Map: `.scratch/design-checks-speed/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

Ticket 01 found that `bun install` fails on the repo as it is. The repo has no root `package.json`. With a root file, the migration of `pnpm-lock.yaml` fails, because the lock has no `importers['.']` entry, and Bun resolves fresh versions. The notes are `01-research-bun-latest.notes.md`, section 1.

Decide:

1. Do we keep the pnpm versions, by a `pnpm install` after the new root `package.json` and then the migration? Or do we take the fresh versions and run the full suite on them?
2. What replaces each `pnpm` call in the root `Makefile`, `.github/workflows/check.yml`, the prek hook, and the root `AGENTS.md`? An example: `pnpm --dir apps/site <script>` becomes `bun run --cwd apps/site <script>`.
3. Does the isolated linker of Bun fit the Next.js build and the `packages/*` imports, or does the spec set the hoisted linker?

## Decision

Brian decided on 2026-11-20: pnpm stays the installer for now. The spec keeps `pnpm-lock.yaml`, the pnpm workspace, and each `pnpm` call. Bun runs `test`, `check`, and `fmt` on the `node_modules` that pnpm installs. The move to `bun install` is OUT OF SCOPE, as a follow-up after this spec. The facts for that follow-up are in `01-research-bun-latest.notes.md`, section 1.
