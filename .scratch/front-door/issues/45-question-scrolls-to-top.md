# 45: A new question scrolls to its top under the Thread header

Spec: `.scratch/front-door/PRD.md`. Source: AT-31 in the evidence round of 2026-11-11.

**App:** site

**What to build:** When the reader sends a question into a Thread that holds Answers, the new question bubble scrolls so its top sits just under the Thread header. Today it stops at 454 px, then 312 px, while the header ends at 113 px. The older Answers above keep their render, with no entrance and no stream again.

**Blocked by:** none

**Status:** done

- [x] Red first: a test that sends a question into a Thread with two Answers at 375 px and reads the top of the question bubble against the bottom of the Thread header.
- [x] The bubble top lands within 16 px under the header, after the motion ends.
- [x] A short Thread, with too little content to scroll, does not jump.

## Comments
- Closes with the squash merge of the spec PR.
