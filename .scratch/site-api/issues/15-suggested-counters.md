# 15: Suggested counters in the analyze document

**What to build:** When the verdict is "counter", the analyze document carries one to three suggested counters: a small change to the trade that moves the asker's letter up one step, each with the player to add or swap and a one-line reason. The site renders them in the "Suggested counters" slot under the verdict, which today reads "No counters yet."

**Blocked by:** None (can start immediately). The site slot exists; the site needs a small follow-up to render the new field.

**Status:** wontfix

- [ ] Add `counters` to the document: a list, empty unless the verdict is "counter". Each item has `ask` (a player id and name from the other roster, or a pick), `drop` (optional, a player the asker stops asking for), `letter` (the asker's letter after the change), and `reason`.
- [ ] The code proposes candidates from the other roster by the same rubric: run the grade on each one-player change and keep the ones that lift the asker's letter by one step. Cap the work at the top N players by points per game.
- [ ] Claude writes the one-line reason per counter in the same call as the analysis, with the same prose checks. No trade value, sum, ratio, or chart name.
- [ ] The fixture `tests/fixtures/api/analyze-response.json` gains a `counters` list and stays byte-identical with the site's copy after the site follow-up.
- [ ] Tests with the call patched: a "counter" verdict gets one to three items; an "accept" verdict gets none; each item's letter is one step above the start.
- [ ] The result cache key does not change.
- [ ] `uv run pytest -q` passes with no failed test.

## Comments

Closes as wontfix in the audit of `todoist-queue` on 2026-11-12. Brian dropped it, because it fixes no real bug and changes nothing that a manager sees.
Proof: `packages/analyzer/site/form/analyze-result.tsx` still shows "No counters yet.", and the manager-brain PRD puts counters out of scope; the letter-step method of the ticket died with the rubric, so it needs a new design if Brian still wants it.
Read 1 file: .scratch/todoist-queue/audit.md.
