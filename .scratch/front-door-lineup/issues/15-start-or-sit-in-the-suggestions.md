# 15: Start or sit in the Suggestions

Spec: `.scratch/front-door-lineup/PRD.md`. Acceptance tests AT-13, AT-14, AT-15.

**App:** both

**What to build:** Start or sit joins the Suggestions. It leads Thursday to Sunday, sits third on Wednesday after Waiver targets, and leaves Monday as today. It goes first on any day when a starter is OUT, on IR, or on a bye. Its fact comes from code facts only: "1 can't play, 1 Q", or the next kickoff of the lineup when both counts are zero.

**Blocked by:** 13

**Status:** ready-for-agent

- [x] A pytest shows the order on Thursday, Sunday, Wednesday, and Monday (AT-13).
- [x] A pytest or a live run shows Start or sit first on a Tuesday with a hole in the lineup (AT-14).
- [x] The fact reads "N can't play, M Q" or "Next kickoff <day> <time>", and the Suggestions make no Jev call (AT-15).
