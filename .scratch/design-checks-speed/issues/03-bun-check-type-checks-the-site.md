# 03: `bun check` type-checks the site

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-23.

**App:** site

**What to build:** The type check of the site runs `next typegen`, then `bun check`, in place of `tsc --noEmit`. The script name of the site no longer hides the subcommand.

**Blocked by:** none

**Status:** done

- [x] A type error in a scratch copy fails the type check with its file and line.
- [x] The type check runs `next typegen` before `bun check`.
- [x] The type check of the real code exits 0.

## Comments

The merge: `aa750de1` on `design-checks-speed` on 2026-11-20; review fixes on fix branches a to n; Judge fix round on AT-13 (evidence only).
The proof: `make check-fast BASE=main` passed at each merge, 3 green CI runs on 4d5f4d13 gave a median of 315 s, and the Judge gave PASS to AT-1 to AT-39.
Read at least 5 files: AGENTS.md, apps/site/AGENTS.md, .scratch/design-checks-speed/PRD.md, .scratch/design-checks-speed/ACCEPTANCE.md, .scratch/design-checks-speed/issues/03-bun-check-type-checks-the-site.md.
Closes with the squash merge of the spec PR.
