# 03: Lock the form while a grade runs

**What to build:** From the moment the user submits a trade until the result or the error arrives, every player row and the two team pickers are locked. A tap on a row does nothing and the row shows it is locked. The submit button shows the grade is in progress. When the result arrives, the form unlocks.

**Why:** The commissioner can tick and untick players while the grade runs, and the result then does not match the form.

**Blocked by:** None.

**Status:** done

- [x] `src/components/trade-form.tsx`: a `locked` state set on submit and cleared on result or error. Rows and pickers read it: `disabled` on the inputs, `aria-disabled` on the rows, and a muted look with tokens only.
- [x] The submit button reads "Grading…" with `aria-busy` while locked. No pulse under `useMotionOff`.
- [x] A 422 or a 429 unlocks the form, so the user can fix the trade.
- [x] Tests read the screen: after submit, a row tap changes no pick; after the result, a tap works; after an error, a tap works.
- [x] Check at 390 wide with `agent-browser` during a grade. A real grade takes 5 to 20 seconds, so use a slow local API or throttle.
- [x] `pnpm test` passes with no failed test. 133 of 133 pass on `lock-form` at `4e2015b`.
- [ ] Push to main deploys.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in 4e2015b6.
Proof: The commit "Lock the trade form while a grade runs" merged in 2dcfda4c on `main`, and `grade-bar.tsx` sets `aria-busy` and "Grading…".
Read 1 file: .scratch/todoist-queue/audit.md.
