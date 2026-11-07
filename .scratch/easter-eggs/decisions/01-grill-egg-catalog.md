# 01: Which egg kinds go in the catalog

Map: `.scratch/easter-eggs/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

Which egg kinds go in the catalog of the first build: the targets, the actions, and the conditions. Each egg must be very hard to find, found by a tap and never by an answer, and hard for an AI that reads the whole site.

## Decision

Brian decided in the grill of 2026-11-06. An egg kind is a target, an action, and an optional condition, which combine. The survey of the app is in `01-grill-egg-catalog.notes.md`.

Actions:

- 2 to 5 taps in a row.
- A long press of 1 second, or a long hold of 3 or 5 seconds.
- A tap combo: tap A, then B, then C on one page.
- A selected word: highlight one exact word in a blurb.

Conditions:

- Light mode. Dark is the default.
- An open state: a "Show all", a popover, a chip, or a fold.
- An old week, or the frozen midseason page.
- A sim outcome: the replay shows roster X as champion, or at one seed.
- An analyzer trade: one exact trade, or any trade that the analyzer grades F.
- A clock window, such as 11 PM to midnight ET, or a Thursday.
- Scroll first: the egg works only after a scroll to the end of the page.
- A page that does not exist: a typed URL shows the 404 page with an egg.

Targets: a number tile, an award tile, a leaders row, a median bar, a recap line, and the must-watch card of a week page. The "01" of the rankings hero, a ladder tile, and a movement arrow row. A W/L chip, an odds tile, a grade factor row, a roster row, a moves row, and a best adds row of a manager page. A Luck cell, a Top 10 row, a bench row, a Look Ahead game, and an act heading of the midseason page. A standings row, a bracket chip, and the champion trophy of the sim. The verdict word, a factor row, a fold-line avatar, and the swap card of the analyzer. A heading, a word in a blurb, the empty space after the last chapter, and the 404 hero anywhere.

Most eggs belong on old week pages and the midseason page, behind an open state, because those pages never change after they publish.

Cut, with the reason:

- The logo: it is a link home. The footer: the site has none.
- A bare avatar or headshot with no context id: the same image shows in many chapters, and DEF players have no headshot.
- The swipe: it fights the page scroll on a phone.
- The hover and the key code: half the league reads on a phone, and a key code is typed.
- Time on the page and the device: Brian cut them.

If the eggs prove too hard, Brian raises the count of each egg drop.

## Revised 2026-11-07 by Brian

Brian tested the hunt by hand and changed the catalog. The text above stays as the first decision.

- Taps: a double-tap only. The actions `tap3`, `tap4`, and `tap5` are gone. A burst of 3 or more fast taps sends nothing, so a spam of taps finds no double-tap egg. The tap combo stays: tap A, tap B, then a double-tap on C, within 5 seconds.
- Holds: one action `hold`. A press of 2 seconds or more counts, with no upper limit. The holds of 1, 3, and 5 seconds are gone. A press of 1 to 2 seconds sends nothing.
- The 404 page: an egg with `not_found = true` matches on any missing URL, not on one typed path. Its page is `*404`.
- The analyzer: an egg names two teams, and the draft picks them at random. Any graded trade between exactly those two teams matches, in either direction, with any players. The action stays a double-tap on the verdict word. The idea "any trade that the analyzer grades F" stays out of scope.
- Blurbs (2026-11-07): a hold egg never goes on a blurb, because on Android a long press on text selects a word. A blurb may take a double-tap egg. The blurb is one target, so a double-tap anywhere in it counts. The draft and the drop refuse a hold on a blurb.
