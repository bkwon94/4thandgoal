# 01: Does the Open card get the focus blur and the height animation?

Map: `.scratch/card-polish/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

The Showcase Card method opens a drawer with a height change on a spring, and the details come into focus from a 6px blur. Our motion rule allows only transform and opacity. The recap panel and the team picker are already exceptions for height. The spec must say if the Open card is a third exception for height, and if the blur is allowed or replaced by opacity and a short rise. A yes may need a change to the motion rule in an ADR.

## Decision

The Open card keeps the motion of the Showcase Card item. Brian decided it on 2026-11-07, with the rule "follow the Scrolltide item as far as possible".

1. The height animates with `grid-template-rows` from `0fr` to `1fr`. It is the one height method for every Open card. The closed panel stays in the DOM with `hidden="until-found"`, so find-in-page still finds its text and opens the card. Correction from cpc:implement: Chromium skips `inert` content in find-in-page, so `inert` cannot meet this rule.
2. The details come into focus from a 6px `filter: blur`, a beat behind the height. An acceptance test records the frame rate on a throttled phone profile. The blur goes only if that test fails.
3. The card moves on a damped spring, sampled into a CSS `linear()` curve, with the small overshoot of the item.

Reduced motion turns each of these to an instant change. ADR 0028 records the exception to the motion rule of ADR 0024.

A fact found on the way: GameCard does not animate its height now. It mounts the panel with opacity and a rise. Only LadderCard animates height, with `framer-motion`.
