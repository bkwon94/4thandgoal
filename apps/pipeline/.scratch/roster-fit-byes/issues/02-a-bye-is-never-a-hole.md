# 02: A bye is never a hole

**What to build:** A starter's bye in any week makes no hole, whether or not a bench player covers him.
The absence read on a starting slot keeps one kind, due back. The cover logic drops its bye checks: a
cover is a bench player above the line at an allowed position who is not out himself, and his own bye
no longer matters. The hole sentence for a bye goes away. A starter due back inside the return window
with no cover is still a hole. One due back after the window is still a hole. One out with no return
week is still a hole. The schedule adjuster and its byes left lean do not change.

**Blocked by:** 01, Rename the bye window to the return window.

**Status:** done

- [x] A starter with his bye in week N+1 and no bench cover is no hole, and the reason has no "hole".
- [x] A starter with his bye in week N+1 and a bench cover is no hole.
- [x] Two starters with byes in the window and one cover give no hole.
- [x] A trade that gives away the only bench cover for a bye opens no hole and gives no step down.
- [x] A starter due back in week N+2 with no cover is still a hole, and with a cover is not.
- [x] A starter due back in week N+6 is still a hole.
- [x] With no schedule map, the reason still names the missing schedules.
- [x] The schedule adjuster tests for byes left still pass unchanged.
- [x] The hand-worked table passes with its letters unchanged. If a row moves, stop and report it.
- [x] The finder timing test stays under 5 seconds.
- [x] The full suite passes and ruff is clean.
