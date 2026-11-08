# 01: The layout of the six slots on a phone and on a tablet

Map: `.scratch/hero-slots/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** done

## Question

Do the six hero slots read well with real content? Build three real heroes in the slots: the manager hero, the Matchup of the Week, and the analyzer result. Brian looks at each one at 390px and at the `tablet` tier, in dark and in light.

The prototype answers three things:

1. On a phone, is one column in the order `eyebrow`, `title`, `meta`, `feature`, `stats`, `action` right for all three heroes?
2. From the `tablet` tier up, does the two-row split of Tide suit us? In that split, the top row holds the eyebrow and the title, the bottom row holds the stats and the action, and each row is set with `space-between`. Or does the hero stay one column at every width?
3. Do the gaps of Tide fit: `sp-6` between slots, `sp-2` from the eyebrow to the title, and `sp-1` inside the stats?

The prototype keeps the readability floor of ADR 0025: prose at 16px or more, all other text at 11px or more, and tap targets at 44px or more.

## Decision

Brian decided on 2026-11-07, after a prototype of three variants on a throwaway route. The route stacked the manager hero of "To Infinity and Bijan", the Matchup of the Week of week 8 of 2026, and the analyzer result of `.scratch/grade-clarity/evidence/AT-1/tradeA.document.json`, all from real `cpc` data.

1. **Phone.** One column in the slot order: `eyebrow`, `title`, `meta`, `feature`, `stats`, `action`. The variant that put `meta` above the title lost, because it buried the title.
2. **From the `tablet` tier up.** The two-row split of Tide. The top row holds the eyebrow and the title on the left and `meta` on the right, set with `space-between`. `feature` sits between the rows. The bottom row holds `stats` on the left and `action` on the right. A plain wide column wasted the width. Two columns with `feature` on the right failed, because the team rows broke after each word at 640px.
3. **`meta` stays short**, one or two lines, so the right column of the split holds. The week chips of the manager hero move to `feature`, beside the grade.
4. **The title of the Matchup of the Week is words**, such as "The Blue Tent by 1.43". The margin alone said too little as a title.
5. **`meta` is 16px.** The reason of the analyzer is a full sentence, so it is prose under ADR 0025.
6. **Gaps:** `sp-6` between slots, `sp-2` from the eyebrow to the title, and `sp-2` inside `stats`. `sp-1` inside `stats` looked cramped.
7. **An empty slot takes no space.** The analyzer result has no `stats` and no `action`. The Matchup has no `stats`. The manager hero uses its record line, such as "7-9 · 9th of 12", as its eyebrow.

The blurb of the Matchup, about 90 words, is the heaviest part of any hero. Where it goes is new fog: `decisions/05-spec-matchup-blurb.md`.

The prototype code is deleted. Space Grotesk 300 is already loaded, because `fonts.ts` loads weights 300 to 700.
