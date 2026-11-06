# 15: The roast voice: one prose block per chapter

Spec: `.scratch/midseason-report/PRD.md`. Acceptance tests AT-40, AT-41, AT-52, AT-61, AT-62, and AT-63.

**App:** both

**What to build:** Each chapter of the report has one prose block of 40 words or fewer, written in the voice of the client's Roast setting: `off`, `warm`, `hot`, or `savage`, with `savage` as the default. The voice runs through the whole paragraph, as on the P4 Voice board of the Design canvas, row "Ticket 17 · the roast in the prose". The fact sheet of each block holds the facts of the whole report, so a paragraph can call back across chapters, and the verifier checks every number against it. The writer names the unit of a number that a reader can misread and never mixes the head-to-head count with the record that holds the median games. The separate roast block goes: `midseason.json` has no `roast` field in a chapter, and the site has no "The roast" heading. The limits of decision 17 stay at every level.

**Blocked by:** none.

**Status:** in-review

- [x] A build of CPC week 8 gives one prose block per chapter, each with 40 words or fewer, and the verifier passes each.
- [x] No chapter in `midseason.json` has a `roast` field, and the site schema and page agree.
- [x] With no `roast` value, the build runs at `savage`, and the review file names the level.
- [x] The config check rejects a `roast` value outside the four levels and names them.
- [x] A blurb that cites a fact of another chapter passes the verifier and the publish.
- [x] The prompt holds the four voices, the limits, the unit rule, the count rule, and the P4 Voice samples as examples.
