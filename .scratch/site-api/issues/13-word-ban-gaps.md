# 13: The rubric's word ban has gaps

**What to build:** The analysis prose never leaks a trade value by another word. Today the ban allows "value" with no number next to it, and "worth" and "price" are not banned at all.

**Blocked by:** None (can start immediately).

**Status:** wontfix

- [ ] Ban "worth" and "price" in the prose check, in every form.
- [ ] Decide on "value" with no number: ban it, or allow it only in the fixed phrase the rubric uses. Record the decision in the ticket.
- [ ] A `.value` fact number that equals a number in another cited fact fails the number check when the sentence is about value.
- [ ] Tests with the call patched: each banned word fails, the allowed phrase passes, the equal-number case fails.
- [ ] `uv run pytest -q` passes with no failed test.

## Comments

Closes as wontfix in the audit of `todoist-queue` on 2026-11-12.
Proof: Manager brain c133eb89 deleted `analysis.py`, `prompts/analysis.md`, and the rubric, so the prose check this ticket extends is gone.
Read 1 file: .scratch/todoist-queue/audit.md.
