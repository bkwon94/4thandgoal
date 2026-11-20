# 18: Proof: the CI time and the out of scope guards

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-11, AT-28, AT-34, AT-36, AT-37, and AT-39.

**App:** root

**What to build:** The whole CI run takes 360 s or less, and no job takes more than 360 s. Each CI job uses a free standard runner. The spec added no `bun install`, no landmines rule, and no `node_modules` cache.

**Blocked by:** 04, 05, 06, 07, 14, 15, 16, and 17

**Status:** ready-for-agent

- [ ] The median of 3 full CI runs of the spec branch is 360 s or less, and no job takes more than 360 s.
- [ ] The lint of all site code exits 0.
- [ ] Each `runs-on` line names a standard runner.
- [ ] No `bun install` appears in the root `Makefile`, the workflows, or the hook config.
- [ ] No file names a landmines rule.
- [ ] No CI step caches a `node_modules` folder.
