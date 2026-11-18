# 03: The lead line, the blurbs, and the flag

Map: `.scratch/site-answer/MAP.md`.

**Kind:** spec

**Blocked by:** 01, 02

**Status:** done

## Question

These small choices go into the spec:

1. The fixed lead line of each display.
2. The blurb of each page, and its key in the client copy.
3. What a client with the `front_door` flag off shows, because its Menu has other items.
4. The Thread keeps a Site answer like any other Answer.
5. The exact row of `decide()` for decision 01, rules 4 and 6: a clear site yes runs before the Topic row, but a bare page name that is also a Topic, such as "power rankings?", keeps its Topic. One way: a site yes whose picked page matches a Topic with a yes on `FITS_TOPIC` goes to the Topic.

The copy names no internal part: no "Jev", "Advisor", "Finder", or "front door".

## Decision

Brian approved the spec, 2026-11-18. `PRD.md` records each choice under Implementation Decisions:

1. The lead lines are fixed in code: "The site has N tools and M pages to read.", "The <label> has its own page.", and "The site has no page for that. Here is what it has." Decision 15.
2. Each package gives its blurb beside its menu link, not in `copy.toml`, because both clients share the words. Decision 11.
3. The page list follows the Menu that the client shows, so the `front_door` flag picks it as it picks the Menu. Decision 9.
4. The Thread keeps a Site answer as the page key only, and the site builds the links at render time. Decision 13.
5. Order A holds with no extra row. "power rankings?" and "show me the power rankings" score below 0.7, so they keep the Topic. Decision 6.
