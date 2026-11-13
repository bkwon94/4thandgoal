# A quick run skips the spec flow

This ADR amends ADR 0026. ADRs 0020 and 0026 say a PR to `main` merges on the Test verdicts of its
acceptance tests. That flow costs hours for a spec, and the same cost falls on a one-line bug fix.
We decided that a bug or a small change goes through `4ag:quick`, a quick run, and skips the spec flow.

## The boundary

A change is a quick run when all four rules hold:

1. It fits on one branch and one PR, with up to five items of one kind: each a Bug or each a Quick win.
2. It adds no term to `GLOSSARY.md` and needs no ADR.
3. It moves no seam: no new port, no new page, and no new shape of a data file.
4. Each item has a done condition of one sentence.

If one rule fails during the run, the run stops and hands off to `4ag:plan`.

## What a quick run keeps

- The builder never gives the Test verdict. A fresh Judge reads only the done conditions and the
  evidence, and gives PASS, FAIL, or BLOCKED for each item.
- A Bug shows red evidence before the fix and green evidence from the same loop after the fix.
- The record stays in the local tracker, at `.scratch/bugs/<slug>.md` or `.scratch/quick-wins/<slug>.md`,
  because the notes may name league managers (ADR 0021).
- Brian merges each PR. CI runs the full suite.

## What a quick run drops

- The map, the spec, `ACCEPTANCE.md`, the tickets, and the ticket branches.
- The `verdict` gate. The PR has no `ACCEPTANCE.md`, so `verdict.yml` passes it.
- The Judge for an item whose evidence is only a diff of text or config.

## Why the narrow Judge

The common miss of an agent bug fix is a test that does not match the bug. The test fails for some
other cause, and then it passes, and the real bug stays. The builder wrote both halves, so it cannot
see this. The Judge asks two questions per item: does the red evidence show the bug of the done
condition, and does the green evidence come from the same loop at the fixed commit?

We rejected three alternatives:

- **A light mode inside `4ag:plan` and `4ag:implement`.** It makes the two biggest skills longer and
  blurs when each flow applies.
- **No Judge.** The builder would grade its own work.
- **A `verdict` gate on a quick PR.** Brian merges each PR, and the gate adds CI work for little gain.
  If a FAIL slips into a merge, we add the gate then.
