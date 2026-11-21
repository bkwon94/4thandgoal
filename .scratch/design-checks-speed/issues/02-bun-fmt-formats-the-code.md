# 02: `bun fmt` formats the code and the checks enforce it

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-24.

**App:** site

**What to build:** `bun fmt` formats all site code and package code once, in one commit with no other change. Then the hook checks the format of the staged files, and CI checks the format of all files. The repo pins the Bun version in one place, and CI installs that version.

**Blocked by:** 01

**Status:** done

- [x] One commit holds only the format change of the whole code.
- [x] A staged file with an unsorted class list and a wrong indent fails the hook on the format check, and the commit does not land.
- [x] CI checks the format of all files and exits 0.
- [x] CI installs the pinned Bun version.

## Evidence of CI

Date: 2026-11-21. Runs 44873662117, 44874144251, and 44874592510 of `check.yml` on 4d5f4d13 all passed.

- The job `site-unit (1)` of each run runs `make check-site-unit`. Its raw log shows `==> fmt: ok`, and the job exits 0. The command is `bun fmt --no-script --check ... 'apps/site/**/*.{ts,tsx,mjs,mts,css}' 'packages/*/site/**/*.{ts,tsx,css}' ...`.
- Job logs: 136753507714 (`fmt: ok (1.1 s)`), 136755001704 (`fmt: ok (1.1 s)`), 136756394754 (`fmt: ok (0.8 s)`).
- The step "Set up Bun" uses `oven-sh/setup-bun@v2` with `bun-version-file: .bun-version`. The file holds `1.4.5`.
- Each log shows `Obtained version 1.4.5 from .bun-version`, then `1.4.5+a7733435c`, and the test step prints `bun test v1.4.5`.

## Comments

The merge: commits `b6a97422` to `c76f3599` on `design-checks-speed` on 2026-11-20; review fixes on fix branches a to n; Judge fix round on AT-13 (evidence only).
The proof: `make check-fast BASE=main` passed at each merge, 3 green CI runs on 4d5f4d13 gave a median of 315 s, and the Judge gave PASS to AT-1 to AT-39.
Read at least 5 files: AGENTS.md, apps/site/AGENTS.md, .scratch/design-checks-speed/PRD.md, .scratch/design-checks-speed/ACCEPTANCE.md, .scratch/design-checks-speed/issues/02-bun-fmt-formats-the-code.md.
Closes with the squash merge of the spec PR.
