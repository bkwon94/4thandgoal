# 06: Who gives the Test verdict

Map: `.scratch/fast-cycle/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

ADR 0020 made Brian post a test verdict for each acceptance test. Brian wants that comment gone, because the workflow should be sure enough by the time the PR opens, and he checks most work on the local dev server. Decision 01 forbids a weaker gate, so the comment needs a replacement.

## Decision

Brian decided on 2026-11-06, in a grill.

1. A fresh subagent, the Judge, gives PASS or FAIL for each `AT-<n>`. It reads only `ACCEPTANCE.md`, `EVIDENCE.md`, and the evidence files. It gets no build context.
2. After a FAIL, the orchestrator fixes the work and records the evidence of the failed tests again. A fresh Judge checks only those tests.
3. A second FAIL sets the test to BLOCKED. The orchestrator opens no PR and tells Brian the test and the reason.
4. The `verdict` check reads the Judge's verdicts. Brian merges.

The reason: the rule that no agent grades its own work holds, and the human step becomes the merge click. ADR 0026 records it and supersedes ADR 0020. Where the Judge writes is spec ticket 12.
