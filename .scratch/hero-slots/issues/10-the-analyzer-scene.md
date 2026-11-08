# 10: The analyzer scene

Spec: `.scratch/hero-slots/PRD.md`. Acceptance tests AT-20, AT-21, and AT-42.

**App:** site

**What to build:** A manager opens `/analyze/`, and the lights of the scene drift while no trade is graded. The manager grades grade-clarity trade A, and when the verdict "Yes" arrives, the lights settle into two groups, one per side, with the bigger group on the side of behold the lamb. This is the last ticket of the spec. If it cannot ship, the analyzer form keeps the drift of the 404 and the rest of the spec still ships.

**Blocked by:** 04 and 07

**Status:** ready-for-agent

- [ ] Before a grade the lights move for 6 s and do not settle (AT-20).
- [ ] After the verdict of trade A the lights settle into two groups, with the bigger group on the side of behold the lamb, from a run on the real API (AT-21).
- [ ] No file under `apps/pipeline/` and no published file under `clients/` changes against `main` (AT-42).
- [ ] `pnpm check:floor` passes for `cpc` and `norcal`.
