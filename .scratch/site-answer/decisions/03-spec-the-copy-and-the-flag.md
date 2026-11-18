# 03: The lead line, the blurbs, and the flag

Map: `.scratch/site-answer/MAP.md`.

**Kind:** spec

**Blocked by:** 01, 02

**Status:** open

## Question

These small choices go into the spec:

1. The fixed lead line of each display.
2. The blurb of each page, and its key in the client copy.
3. What a client with the `front_door` flag off shows, because its Menu has other items.
4. The Thread keeps a Site answer like any other Answer.
5. The exact row of `decide()` for decision 01, rules 4 and 6: a clear site yes runs before the Topic row, but a bare page name that is also a Topic, such as "power rankings?", keeps its Topic. One way: a site yes whose picked page matches a Topic with a yes on `FITS_TOPIC` goes to the Topic.

The copy names no internal part: no "Jev", "Advisor", "Finder", or "front door".

## Decision

None yet.
