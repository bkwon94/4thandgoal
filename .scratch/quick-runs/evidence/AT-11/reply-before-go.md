One quick run is ready. Reply "go" or a fix to the done condition.

- Branch: `bug-pick-owner`
- Quick file: `.scratch/bugs/pick-owner.md`
- Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.
- Item 1: week_moves names the first owner of a traded pick. Kind: bug. Method: diagnosing-bugs.
  Done condition: `week_moves` in `apps/api/src/cornerstone_api/free_tools.py` names the manager who receives a traded pick from `owner_id`, not the first owner in `roster_id`.

Reply "go", a fix, or "stop".
