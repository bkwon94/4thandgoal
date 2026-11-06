# Easter eggs: map

App: both.
Spec branch: `easter-eggs`.

## DESTINATION

A CPC-only `eggs` package hides two to three eggs in each week build, from medium to extremely hard to find. A manager who finds an egg sends its egg code to Brian, the first one is its hunter and gets the reward by hand, and the egg board on the site shows each egg and its hunter.

## DECISIONS SO FAR

- The site has no login, so a manager claims an egg outside the site: the egg code goes to Brian. Brian gives each reward by hand. Grill of 2026-11-06, Stage 1.
- The pipeline makes two to three eggs each week from a catalog of egg kinds that Brian and Claude brainstorm. Grill of 2026-11-06, Stage 1.
- The site holds only a hash of each egg code. The real codes stay out of the public repo. Grill of 2026-11-06, Stage 1.
- Brian records each hunter in a file, and the egg board on the site shows each egg, its hunter, and its reward. Grill of 2026-11-06, Stage 1.
- The terms are Egg, Egg kind, Egg code, Hunter, and Egg board, in `GLOSSARY.md`. Grill of 2026-11-06, Stage 1.

## NOT YET SPECIFIED

- Which egg kinds go in the catalog, on which pages, at which difficulty? `decisions/01-grill-egg-catalog.md`.
- How does an egg show its code only after the hard steps, and how do the codes reach Brian but not the repo? `decisions/02-prototype-code-reveal.md`.
- What are the rewards, and does a reward depend on the difficulty? `decisions/03-grill-rewards.md`.
- Does an egg end with its week, or stay hidden until a hunter finds it? `decisions/04-grill-egg-lifespan.md`.
- How does a manager send a code, and how does Brian record the hunter and settle a tie? `decisions/05-grill-hunt-record.md`.
- Does the site tell managers that eggs exist, and does it give hints? `decisions/06-grill-hints.md`.
- Where does the egg board sit in the menu, and what does it show for a hidden egg? `decisions/07-spec-egg-board.md`.

## OUT OF SCOPE

- Eggs for `norcal` or any other client. The feature is for CPC only, so only `clients/cpc/client.toml` takes the package.
- A login or a claim form on the site. The destination claims each egg outside the site, by hand.
- Automatic payout of a reward. Brian gives each reward by hand.
