# Egg polish

Status: ready-for-agent
Date: 2026-11-08
Apps: site. The site changes four parts of the egg hunt after the methods of Scrolltide items. The pipeline and the API do not change.
Spec branch: `egg-polish`.
Source: the map `.scratch/egg-polish/MAP.md` and decision tickets 01 to 04, from the session of 2026-11-08. ADR 0024, ADR 0025, ADR 0027, ADR 0028.
Tickets: 01 to 07, in `issues/`.

## Problem Statement

The first egg drop goes live with the weekly publish on Tuesday, 2026-11-10. A league manager on a phone meets the egg hunt at three moments: the find, the claim, and the egg board. Each works, but none of them feels like an event.

The find cracks the egg along the same zigzag every time, so after two finds the crack is only a delay before the letter. The claim ends on a plain button, the same as any form, so the moment a manager wins a letter has no weight. The egg board stacks one card per egg word down the page, and a manager must read the leader line of each card to see how close a race is. The hero of the egg board is the one hero of the site that is not on the hero slots, so the board looks apart from the rest of the site.

## Solution

The hunt feels like an event, and it stays clear and in the look of the site.

1. **The crack starts at the tap point.** A tap squashes the egg. Crack lines spread out from the spot the finger pressed, the egg shakes harder, and light grows inside it. Then the shell bursts into shards, and the letter tile grows out of the tap point. Each find cracks in a new way.
2. **The claim is a tear.** The foot of the claim sheet is a claim ticket that shows the letter, the egg word, and the team. A manager tears the stub off the ticket to send the claim. A tap on the stub tears it too. A claim stamps the ticket CLAIMED.
3. **The egg words are one slider.** One egg word fills the slide at a time, as a giant word that lights the letters of the leader. A tab row above it shows the count of the leader of each word, so the whole race shows at a glance. The closest race opens first.
4. **The egg board hero sits on the hero slots,** so the board reads as one family with every other page.

All four parts are SVG, CSS, and React only, with no WebGL and no new dependency. Under reduced motion, each change is instant.

## User Stories

### The find

1. As a manager, I want the egg to react the moment I tap it, so that the tap feels physical and the egg never seems to lag.
2. As a manager, I want the crack to start where my finger pressed, so that the find feels like my own.
3. As a manager, I want each find to crack in a new way, so that the tenth find still feels fresh.
4. As a manager, I want the egg to shake harder and glow from inside as the cracks spread, so that the moment builds before the release.
5. As a manager, I want the shell to burst into shards from the tap point, so that the letter feels earned.
6. As a manager, I want the letter tile to grow out of the spot I tapped, so that the letter reads as the content of the egg.
7. As a manager, I want the letter and its claim copy to show in about 1.3 s, so that the reward does not keep me waiting.
8. As a manager who uses the keyboard, I want Enter on the egg to crack it from its middle, so that I get the same find.
9. As a manager with reduced motion on, I want the tap to show the letter at once, so that no motion plays.
10. As a manager on an old phone, I want the crack to run on plain SVG and CSS, so that it plays the same as on a new phone.

### The claim

11. As a manager, I want the foot of the claim sheet to be a ticket with my letter, my egg word, and my team, so that I see what I claim before I send it.
12. As a manager, I want the stub to stay locked and name the next missing step until I pick my team and my word and enter the passphrase, so that I know what to do.
13. As a manager, I want to drag the stub to tear it, with the holes of the perforation popping as I pull, so that the claim feels like a real act.
14. As a manager, I want the stub to spring back if I let go early, so that a slip sends nothing.
15. As a manager, I want a tap on the stub to tear it by itself, so that I never get stuck on the gesture.
16. As a manager who uses the keyboard or a screen reader, I want Enter or Space on the stub to tear it, so that the claim needs no drag.
17. As a manager, I want the stub to flutter away and the ticket to show that the claim sends, so that I know the site works on it.
18. As a manager, I want a CLAIMED stamp on the ticket when my claim wins, so that the win lands before the end card.
19. As a manager who was too late, I want a TAKEN stamp and the stub back on the ticket, so that I know at once what happened.
20. As a manager with a wrong passphrase, I want the error text and the stub back on the ticket, so that I can fix the passphrase and tear again.
21. As a manager who claims a block, I want the ticket to show the block in place of an egg word, so that the ticket is true for a block too.
22. As a manager with reduced motion on, I want the stub to leave and the stamp to show with no motion, so that the claim stays clear.

