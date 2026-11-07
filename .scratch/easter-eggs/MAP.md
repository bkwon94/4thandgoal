# Easter eggs: map

App: both. The site and the API, plus the weekly publish.
Spec branch: `easter-eggs`.

## DESTINATION

A CPC-only `eggs` package hides very hard eggs across the site, six more each Tuesday with the weekly publish. Each egg holds one letter. The first manager to find an egg claims it in a form on the site and puts its letter toward one egg word: CORNERSTONE, LANSDALE, or EAGLES. The API saves each claim, an egg board shows each manager in each egg word, and the first manager to fill an egg word wins its gift card.

## DECISIONS SO FAR

- The terms are Egg, Egg kind, Egg word, Egg drop, Hunter, and Egg board, in `GLOSSARY.md`. Grill of 2026-11-06.
- The three egg words are CORNERSTONE, LANSDALE, and EAGLES, 25 letters in all. Each egg word has one winner, and one manager can win all three. Grill of 2026-11-06.
- An egg is single use: its first hunter gets the letter, and then the egg is gone. `decisions/04-grill-egg-lifespan.md`.
- A manager claims an egg in a form on the site. The form asks for the manager at each claim, with no login and no check, because Brian trusts the league. The API logs each claim, and Brian can undo one. Brian cannot hunt, so the form omits his team. `decisions/05-grill-hunt-record.md`.
- A letter counts toward one egg word. A letter that fits none of the egg words of its hunter can still be claimed, as a block. Grill of 2026-11-06, ticket 01.
- Eggs hide in a secret list on the API. A generic listener in the bundle sends each multi-tap and long press to the API, which answers with an egg only for a match. The public repo and the bundle never name a spot. `decisions/02-prototype-code-reveal.md`.
- The API keeps the eggs and the claims in one SQLite file on its Fly volume. The rest derives from the two tables. Grill of 2026-11-06, ticket 01.
- An egg drop of six eggs goes live each Tuesday from week 9 to week 17, 54 eggs in all. Brian places the six spots. The API gives each spot a letter: the letters that the most managers still need, but never the last letter that a leader needs. Grill of 2026-11-06, ticket 01.
- An egg kind is a target, an action, and an optional condition. The catalog has 5 actions, 8 conditions, and about 30 targets, most on old week pages and the midseason page. `decisions/01-grill-egg-catalog.md`.
- Claude Design, the Design artifact type built into Claude, makes the design of the claim form, the egg, the animations, and the egg board. Brian, 2026-11-06. `decisions/08-prototype-claim-form.md`.
- The prizes are three gift cards: CORNERSTONE the biggest, LANSDALE the second, EAGLES the third. Grill of 2026-11-06.

## NOT YET SPECIFIED

- What is the value of each gift card, and does the site show it? `decisions/03-grill-rewards.md`.
- Does the site tell managers about the eggs or the egg drop, and does it give hints? `decisions/06-grill-hints.md`.
- What does the claim form look and feel like, with the status of each egg word to help the choice? `decisions/08-prototype-claim-form.md`.
- How does Brian place six spots each week, and how does the egg drop join the Tuesday publish? `decisions/09-grill-weekly-drop.md`.
- Does the egg check use an open route or the analyzer passphrase, how many calls may one browser make, and how does the listener leave a normal tap alone? `decisions/10-grill-listener-limits.md`.
- Where does the egg board sit in the menu, and what does it show? `decisions/07-spec-egg-board.md`.

## OUT OF SCOPE

- Eggs for `norcal` or any other client. The feature is for CPC only, so only `clients/cpc/client.toml` takes the package.
- A login, a PIN, or Google sign-in. Brian trusts the league, and an account is a barrier to the fun.
- A riddle, an answer box, or any typed answer. An egg is found and tapped, never answered.
- An egg that only a live NFL game window shows. It needs a game clock in the API. Hold it for a later catalog.
- Automatic payout of a gift card. Brian gives each prize by hand.
