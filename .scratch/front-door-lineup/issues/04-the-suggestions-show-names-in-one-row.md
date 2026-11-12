# 04: The Suggestions show names in one row

Spec: `.scratch/front-door-lineup/PRD.md`. Acceptance tests AT-42, AT-43, AT-44.

**App:** site

**What to build:** At 375 px the Suggestions take one row of about 48 px, with "More" first and each chip showing only its Topic name. A first tap on a chip shows a full-width strip with the whole fact and "Open →". A second tap on the chip or the strip opens the Topic. A tap on another chip cross-fades the strip to its fact. The morph into the question, the "More" panel, reduced motion, and both themes stay.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] At 375 px the row is one line of about 48 px, with an empty Thread and with an Answer (AT-42).
- [ ] The first tap shows the strip, and the second tap opens the Topic (AT-43).
- [ ] A tap on another chip changes the strip and opens no Topic (AT-44).
- [ ] The design bar of the spec ran, and `critique` and `polish` found nothing open.