### The egg board

23. As a manager, I want the egg board hero to look like the hero of every other page, so that the board feels part of the site.
24. As a manager, I want the counts of eggs left, found, and to drop in the stats of the hero, so that I see the state of the hunt first.
25. As a manager, I want the grid of eggs by week in the hero, so that I see which weeks still hold eggs.
26. As a manager, I want a tab for each egg word with the count of its leader, such as "CORNERSTONE 4/11", so that I see every race at a glance.
27. As a manager, I want the tabs in a fixed order, so that I learn where each word is.
28. As a manager, I want the board to open on the closest open race, so that the most exciting race shows first.
29. As a manager, I want the giant egg word to light the letters the leader holds and outline the ones the leader needs, so that the title tells me how close the race is.
30. As a manager, I want to swipe or tap a tab to move to the next word, with the giant word swapping letter by letter, so that the move feels alive.
31. As a manager, I want each slide to keep the leader line, the top 5 managers with their tiles, and "Show all", so that I lose no detail of today.
32. As a manager, I want a tie for the lead to say that the managers tie, so that the leader line is true.
33. As a manager, I want a won word to wash red and show the winner and the gift card, so that I see at once that its race is over.
34. As a manager, I want a won word last in the slider, so that the open races come first.
35. As a manager before the first claim, I want the slider to open on CORNERSTONE with all letters as outlines, so that the open race reads clearly.
36. As a manager who uses a screen reader, I want the tab row to be real tabs and each slide to be its panel, so that I can move between words with the keys.
37. As a manager with reduced motion on, I want the word to change at once with no roll and no letter swap, so that no motion plays.

### All parts

38. As a manager on a 390px phone, I want every part to fit with no sideways scroll and 44px tap targets, so that the hunt is easy on my phone.
39. As the commissioner, I want no part to name an egg spot, so that the board never gives a hint.

## Implementation Decisions

### The crack (decision 01)

- The find card keeps its phases, and the crack between them changes. The phases are the egg, the crack, and the letter.
- The tap gives a tap point in the coordinates of the egg art. The point is clamped inside the egg, so a crack never starts on its edge. A tap by the keyboard uses the middle of the egg.
- The squash runs about 0.15 s after the tap.
- Six jagged crack lines draw out from the tap point. The jitter of each line comes from a fresh seed on each tap.
- A light grows inside the egg at the tap point while the lines draw, and the egg shakes harder.
- At about 0.56 s the shell bursts. The two halves fly apart along a zigzag through the tap point, and about seven shards fly out from it. A flash rings out from the tap point.
- The letter tile grows from the tap point out of a blur. The letter and its copy show at about 1.3 s. The constant of the time from the tap to the letter changes to match.
- The crack follows the method of the Contour Reveal item of Scrolltide, so ADR 0028 covers its motion, such as the draw of the lines and the blur of the tile. The hard rules of ADR 0028 still win.

### The claim (decision 02)

- The claim ticket replaces the claim button at the foot of the claim sheet. The three steps above it stay as now: the team, the egg word or the block, and the passphrase.
- The ticket body shows the letter tile, the egg word or the block, and the team. The stub sits at its right edge, past a perforation.
- The locked stub names the next missing step, from the rule of the claim button of now.
- A drag of the stub to the right tears it. The progress is the drag distance over a fixed length, and the holes of the perforation pop from the top down as the progress grows. A full tear sends the claim. A release before it springs the stub back and sends nothing.
- A tap on the stub with no drag tears it by itself. Enter or Space does the same. The stub is a real button with a label that names the claim, such as "Tear to claim N for CORNERSTONE".
- A full tear calls the claim of the API, as the button does now. While the API answers, the stub is gone and the ticket shows a sweep.
- A claim stamps CLAIMED, and then the end card shows as now. Another manager first stamps TAKEN, the stub comes back, and then the end card shows as now. A wrong passphrase shows the error of now, and the stub comes back.
- The tear follows the method of the Tear Ticket item of Scrolltide, written in SVG and CSS with no WebGL. ADR 0028 covers its motion.
- `GLOSSARY.md` gains the term **Claim ticket** in the eggs section: the ticket at the foot of the claim sheet whose stub a manager tears to send the claim.

### The egg word slider (decision 03)

