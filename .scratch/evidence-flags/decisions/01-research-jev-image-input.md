# 01: Does TypeSafe Jev take images, and with what limits?

Map: `.scratch/evidence-flags/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** open

## Question

A third question asks if a screenshot shows text that is cut off or that overflows. It would catch defects such as AT-41 of easter-eggs, the banner cut at 375, and the pill bar overflow at 1280 that reached CI. The `Jev` port in `packages/league/python/src/league/jev_port.py` takes a text state only. Find out if the TypeSafe API and `typesafe-sdk` take an image, in what format, at what size limit, and at what cost. If Jev takes no image, this question moves to OUT OF SCOPE. If it does, the spec adds the image input to the port.

## Decision

None yet.
