# 02: What the Tools list and the page card look like

Map: `.scratch/site-answer/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** done

## Question

The Site answer has two displays, each its own new block kind:

1. The list view, for "what tools are there". It shows two groups, Tools and the pages to read.
2. The page card, for "where is X" and "how do I use X". It shows one page with its link and its blurb.

Which look and which motion should each display have? Build 2 or 3 variants of each in the Thread on a phone width, with `ui-sdk`, `transitions-dev`, and `scrolltide`, per the design bar. Brian picks one variant of each. Record the pick and the code facts the spec needs, then delete the prototype code.

## Decision

Brian, 2026-11-18, after three rounds of a UI prototype in the real cpc Thread at 390 px. Round 1 had three variants: A, a launcher of tiles; B, an index of rows in the Answer card; and C, a shelf of cards that scrolls sideways. Round 2 added D, a mix of A and B. Round 3 gave D one Tool tone. Brian chose D.

1. **The list view is the A launcher.** It is for "what tools are there". A lead line sits on the Thread. Then come two groups, "Tools" and "Pages to read", each a grid of tiles in 2 columns, or 3 from 640 px for the pages to read. The whole tile is the tap target, with an arrow mark in its corner. A tile holds an icon box, the label, and a one-line blurb. The tiles pop in from scale 0.96 with a fade, 250 ms, 40 ms apart.
2. **The page card is the B card.** It is for "where is X", "how do I use X", and a page the client lacks. The normal Answer card holds the lead line, the icon box and the page name, the blurb, and one full-width "Open the <page>" button. An "All pages · N" fold under it holds the rest as rows. The card settles as a normal Answer does. The rows rise 8 px with a 2 px blur, 40 ms apart. No small "Menu · <page>" line shows under the name.
3. **The none case is the B card with no page.** One line says that the site has no such page. The rows of all the pages follow.
4. **One Tool tone marks a Tool in both themes.** Red marks only a Tool. The pages to read keep the plain card surface in both themes.
   - Tool tile: `color-mix(in srgb, var(--color-accent) 10%, var(--color-card))` in light; `bg-raised` with a `border-rule` in dark. Ink text.
   - Icon box of a Tool and the "Open" button: `color-mix(in srgb, var(--color-accent) 20%, var(--color-card))` in light, `24%` into `var(--color-raised)` in dark. Text and icon in `--color-accent-ink`.
   - Button hover: 28% in light, 34% in dark, over 150 ms with `ease-out`. Press: the `press` utility, scale 0.98.
   - No solid white fill in dark, and no solid black fill in light.
5. **Contrast passes AA in both themes**, measured in Chromium: the button label 5.07 to 1 in light and 6.54 to 1 in dark; the blurb on a Tool tile 9.78 and 9.42; the label on a Tool tile 15.85 and 15.13.
6. **The Tools of cpc are the Trade Analyzer and the Playoff Sim.** The sim links to `/midseason/2026/#sim` until the standalone sim page of `season-sim` has a Menu link. Managers is a page to read. Home is not in the list.
7. **Reduced motion keeps only the fades.** Each link is a real `<a href>`, and nothing moves to a page with no tap.

What the prototype also showed, for the spec:
- The draft lead lines were "The site has 2 tools and 4 pages to read.", "The Trade Analyzer has its own page.", and "The site has no waiver page." with "Here is what it has." Ticket 03 sets the final copy.
- `--color-accent-text` is light pink in both themes and fails on a pale tile. `--color-accent-ink` is right for the Tool tone.
- The light Tool tile has a press state but no hover state. The spec adds the hover state.
- The test `src/no-plate.test.ts` (ADR 0036) rejects the bare word `plate` in code. The prototype named the field `iconBox`.
- In dark, the question bubble of the Thread is solid white. It is outside this spec, and it is a Quick win in the queue.

The prototype is on the branch `site-answer-proto-02` at `fc6714e9`, as the source record. It never merges. The variants are A, B, C, and D, with the switcher and `?variant=` and `?case=`.
