# Egg polish: map

App: site.
Spec branch: `egg-polish`.

## DESTINATION

One site spec that makes the egg hunt feel like an event before the first egg drop on Tuesday, 2026-11-10.
It changes four parts after Scrolltide items: the egg opening, the claim, the egg word cards, and the egg board hero.
The lead goal is an event. The support goals are consistency with the site, clarity at each step, and pull to hunt.

## DECISIONS SO FAR

- The work ships before the first egg drop on Tuesday, 2026-11-10. Brian decided it in the Stage 1 grill.
- The scope is four parts: the crack, the claim after Tear Ticket, the egg word cards after Stack Slider, and the egg board hero on the hero slots. Brian decided it in the Stage 1 grill.
- The egg opening stays a crack, because it is an egg. Brian rejected Crumple Reveal in the Stage 1 grill.
- The crack starts at the tap point, spreads, and bursts into shards, after a short squash. `decisions/01-prototype-egg-crack.md`.
- The claim is a tear of the stub of a claim ticket; a tap or a key tears it too. `decisions/02-prototype-claim-tear.md`.
- The word cards are one slider with a tab row; the giant word lights the letters of the leader; closest race first; red wash for a won word. `decisions/03-grill-word-cards.md`.

## NOT YET SPECIFIED

- Which hero slots does the egg board fill, and does it get a hero scene? `decisions/04-spec-board-hero.md`.

## OUT OF SCOPE

- The egg button and the egg banner. They are signposts, and the time before Tuesday is short.
- Block Field, Unfurl, and Step Path. Each is a candidate for a later spec.
- Any change to the API, the claim rules, or the egg drop. The spec changes only how the site shows the hunt.