- One slider replaces the word cards and the won cards of the egg board. It renders the board answer of the API, as the cards do now.
- A tab row of the three egg words sits above the slider, in the fixed order CORNERSTONE, LANSDALE, EAGLES. Each tab shows the word and the count of its leader, such as "CORNERSTONE 4/11". A won word tab shows that it is won.
- The tab row is a tablist, and each slide is its tabpanel. The arrow keys move between tabs.
- A horizontal swipe moves to the next or the last slide. A vertical swipe stays a page scroll.
- The giant word is the egg word in tiles. A letter the leader holds is lit in white. A letter the leader still needs is a dim outline. A won word lights every letter in red.
- The leader comes from the ranking of now: the most letters first, and a tie keeps the order of the rosters. The giant word lights the letters of that first manager.
- A tie for the lead changes the leader line, such as "Late Hits and Red Zone tie with 4 of 11."
- Under the giant word, each open slide keeps the leader line, the top 5 managers with their tiles, and "Show all", which opens the full list in place. A won slide shows the winner and the gift card in place of the rows.
- The slider opens on the open word whose leader holds the largest share of its letters. The other open words follow, closest first. A won word goes last. A tie in the share keeps the fixed order.
- A move between slides rolls the slides with a blur on the neighbors, and the giant word swaps letter by letter. An open slide sits on the dark hero ground. A won slide washes the frame into the red accent. No word gets a new color.
- The slider follows the method of the Stack Slider item of Scrolltide. ADR 0028 covers its motion.

### The egg board hero (decision 04)

- The egg board hero moves onto the hero slots of the shared hero part:
  - eyebrow: "Egg hunt".
  - title: "The Egg Board".
  - meta: the line of now: the sum of the gift cards, the count of egg words, and "First to fill a word wins it."
  - feature: the grid of the eggs of each week, with the current week marked, and the legend under it.
  - stats: three tiles for the eggs left to find, found, and to drop, in the colors of now.
  - action: none.
- The hero gets no hero scene. ADR 0027 keeps the scene on the week page, the home Matchup, the manager pages, and the 404. The grid of eggs is already a picture of the data.

### Across the parts

- Each part keeps the stable ids and the marks the egg targets need, so no egg target of the catalog breaks.
- The API, the claim rules, the egg drop, and the board answer do not change.
- No Scrolltide source enters the repo, because it is paid source and the repo is public.

## Testing Decisions

A good test drives a part as a manager does and reads only what shows on the page or what the part sends to the API. A good test never reads an inner state, a class name of an animation, or a timer.

The seams are the ones the eggs package already has. The spec adds no new seam.

1. **The egg hunt component, through its one port.** The tests of the hunt fire real pointer events on the page and read what the hunt sent through the one fake of the port. They cover the tap point and the crack to the letter, the tear by a drag, by a tap, and by a key, the release before a full tear, the locked stub, and each answer of the claim. Prior art: the tests of the egg hunt and of the egg hunt with motion off.
2. **The egg board component, from the board fixture.** The fixture is held to the real answer of the API by the API tests. The tests cover the tab row, the order of the slides, the lit letters of the giant word, a tie, a won word, the board before any claim, and the hero slots. Prior art: the tests of the egg board.
3. **The browser, at the floor.** Playwright runs the path of a manager on the served build at 390px. It finds the test egg, cracks it, tears the stub, and sees the claim on the egg board. The floor check runs axe and the 390px rules on the claim sheet and the egg board. Prior art: the e2e test of the eggs and the floor check.

## Out of Scope

- The egg button and the egg banner. They are signposts, and the time before Tuesday is short.
- The Block Field, Unfurl, Step Path, Particle Text, and Crumple Reveal items of Scrolltide. Each is a candidate for a later spec.
- Any change to the API, the claim rules, the egg drop, or the board answer.
- A tint for each egg word. The brand has one accent.
- A hero scene on the egg board.
- The latest claims and how the hunt works, under the slider. They stay as now.

## Further Notes

- The spec must merge and deploy before the first egg drop on Tuesday, 2026-11-10. If time runs short, the claim tear goes last, because the claim is the one step that must not break on Tuesday. The button of now stays until the tear passes.
- The canvas of the prototypes is https://claude.ai/artifact/HaTnYegqcyt1VS9eh1c1wq. It holds the three crack variants and the claim tear. The chosen crack is variant B, with the squash of variant A.
- Decision 03 said "the top 3 managers". The card of now shows the top 5, so the spec keeps 5.
