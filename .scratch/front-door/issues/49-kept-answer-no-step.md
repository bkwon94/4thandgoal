# 49: A kept Answer shows whole, with no step line first

Spec: `.scratch/front-door/PRD.md`. Source: AT-8 in Judge round 1 of 2026-11-11.

**App:** site

**What to build:** When the reader taps a personal Suggestion whose Answer is kept, the whole Answer shows at once. No step line shows first. Today the step "Reading the league…" shows for about 35 ms after the tap, then the kept Answer replaces it (`evidence/AT-8/run-weak-spots.txt`, frame 31.92 s). The Judge failed AT-8 on this, because its Then says "no stream and no tool step".

**Blocked by:** none

**Status:** done

- [x] Red first: a test that taps a personal Topic whose Answer is kept and samples each frame. No frame shows a step line.
- [x] A fresh Answer still shows its step lines during the wait (AT-65 stays true).
- [x] The fix shows no step line until the stream sends a step, or holds the first step line for a short intent delay, so a fast kept Answer never shows one.

## Comments
- Closes with the squash merge of the spec PR.
