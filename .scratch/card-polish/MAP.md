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

## NOT YET SPECIFIED

- What does each Open card show closed and open? `decisions/02-prototype-open-card-content.md`.
- How does the Grade dial look? `decisions/03-prototype-grade-dial-look.md`.
- Which tiles become Trend tiles, and what does each trend plot? `decisions/04-grill-trend-tile-scope.md`.
- How large are the Sleeper avatars? `decisions/05-research-avatar-size.md`.
- What do the chips of the Index list filter on? `decisions/06-grill-index-list-chips.md`.
- How does the Index list sit at 390px? `decisions/07-prototype-index-list-phone.md`.
- What steps fill the Ready halo? `decisions/08-spec-ready-halo-steps.md`.

## OUT OF SCOPE

- The Grade dial in the manager hero. The `hero-slots` spec owns the hero.
- A pipeline series for the trends. The spec changes the site only.
- The other Scrolltide items: Morph Navbar, Wordmark Bleed, and the easter-egg ideas. They wait for a later round.
- A link variant of `Card`, one section wrapper in place of four, and a refresh of `apps/site/.impeccable.md`. Each is a cleanup with its own ticket.
