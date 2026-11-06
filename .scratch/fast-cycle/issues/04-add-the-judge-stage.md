# 04: The Judge stage of cpc:implement and cpc:review

Spec: `.scratch/fast-cycle/PRD.md`. Acceptance tests AT-14, AT-15, AT-16, AT-17, AT-18, and AT-25.

**App:** both

**What to build:** After the evidence stage, `cpc:implement` starts a fresh Judge with a brief that names only `ACCEPTANCE.md`, `EVIDENCE.md`, and `evidence/`. The Judge writes `VERDICTS.md`, and the orchestrator commits it alone as "Record the Test verdicts of the Judge". A FAIL gets one fix round and a fresh Judge on the failed tests. A second FAIL sets BLOCKED, opens no PR, and tells Brian the test and the reason. The PR body no longer asks Brian for verdicts. `cpc:review` treats a FAIL of Brian as a finding, fixes it, records its evidence again, and runs a fresh Judge on that test. The text of each skill that says Brian gives the Test verdict now names the Judge.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] On a throwaway copy of the evidence of `faster-evidence` at `197fb328`, the Judge gives PASS to each of the 14 tests (AT-14).
- [ ] With the Observation of AT-2 of that copy made false, a fresh Judge gives FAIL to AT-2 with a reason that names the mismatch (AT-15).
- [x] The brief of the Judge names only the three paths, with no diff, ticket, PRD, or build note (AT-16).
- [ ] A throwaway feature whose AT-2 cannot pass gets BLOCKED after the second round, no `gh pr create` runs, and the message to Brian names AT-2 and the reason (AT-17).
- [ ] Each round is one commit that changes only `VERDICTS.md` (AT-18).
- [x] `GLOSSARY.md` defines **Judge** and the changed **Test verdict**, and ADR 0020 names ADR 0026 (AT-25).
