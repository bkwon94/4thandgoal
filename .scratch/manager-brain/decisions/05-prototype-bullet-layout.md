# 05: What layout the Lean, the Case, and the Bullets take

Map: `.scratch/manager-brain/MAP.md`.

**Kind:** prototype

**Blocked by:** 04

**Status:** done

## Question

The side cards trade their factor rows for 3 to 5 Bullets per side, each with a Mark: for, against, or even. A Finder trade gets 2 to 3 Bullets. The hero holds the Lean, the Case, and the fairness line. Decide the layout on the phone and the desktop: the order of the Bullets, the look of the Mark, how the Case reads at length, and if a tap shows the fact behind a Bullet. Search scrolltide for ideas before the layout prototype. Use real output from the winning arm of ticket 04.

## The prototype

Three variants on one throwaway route, with real Advisor output from prototype 04 (28 trades and the Finder picks):

- A, Ledger: the page of today. The Case is clamped to 3 lines. Each Bullet is a row with a ▲ or ▼ Mark, and a tap on the row opens its fact.
- B, Scale: a 5-step scale from Pass to Send it with the Lean lit. The full Case sits under it. A sliding switcher picks the side, with For, Against, and Even bands.
- C, Letter: the Case as a long letter, with a "facts behind it" list and small numbered fact tags.

Scrolltide had no advice layout. The 5-step scale came from a segmented dial in its "Sales Console" screen. The motion came from transitions.dev: the staggered text reveal and the accordion.

## Decision

Brian, 2026-11-09: A as the base, with the scale and the side switcher of B.

1. The hero shows the Lean word, then the 5-step scale (Pass, Lean no, Gut call, Lean yes, Send it) with the Lean step lit, then the Case, then the fairness line. No letter shows.
2. The Case is clamped to 3 lines on the phone, with "Read the full case" to open the rest. The Advisor writes the Case with its condition first, so the clamp always shows it. This is a rule of the Advisor prompt, not of the layout.
3. The Bullets sit in a switcher of B, one tab per team, at every width. The same pattern covers a trade of 3 or more teams. The tab of the asker opens first.
4. Inside a tab, the Bullets are rows of A, in bands: For, then Against, then Even. A band with no Bullet is left out.
5. The Mark is a glyph, not a color alone: ▲ for, ▼ against, – even. The glyph is decorative, and a screen reader hears the word.
6. A tap on a row opens the fact behind the Bullet under it, as an accordion. The API sends the fact text with each Bullet, because the fact id alone does not read.
7. The Finder card shows the headline, the swap, then its 2 to 3 Bullets as rows of A, with the same Marks and the same tap.

Known risk: the tabs hide the other side until a tap, and "would he accept" is half the advice. Brian chose tabs for one pattern across all trade sizes.
