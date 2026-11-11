# 46: The ask box glides to the bottom in one move

Spec: `.scratch/front-door/PRD.md`. Source: AT-42 in the evidence round of 2026-11-11.

**App:** site

**What to build:** On the first question, the ask box glides from the center to the bottom in one move. Today it first rises about 55 px, from 452 px to 397 px, as the greeting leaves, then glides down to 668 px.

**Blocked by:** none

**Status:** in-review

- [x] Red first: a test that samples the top of the ask box each frame after the first send at 375 px. The top never moves up.
- [x] The glide is one move from the center to the bottom.
