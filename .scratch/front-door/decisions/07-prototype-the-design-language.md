# 07: What is the look and the motion system of the front door?

Map: `.scratch/front-door/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** done

## Question

Build a throwaway prototype of the look and the motion: the type, the colors, the surfaces, and the motion tokens for open, close, enter, and stream. Follow the DESIGN BAR of the map. Brian sees it and reacts. The spec needs one cohesive system before the front door is laid out.

## Decision

Brian, 2026-11-09, after he ran three variants on his iPhone with real week 8 data: A "House" (the brand that exists now), B "Paper" (light and editorial), and C "Night" (dark and chat-first). He found A and C solid.

1. The front door takes the structure and the motion of C, in the brand of A.
   - From C: the ask box sits at the center of an empty Thread and glides to the bottom on the first question, on one shared layout spring. Suggestions are chips near the ask box. A chip morphs into the question bubble. The words of an Answer sharpen from a blur of about 6 px as they stream. The data block settles from a blur at a scale of 0.98.
   - From A: the fonts, the tokens, the band, and the accent of each client. A Suggestion morphs into the question as one surface, "More" springs open from one pill into the 13 Topics, and the send button sits in a halo that grows as the field fills.
2. The look of C becomes the dark theme of the brand, with a light theme beside it. The site already has a light and a dark theme.
3. Reason: each Answer links to a full page in the brand of A. A front door in a second brand makes each "Read the full report" tap a jump between two products.
4. The motion follows the `transitions-dev` tokens. It keeps the fades and drops each move, blur, and loop under `prefers-reduced-motion`. The check mark uses no bounce.

Ideas from scrolltide, with no code taken: Morph Pill Card, Morph Navbar, Send Halo, Nightjar, Focus Reveal, Showcase Card, Shoal, and mobula.

What the prototype also showed:
- The real layout sets no `viewport-fit=cover`, so the safe area of the iPhone stays 0. The spec must set it for an ask box pinned to the bottom.
- The dev server needs `allowedDevOrigins` for a phone on the LAN.
- Brian asked "week 1 results" and "highest scoring team this season" in the first minutes. See decision 12.

The prototype code is deleted from the repo. A copy for prototype 08 sits in the session scratchpad, outside the repo.
