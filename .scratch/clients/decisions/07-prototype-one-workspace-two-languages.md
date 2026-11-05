# 07: One workspace for two languages

Map: `.scratch/clients/MAP.md`.

**Kind:** prototype

**Blocked by:** 01

**Status:** done

## Question

How do `uv` and `pnpm` find the code of a package, and how does the check run per package? A package holds Python and React in one folder (ADR 0023). Build a throwaway workspace with two packages. Show that `uv` imports the Python of each one, and that `pnpm` builds the React of each one. Show that the check runs only on the packages a diff touched. Then delete the prototype.

Decision 01 note: Decision 01 sets eight packages, with the order `league`, then `facts`, then the core packages. `facts` has no site side, and `design` has no Python, so the workspace must take a package with one language. Decide the folder of the API app too: `cornerstone_api` lives in `apps/pipeline/` today.

## Decision

Brian decided each item on 2026-11-03, from a throwaway workspace. The workspace held `league` in both languages, `facts` in Python only, `design` in the site only, and `waiver` in both, plus a thin `apps/pipeline`, `apps/api`, and `apps/site`. The prototype is deleted.

### What the prototype showed

- One root `pyproject.toml` with `[tool.uv.workspace] members = ["apps/pipeline", "apps/api", "packages/*/python"]` and one root `uv.lock`. `pipeline` imported `waiver`, `waiver` imported `facts`, and `facts` imported `league`.
- One root `pnpm-workspace.yaml` with `apps/site` and `packages/*/site`. Each package ships TSX source with no build step, and `transpilePackages` in `next.config.ts` compiles it. The static export held the waiver board.
- A package with one language works. The globs skip a folder that does not exist, with no error.
- The shared `.venv` holds every member, so `api` imported `waiver` with no dependency on it. `uv run --exact --package cpc-api` fails that import with `ModuleNotFoundError`. pnpm already blocks an undeclared import, because each package gets only its own `node_modules`.
- `pnpm --filter "...[<ref>]"` selects each changed package and each package that depends on it. uv has no such filter, so a short script reads the workspace sources of each `pyproject.toml`.
- A diff that touched only a root file, such as `pnpm-workspace.yaml`, selected no package.

### The decision

1. **One root workspace and one root lock file per language.** The Python package is `cpc-<domain>` and imports as `<domain>`. The npm package is `@cpc/<domain>`. A package has no build step. CI caches the root `uv.lock` and the root `pnpm-lock.yaml`.
2. **The API is the app `apps/api/`.** It is a thin uv member, apart from `apps/pipeline/`. The analyzer routes stay in `packages/analyzer/python` (decision 01).
3. **A change selects by package, not by language.** A change anywhere in `packages/<domain>/` checks both languages of that package, plus each package and app that depends on it. The published file is the seam between the two languages (ADR 0011), so a change to the Python can break the site.
4. **The check runs each Python member with `uv run --exact --package <name>`.** An import of a package that the member does not list then fails, so the check enforces the dependency order of decision 01.
5. **A change to a root file runs the full check.** The root files are the workspace files, the lock files, the root `Makefile`, and `.github/`.
