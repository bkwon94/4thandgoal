# 17: How does the roast sit inside the prose of a chapter?

Map: `.scratch/midseason-report/MAP.md`.

**Kind:** prototype

**Blocked by:** 14

**Status:** done

## Question

Brian found "The roast" as its own heading and block lame. The roast must fit into the prose naturally. Screenshot: `~/screenshots/midseason-feedback/01`.

Today each chapter has a `blurb` block and a separate `roast` block. Both apps change: the writer in `packages/midseason/python/src/midseason/prose.py`, the `roast` field in `published.py`, and the roast part of the site. The roast rules, the `roast` setting (`off`, `warm`, `hot`), and "each roast cites a fact" stay.

This ticket decides the shape of the prose with the roast inside it, its length, and what the `off` setting writes. Brian must read sample prose from the real data before the choice.

## Decision

Brian decided it on 2026-11-06, after five phone boards with the real CPC week 8 data in the row "Ticket 17 · the roast in the prose" of the Design canvas: P1 The kicker, P2 Woven, P3 The headline carries it, P1 v2 with four levels, and P4 Voice. He chose P4 Voice: "a lot better, I like this vibe better."

- **The roast setting is the voice of the whole paragraph,** not a sentence or a block. Brian rejected the kicker: a joke on the last sentence reads like a template, not natural writing.
- **Four levels,** each a different writer:
  - `off`: a sharp, clean sports writer. Lively, with no jabs.
  - `warm`: a funny friend in the group chat. It teases all the way through.
  - `hot`: a mean columnist. Every sentence has an edge.
  - `savage`: a full roast from the first word to the last.
- **The writer writes each level from scratch.** The facts sit inside the voice, not in a list with a joke after it.
- **The limits stay at every level, savage too:** football decisions only, nothing about life outside fantasy, no profanity, no slurs, and no starred-out swear words. Each paragraph cites real facts, and the fact check covers every number.
- **The writer gets facts from the whole report** for each paragraph, so it can make a callback across chapters, such as a lineup fact in the luck chapter. The fact check covers the borrowed facts too.
- **The writer names the unit of each number.** For example, "34.2" in a trade is points over the line, not raw points.
- **No count mix:** head-to-head numbers go with head-to-head records. The 11-5 record of CPC counts the median games.
- **Each chapter has one prose block of 40 words or fewer.** The `roast` block, "The roast" heading, and the `roast` field of each chapter in `published.py` go. The `roast` setting of each client takes the value `savage` too. The default is `savage`, set by Brian during the spec.

The bar for the writer is the P4 Voice board. Its best lines: "One auction, no survivors." "Remove the gifts and first place is a rumor." "That is losing with a head start."

Not chosen: P1, a joke on the last sentence. P2, a jab squeezed into a fact sentence. P3, a jab in the headline, which also needs a fact check of headlines.
