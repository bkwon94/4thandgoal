# 05: Install the approved examples

**What to build:** The tone prompt holds the 6 to 8 sentences Brian kept from ticket 04 as the passed examples, each with the fact IDs it cites and one line on why it passed. The failed examples that teach an accuracy rule stay, rewritten in the new voice, with their lesson intact. Every other old example is gone. The rule that example numbers and names never appear in a new blurb stays.

Spec: `.scratch/tone/PRD.md`, section "The example set".

**Blocked by:** 04 Draft the example candidates, and Brian's pick in its comments.

**Status:** ready-for-agent

- [ ] The passed examples are Brian's picks, with fact IDs and a one-line reason each.
- [ ] The failed examples keep their accuracy lessons and read in the new voice.
- [ ] No old passed example remains.
- [ ] A prompt text test guards that the examples section names every picked example.
- [ ] `make test` passes. Lint count on the branch is no higher than on main.
