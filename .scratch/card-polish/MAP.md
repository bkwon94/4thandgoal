# Card polish: map

App: site.
Spec branch: `card-polish`.

## DESTINATION

One spec that upgrades five site parts with methods from Scrolltide items, in our own code: the Open card, the Grade dial, the Trend tile, the Ready halo, and the Index list. The goal: a phone reader gets more of each team's story from the cards and tiles, the site feels finished with the hero as the one loud surface, and each pattern has one shared part.

Rules that hold: ADR 0024 (the hero is the one loud surface), the ADR 0025 readability floor, the motion of each Scrolltide item, inside the hard rules of ADR 0028, and no change to the hero, which the `hero-slots` spec owns. No Scrolltide source enters the repo, because it is paid source and the repo is public. The team adapts the method and writes its own code.

## DECISIONS SO FAR

- The spec is one spec with one PR, slug `card-polish`. Brian, 2026-11-07.
- The spec changes the site only. The site build reads the earlier `page.json` files of the season for the trends of the week page. Brian, 2026-11-07.
- The terms are Open card, Grade dial, Trend tile, Ready halo, and Index list. The dial shows the Roster grade, not the Grade of the analyzer. The spec adds the terms to `GLOSSARY.md`. Brian, 2026-11-07.

- Each part follows its Scrolltide item as far as possible. Only a hard rule of ADR 0028 overrules the item. Brian, 2026-11-07.
- The Open card keeps the height, the focus blur, and the spring of the Showcase Card item. ADR 0028 records it. `decisions/01-grill-open-card-motion.md`.
- The large picture of the Index list is not the team avatar. Sleeper serves 400px at most, and only 8 of 24 teams have that size. `decisions/05-research-avatar-size.md`.
- One Open card part: GameCard keeps its closed layout with the Showcase drawer, LadderCard takes the full Showcase shell with a large rank. GameCard has three chips. `decisions/02-prototype-open-card-content.md`.
- The Grade dial is four equal arcs, one per part, lit by rank. Index cards keep the letter box with four small arcs in a row. Season So Far shows a 2x2 grid. `decisions/03-prototype-grade-dial-look.md`.
- Seven Trend tiles: the four week numbers and the three Moves tiles. Bars or a stepped area per tile, from week 1 to the page week. No donut. `decisions/04-grill-trend-tile-scope.md`.
- The chips of the Index list filter on the playoff race: All, In (75% or more, or clinched), Bubble (25% to 75%), Out (under 25%, or eliminated). `decisions/06-grill-index-list-chips.md`.
- The Index list is a ledger that opens rows in place on phone and tablet, and a ledger beside a sticky stage on desktop. Each row adds a small avatar. The stage is built from the `hero-slots` slots, and only its ticket waits for that spec to merge. `decisions/07-prototype-index-list-phone.md`.
- The Ready halo brightens with the share of passed checks: a team, a get, and a give per side. `decisions/08-spec-ready-halo-steps.md`.
- The grade weights are a site constant with a test against the pipeline tunables. `decisions/09-spec-grade-weights-source.md`.

## NOT YET SPECIFIED


## OUT OF SCOPE

- The Grade dial in the manager hero. The `hero-slots` spec owns the hero.
- A pipeline series for the trends. The spec changes the site only.
- The other Scrolltide items: Morph Navbar, Wordmark Bleed, and the easter-egg ideas. They wait for a later round.
- A link variant of `Card`, one section wrapper in place of four, and a refresh of `apps/site/.impeccable.md`. Each is a cleanup with its own ticket.
- A fetch of the 168px full-size avatar in place of the 80px thumb. It is a pipeline change, and this spec changes the site only.
