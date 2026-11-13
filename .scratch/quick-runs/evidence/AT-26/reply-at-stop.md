Two quick runs are ready. The input held one Bug and one Quick win, so the run split them. Reply "go" or a fix to a done condition for each run.

Run 1 of 2
- Branch: `bug-pick-owner`
- Quick file: `.scratch/bugs/pick-owner.md`
- Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.
- Item 1: week_moves names the first owner of a traded pick. Kind: bug. Method: diagnosing-bugs.
  Done condition: `week_moves` in `apps/api/src/cornerstone_api/free_tools.py` names the manager who receives a traded pick from `owner_id`, not the first owner in `roster_id`.

Run 2 of 2
- Branch: `win-depth-sentence`
- Quick file: `.scratch/quick-wins/depth-sentence.md`
- Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.
- Item 1: Rewrite the depth phrases so a manager reads each one in one pass. Kind: quick-win. Method: text only.
  Done condition: each phrase of `DEPTH_MEANINGS` in `apps/api/src/cornerstone_api/personal_facts.py` reads as one plain clause, with no "meaning" and no "starter count past the starters".

Reply "go", a fix, or "stop" for each run.
