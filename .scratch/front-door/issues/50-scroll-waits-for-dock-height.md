# 50: The scroll to a new question waits for the new height of the dock

Spec: `.scratch/front-door/PRD.md`. Source: the CI run 43111521960 of PR #34. The test of ticket 45 failed on the NorCal floor with "the bubble top sits 303.015625px under the header".

**App:** site

**What to build:** The newest turn of the Thread holds a fill that reads `--door-dock`, the height of the dock. The page sets `--door-dock` from a ResizeObserver, one render after the dock changes. A dock that changes in the same render as a new turn leaves the fill short for one render. The scroll to the question starts in that render. The browser clamps the target of the scroll to the short page, and the later growth of the page does not move the scroll. The question then stops low under the Thread header.

Two paths hit it:

- A miss drops the chips of the dock in the same render as the miss card. The question stops 78 px under the header on NorCal and 54 px on CPC, on each run.
- The test of ticket 45 opens a Topic from the More panel, then asks at once. The More panel can end its exit in the same render as the note of the failed call. The dock then drops from 560 px to 144 px, the page max scroll is 808 px, and the target is 1099 px. The test fails about 1 run in 6 under load, on NorCal only, because the NorCal Answers leave less room below the question.

The fix is in the product. The scroll effect reads the height of the dock first. If the height differs from `--door-dock`, it sets the new height and scrolls on the next render.

**Blocked by:** none

**Status:** done

- [x] Red first: a test that answers a question with a miss in a Thread with two Answers at 375 px, and reads the top of the question bubble against the bottom of the Thread header. It failed at 78 px on NorCal and 54 px on CPC.
- [x] The bubble top lands within 16 px under the header, after the motion ends, on both clients.
- [x] The test of ticket 45 passes 10 runs of 10 at 6 workers on NorCal.

## Comments
- Closes with the squash merge of the spec PR.
