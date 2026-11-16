# The team sheet has no close on a change of team

Kind: bug
Status: done
Branch: `bug-team-sheet-close`.
Source: the session of 2026-11-15.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The team sheet has no close when Your team is already set

Done condition: When Your team is set and the team sheet opens from "Change the team", a close button, Escape, and a tap on the dim each close the sheet and keep the old team, while the sheet of the first visit, with no team set, still has no close.
Method: diagnosing-bugs
Cause: `TeamSheet` in `apps/site/src/app/front-door/team-sheet.tsx` takes no close and ignores Escape and a tap on the dim, and `FrontDoor` in `front-door.tsx` sets `picking` to false only in `pick`, so a set team must pick a team to leave the sheet.
Red: at `af04a1c8` with `apps/site/src/app/page.test.tsx` of `43ce82a2`, `pnpm vitest run src/app/page.test.tsx -t "team sheet" --reporter=verbose` in `apps/site/`. The hook runs the site tests, so the loop and the fix share one commit.

```text
 × closes the team sheet of a change of team with the close button and keeps the old team 215ms
   → Unable to find an accessible element with the role "button" and name "Close"
 × closes the team sheet of a change of team with Escape and keeps the old team 3046ms
 × closes the team sheet of a change of team with a tap on the dim and keeps the old team 3042ms
 ✓ keeps the team sheet of the first visit open on Escape and on a tap on the dim, with no close button 536ms
AssertionError: expected <div role="dialog" …(6)>…(3)</div> to be null
      Tests  3 failed | 1 passed | 27 skipped (31)
```

Green: at `43ce82a2`, `pnpm vitest run src/app/page.test.tsx -t "team sheet" --reporter=verbose` in `apps/site/`

```text
 ✓ closes the team sheet of a change of team with the close button and keeps the old team 543ms
 ✓ closes the team sheet of a change of team with Escape and keeps the old team 402ms
 ✓ closes the team sheet of a change of team with a tap on the dim and keeps the old team 390ms
 ✓ keeps the team sheet of the first visit open on Escape and on a tap on the dim, with no close button 528ms
      Tests  4 passed | 27 skipped (31)
```
Test verdict: PASS

## Comments

Closes with the squash merge of the PR of `bug-team-sheet-close`. Commits: `af04a1c8`, `43ce82a2`, `1748ecf4`. Date: 2026-11-15.
The loop went red on 3 of 4 tests at the parent and green on 4 of 4 at the fix, and `make check-fast` passes with 1525 site tests.
A drag down to close the team sheet is not built, because the sheet runs on framer-motion and its grabber drags nothing.
Read 3 files: apps/site/src/app/front-door/front-door.tsx, apps/site/src/app/front-door/team-sheet.tsx, docs/agents/issue-tracker.md.
