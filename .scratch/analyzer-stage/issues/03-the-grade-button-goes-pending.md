# 03: The grade button goes pending

Spec: `.scratch/analyzer-stage/PRD.md`. Acceptance tests AT-4 and AT-26.

**App:** site

**What to build:** The grade button wraps the ui-sdk `Button`. Under ADR 0035, the wrapper sits in the ui folder of the design package and takes its own name, because a shadcn button already sits there and other parts keep it. The click handler returns a Promise, so the button goes pending: it gets `aria-busy`, `aria-disabled`, and `data-pending`, keeps the focus, and its pending announcement is "Grading the trade". Its label stays "Grade the Trade". The pending state starts the wait of the hero, which is still the grading hero of today. The analyze call stays one `POST` with no stream.

**Blocked by:** none

**Status:** done

- [x] Only the wrapper imports `@ui-sdk`, and the rule test of ADR 0035 passes.
- [x] A keyboard tap on "Grade the Trade" with trade T gives `aria-busy="true"` and `data-pending`, and the focus stays on the button through the wait.
- [x] The label stays "Grade the Trade" while the button is pending.
- [x] The network log of a grade shows one `POST` to the analyze route with a JSON response.

## Comments

The merge: `688abc0e` merged into `analyzer-stage` on 2026-11-16; review fixes `a8f2b48d` and `4eb5bef2`; Judge fix round `7b1d09c7`.
The proof: `make check-fast` passed at each merge, the full check passed on 2026-11-17, and the Judge gave PASS to AT-1 to AT-34 after one fix round.
Read at least 5 files: AGENTS.md, apps/site/AGENTS.md, .scratch/analyzer-stage/PRD.md, .scratch/analyzer-stage/ACCEPTANCE.md, .scratch/analyzer-stage/issues/03-the-grade-button-goes-pending.md.
Closes with the squash merge of the spec PR.
