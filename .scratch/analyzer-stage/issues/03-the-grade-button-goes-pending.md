# 03: The grade button goes pending

Spec: `.scratch/analyzer-stage/PRD.md`. Acceptance tests AT-4 and AT-26.

**App:** site

**What to build:** The grade button wraps the ui-sdk `Button`. Under ADR 0035, the wrapper sits in the ui folder of the design package and takes its own name, because a shadcn button already sits there and other parts keep it. The click handler returns a Promise, so the button goes pending: it gets `aria-busy`, `aria-disabled`, and `data-pending`, keeps the focus, and its pending announcement is "Grading the trade". Its label stays "Grade the Trade". The pending state starts the wait of the hero, which is still the grading hero of today. The analyze call stays one `POST` with no stream.

**Blocked by:** none

**Status:** ready-for-agent

- [x] Only the wrapper imports `@ui-sdk`, and the rule test of ADR 0035 passes.
- [x] A keyboard tap on "Grade the Trade" with trade T gives `aria-busy="true"` and `data-pending`, and the focus stays on the button through the wait.
- [x] The label stays "Grade the Trade" while the button is pending.
- [x] The network log of a grade shows one `POST` to the analyze route with a JSON response.
