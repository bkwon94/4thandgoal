# 11: The re-run job

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-14, AT-15, AT-16, AT-17, AT-18 and AT-36.

**App:** both

**What to build:** A CI job on each PR to `main` reads its script from `main`. It finds the quick file of the PR. For each item that is not text only, it runs the Red command at the red commit and expects a failure, and runs the Green command at the fix commit and expects a pass. It checks that the failure line quoted in the Red block shows in its own output. A PR with no quick file passes.

**Blocked by:** 01

**Status:** ready-for-agent

- [x] On a real git repo with a true red commit and fix commit, the script exits 0.
- [x] A Red command that passes at the red commit fails the job and names the item.
- [x] A quoted failure line that the command does not print fails the job and names the item and the line.
- [ ] The job on the PR of this spec passes with the note "no quick file".
- [x] The workflow checks out its script from the default branch and names no model key.
