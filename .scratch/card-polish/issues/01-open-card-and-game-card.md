# 01: Open card and GameCard

Spec: `.scratch/card-polish/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, AT-4, AT-8, AT-9, and AT-10.

**App:** site

**What to build:** One shared Open card part opens and closes a card in place, after the Showcase Card method: a height change with `grid-template-rows`, a 6px blur-in a beat behind the height, a spring `linear()` curve, a chevron that turns, and a manager pill with a solid fill. GameCard moves onto it. The closed card keeps both teams, both avatars, both scores, and the share bar. The open panel shows the best player of each side with its team avatar, both records, the recap, and the Manager page pill. The old GameCard accordion goes.

**Blocked by:** none

**Status:** blocked

- [ ] The Open card part opens and closes a GameCard on the week page of CPC week 8, and a part test proves `aria-expanded`, `aria-controls`, and `inert` on a closed panel.
- [ ] The open card of All You Need Is Love vs Unsolicited Dak Picks shows exactly three chips: Best J. Burrow 42.48, Best J. Jacobs 20.2, and Records 11-5 · 6-10.
- [ ] A unit test proves the spring sampler returns a `linear()` curve that starts at 0 and ends at 1.
- [ ] The reduced-motion test proves the card opens at once.
- [ ] Find-in-page finds a word of a closed recap.
- [ ] The frame-rate check at 4x CPU throttle records the median frame rate of an open, with the result in the evidence.
- [ ] `make check-fast` passes.

## Comments

- 2026-11-07, cpc:implement: blocked for Brian's choice. AT-8 and box 1 ask for `inert` on the closed panel, and AT-8 and box 5 ask find-in-page to find text in it. Chromium skips `inert` content in find-in-page: a probe found the word with a plain clipped drawer, and did not find it with `inert`, with or without `hidden="until-found"`. Option A: `hidden="until-found"` with no `inert`, and a `beforematch` listener that opens the card; AT-8 and box 1 change. Option B: keep `inert` and drop find-in-page; AT-8, box 5, and story 13 change. The branch `card-polish-01` holds a build of option A for a second start.
