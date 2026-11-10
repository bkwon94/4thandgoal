# 04: The page shows the read as decided

Spec: `.scratch/manager-brain/PRD.md`. Acceptance tests AT-38, AT-39, AT-41, AT-42, AT-43, AT-44, AT-45, and AT-51.

**App:** site

**What to build:** The analyzer result reads as decision 05 set it. The hero shows the Lean word, then the 5-step scale from Pass to Send it with the Lean lit, then the Case clamped to 3 lines on the phone with "Read the full case", then the fairness line. Under the swap card, a switcher holds one tab per team at every width, the tab of the asker first. Inside a tab, the Bullets sit as rows in For, Against, and Even bands, with ▲, ▼, and – Marks. A band with no Bullet does not show. A screen reader hears the Mark as a word. A tap on a row opens its fact text under it. The Lean word rises in once, and reduced motion shows the page at rest.

**Blocked by:** 02

**Status:** done

- [ ] The hero shows the Lean word and the scale with that step lit, at 375, 768, and 1280 px in both themes.
- [ ] At 375 px the Case shows 3 lines, and "Read the full case" opens the rest.
- [x] The tab of the asker opens first, and a 3-team trade shows three tabs.
- [x] The bands show in the order For, Against, Even, and an empty band does not show.
- [x] A tap on a row opens its fact text.
- [x] The accessibility tree reads "for", "against", or "even" for each row.
- [x] With reduced motion on, the Lean and the Bullets show at rest.
- [x] The render tests of the analyze result cover the scale, the clamp, the tabs, the bands, the Marks, and the tap.
- [x] `make check-fast` passes.
