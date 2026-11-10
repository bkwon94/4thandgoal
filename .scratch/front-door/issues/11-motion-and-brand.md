# 11: The motion and the brand of the front door

Spec: `.scratch/front-door/PRD.md`. Acceptance tests AT-42, AT-43, AT-45, AT-46.

**App:** site

**What to build:** The ask box glides from the center to the bottom on the first question, on one shared layout spring. A tapped Suggestion morphs into the question bubble. "More" springs open from one pill, and the send button sits in a halo that grows as the field fills. The front door takes the look of variant C as the dark theme, in the brand of each client, with the light theme beside it. Under reduced motion, only the fades stay.

**Blocked by:** 03, 05

**Status:** ready-for-agent

- [ ] The ask box glides to the bottom in one move on the first question (AT-42).
- [ ] The tapped chip morphs into the question as one surface (AT-43).
- [ ] CPC and NorCal each use their own fonts, band, and accent, in light and dark (AT-45).
- [ ] Under `prefers-reduced-motion: reduce`, the front door fades with no glide, blur, or spring (AT-46).
- [ ] The motion follows the `transitions-dev` tokens, and `critique` and `polish` run before the commissioner sees it.
