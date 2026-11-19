# 11: The re-run job

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-14, AT-15, AT-16, AT-17, AT-18 and AT-36.

**App:** both

**What to build:** A CI job on each PR to `main` reads its script from `main`. It finds the quick file of the PR. For each item that is not text only, it runs the Red command at the red commit and expects a failure, and runs the Green command at the fix commit and expects a pass. It checks that the failure line quoted in the Red block shows in its own output. A PR with no quick file passes.

**Blocked by:** 01

**Status:** done

- [x] On a real git repo with a true red commit and fix commit, the script exits 0.
- [x] A Red command that passes at the red commit fails the job and names the item.
- [x] A quoted failure line that the command does not print fails the job and names the item and the line.
- [x] The job on the PR of this spec passes with the note "no quick file".
- [x] The workflow checks out its script from the default branch and names no model key.

## Comments

Closes with the squash merge of the spec PR: `trusted-green-11` (`f2a7bc59`) merged into `trusted-green` as `6dd53376` on 2026-11-18.
`scripts/test_rerun.py` has 10 tests, and AT-14 to AT-18 have PASS.
An older quick file with a free-form Red line gets a named FAIL from `scripts/rerun.py`.
The builder did not count the files it read; the ticket commit changed 3 files: .github/workflows/rerun.yml, scripts/rerun.py, scripts/test_rerun.py.
