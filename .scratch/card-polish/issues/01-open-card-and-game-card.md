# 01: Open card and GameCard

Spec: `.scratch/card-polish/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, AT-4, AT-8, AT-9, and AT-10.

**App:** site

**What to build:** One shared Open card part opens and closes a card in place, after the Showcase Card method: a height change with `grid-template-rows`, a 6px blur-in a beat behind the height, a spring `linear()` curve, a chevron that turns, and a manager pill with a solid fill. GameCard moves onto it. The closed card keeps both teams, both avatars, both scores, and the share bar. The open panel shows the best player of each side with its team avatar, both records, the recap, and the Manager page pill. The old GameCard accordion goes.

**Blocked by:** none

**Status:** in-review

- [x] The Open card part opens and closes a GameCard on the week page of CPC week 8, and a part test proves `aria-expanded`, `aria-controls`, and `hidden="until-found"` on a closed panel.
- [x] The open card of All You Need Is Love vs Unsolicited Dak Picks shows exactly three chips: Best J. Burrow 42.48, Best J. Jacobs 20.2, and Records 11-5 · 6-10.
- [x] A unit test proves the spring sampler returns a `linear()` curve that starts at 0 and ends at 1.
- [x] The reduced-motion test proves the card opens at once.
- [x] Find-in-page finds a word of a closed recap.
- [ ] The frame-rate check at 4x CPU throttle records the median frame rate of an open, with the result in the evidence.
- [x] `make check-fast` passes.

## Comments

- 2026-11-08: A Chromium probe showed that `inert` hides a closed panel from find-in-page, so box 1 and box 5 conflicted. A text fragment and `window.find()` found the text with no `inert` and did not find it with `inert`. Brian chose `hidden="until-found"` with a `beforematch` open, so the part tests prove `hidden="until-found"` and no `inert` on a closed panel.
- 2026-11-08: `pnpm check:open-card` on the cpc export recorded a median of 60 fps over 47 frames at a 4x CPU throttle and 375px. The evidence stage records it for AT-10.
