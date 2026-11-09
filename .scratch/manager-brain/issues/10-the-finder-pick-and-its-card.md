# 10: The Finder pick and its card

Spec: `.scratch/manager-brain/PRD.md`. Acceptance tests AT-26, AT-30, AT-31, AT-32, AT-46, AT-47, and AT-48.

**App:** both

**What to build:** A Finder press ends in picks a manager can trust. Code builds a sheet for each shortlist offer, with news only for those players. The Advisor picks up to 3, each with a headline and 2 to 3 Bullets: why you send it, and why he says yes. With no good offer, it gives a plain line. After two failed calls, the document holds the Jev shortlist with plain fact lines and the fallback flag. The finder document carries the headline and the Bullets in the shape of the analyze document. The card shows the headline, the swap, and the Bullet rows of ticket 04 with the same Marks and tap. Find works with no partner picked. "See the full result" grades the pick in the analyzer.

**Blocked by:** 04 and 09

**Status:** ready-for-agent

- [ ] A Find for Maye d'force B with U with no partner returns 1 to 3 picks, each with a headline and 2 to 3 Bullets.
- [ ] With Return of T Mac as the partner, no pick sends Jahmyr Gibbs for Bijan Robinson.
- [ ] Each pick of the press, sent to `/analyze`, reads Send it, Lean yes, or Gut call.
- [ ] With an Anthropic key that is not valid, the document holds the shortlist with fact lines and the fallback flag true.
- [ ] The card shows the rows, the Marks, and the tap of the analyzer, and no letter shows.
- [ ] Find works with no partner picked.
- [ ] `make check-fast` passes.
