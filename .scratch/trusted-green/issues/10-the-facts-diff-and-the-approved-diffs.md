# 10: The facts diff and the approved diffs

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-21, AT-22, AT-23 and AT-24.

**App:** pipeline

**What to build:** The rebuild job also diffs the facts of the latest week whose folder holds every saved input. A PR that changes the output on purpose lists each changed value in `REBUILD.md`: the client, the file, the JSON path, and one sentence of reason. The job passes only if the set of changed paths equals the listed set.

**Blocked by:** 08, 09

**Status:** done

- [x] A base and head rebuild with no change of code reports 0 diffs for each client.
- [x] A seeded change of one waiver score of cpc fails and names cpc, `waiver.json`, and the JSON path.
- [x] The same change passes when `REBUILD.md` lists it, and the output prints the reason.
- [x] A listed path that does not change fails and is named.

## Comments

Closes with the squash merge of the spec PR: `trusted-green-10` (`7b34c085`) merged into `trusted-green` as a fast-forward on 2026-11-18.
`scripts/test_rebuild.py` gained 9 tests, and AT-21 to AT-24 have PASS.
A facts-only rebuild of week 10 does not give back the committed price fields, because week 10 was built before the build saved its inputs.
The builder did not count the files it read; the ticket commit changed 3 files: .github/workflows/rebuild.yml, scripts/rebuild.py, scripts/test_rebuild.py.
