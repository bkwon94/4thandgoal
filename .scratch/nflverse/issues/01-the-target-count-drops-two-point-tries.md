# 01 — The target count drops two-point tries

Spec: `.scratch/nflverse/PRD.md`. Research: `.scratch/nflverse/research.md`, question 2.

**What to build:** The usage reader counts a target as the nflverse rule does: a play with a receiver and no
two-point try. Carries skip two-point tries the same way. Today the count includes two-point tries and runs
34 targets high for the 2026 season. The change moves live trade grades through the trend adjuster, so it
goes out alone, before any other ticket.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] A two-point pass with a receiver is not a target, and a two-point run is not a carry.
- [ ] An agreement test: our target count equals the nflverse target count for every team week in the play by play fixture. The expected counts come from the nflverse weekly player file for the same weeks, saved as a small fixture.
- [ ] The red zone touch count skips two-point tries too, since every two-point try is at the 2-yard line.
- [ ] The existing usage tests pass with the fixture counts updated where a two-point try moved them.
