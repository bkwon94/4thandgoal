# 07: One workspace for two languages

Map: `.scratch/clients/MAP.md`.

**Kind:** prototype

**Blocked by:** 01

**Status:** open

## Question

How do `uv` and `pnpm` find the code of a package, and how does the check run per package? A package holds Python and React in one folder (ADR 0023). Build a throwaway workspace with two packages. Show that `uv` imports the Python of each one, and that `pnpm` builds the React of each one. Show that the check runs only on the packages a diff touched. Then delete the prototype.

Decision 01 note: Decision 01 sets eight packages, with the order `league`, then `facts`, then the core packages. `facts` has no site side, and `design` has no Python, so the workspace must take a package with one language. Decide the folder of the API app too: `cornerstone_api` lives in `apps/pipeline/` today.

## Decision

None yet.
