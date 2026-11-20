# 02: `bun fmt` formats the code and the checks enforce it

Spec: `.scratch/design-checks-speed/PRD.md`. Acceptance tests AT-24.

**App:** site

**What to build:** `bun fmt` formats all site code and package code once, in one commit with no other change. Then the hook checks the format of the staged files, and CI checks the format of all files. The repo pins the Bun version in one place, and CI installs that version.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] One commit holds only the format change of the whole code.
- [ ] A staged file with an unsorted class list and a wrong indent fails the hook on the format check, and the commit does not land.
- [ ] CI checks the format of all files and exits 0.
- [ ] CI installs the pinned Bun version.
