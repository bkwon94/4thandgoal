# 10: The facts diff and the approved diffs

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-21, AT-22, AT-23 and AT-24.

**App:** pipeline

**What to build:** The rebuild job also diffs the facts of the latest week whose folder holds every saved input. A PR that changes the output on purpose lists each changed value in `REBUILD.md`: the client, the file, the JSON path, and one sentence of reason. The job passes only if the set of changed paths equals the listed set.

**Blocked by:** 08, 09

**Status:** in-review

- [x] A base and head rebuild with no change of code reports 0 diffs for each client.
- [x] A seeded change of one waiver score of cpc fails and names cpc, `waiver.json`, and the JSON path.
- [x] The same change passes when `REBUILD.md` lists it, and the output prints the reason.
- [x] A listed path that does not change fails and is named.
