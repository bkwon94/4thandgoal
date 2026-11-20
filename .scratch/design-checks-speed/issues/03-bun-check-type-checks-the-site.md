# 03: `bun check` type-checks the site

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-23.

**App:** site

**What to build:** The type check of the site runs `next typegen`, then `bun check`, in place of `tsc --noEmit`. The script name of the site no longer hides the subcommand.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] A type error in a scratch copy fails the type check with its file and line.
- [ ] The type check runs `next typegen` before `bun check`.
- [ ] The type check of the real code exits 0.
