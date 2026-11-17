# Analyzer stage: the trade on stage, and hero text with no plate

Status: ready-for-agent
Date: 2026-11-16
Apps: site only. The analyzer hero gets the mesh, the stage lines, and the staged reveal. Every hero drops the plate. The pipeline and the API do not change.
Spec branch: `analyzer-stage`.
Source: the map `.scratch/analyzer-stage/MAP.md` and decision tickets 01 to 06. ADR 0035 (one wrapper per ui-sdk part), ADR 0036 (hero text has no plate).
Tickets: 01 to 10, in `issues/`. The revision of 2026-11-17 added 08 to 10.

## Problem Statement

A grade can take up to a minute. During that minute the analyzer hero shows two grey bars and a red sweep. Nothing on the screen tells the reader that the trade they built is the thing on the scale. The wait feels long and empty, and the result then appears all at once, with no moment of arrival.

Every hero of the site also sets its text on a plate: a dark box of the band color with a soft shadow. Where the box sits on the red corner glow, it shows as a dark patch behind the text. Brian finds it ugly.

## Solution

The analyzer hero becomes a stage with three states: idle, wait, and reveal.

1. **Idle.** The hero grid is a live mesh that matches the old 24 px grid, calm and flat. The stage shows one slim row per side, with the team and a count of its players. The headshots wait for the grade.
2. **Wait.** The grade button goes pending and the wait starts at once. The headshots of each side rise into its row. The mesh dips under each side of the trade in turn, so the hero reads as "weighing the sides". Sparse light pulses run along the mesh lines. Short stage lines cycle under the title, one every 2.5 s. No line says that a step is done, because the analyze call has no progress to report.
3. **Reveal.** The lines of the favored side flash once. The mesh dips toward the favored side and goes flat. Then, in about 1 s, the Lean word lands, the Lean scale fills, and the Case and the side tabs rise in.

The stage is the one place on the page that shows the players of the trade. Under a result, the cards below the hero hold the reasons, not the players again. Edit sits in the header of "The Sides".

With motion off, the mesh is still and flat, the stage lines change with no shimmer, and the reveal is a plain fade.

Every hero of the site drops the plate. The corner glow of the static hero art is smaller and lower, so its bright part never reaches text (ADR 0036). The analyzer hero draws its own glow on its canvas, and cuts a soft hole in the mesh under each text block instead.

## User Stories

1. As a reader on the analyzer, I want the hero to show the trade I build, so that the page feels like it is about my trade.
2. As a reader, I want each player I add to show on the stage, so that I see the trade grow before I grade it.
3. As a reader, I want the idle hero to stay calm, so that it does not pull my eye from the Stack while I build.
4. As a reader, I want the wait to start the moment I tap "Grade the Trade", so that I know my tap counted.
5. As a reader, I want the hero to move during the wait, so that I see that work goes on.
6. As a reader, I want the motion to weigh one side and then the other, so that the wait tells me what the grade does.
7. As a reader, I want short lines that change during the wait, so that a wait of up to a minute does not feel empty.
8. As a reader, I want some lines to name the players and the teams of my trade, so that the wait feels like it is about my trade.
9. As a reader, I want no line to claim that a step is done, so that the page never tells me something false.
10. As a reader, I want no fake delay, so that a fast grade shows at once.
11. As a reader, I want the result to arrive in a short staged reveal, so that the Lean feels like a moment.
12. As a reader, I want the Lean word to come first in the reveal, so that I get the answer before the detail.
13. As a reader, I want the mesh to dip toward the favored side, so that the motion agrees with the Lean.
14. As a reader with reduced motion, I want a still hero and a plain fade, so that the page does not move.
15. As a reader with reduced motion, I still want the stage lines to change, so that I know the grade runs.
16. As a reader with a screen reader, I want one "Grading the trade" message, not a new message every 2.5 s, so that the wait is not noisy.
17. As a reader with a screen reader, I want the focus to stay on the grade button during the wait, so that I do not lose my place.
18. As a reader, I want the grade button to look and act like the other pending buttons of the site, so that the page feels like one system.
19. As a reader on a phone, I want the mesh to stay smooth, so that the wait does not stutter or drain the battery.
20. As a reader of any hero, I want text with no dark box behind it, so that the hero looks clean.
21. As a reader of any hero, I want every text to stay readable over the grid and the glow, so that I never strain to read it.
22. As a reader of the week hero, I want the losing score to stay readable, so that the muted text is not lost on the red glow.
23. As a reader of the analyzer hero, I want each text to stay readable while the mesh moves, so that the wait and the reveal are readable at every frame.
24. As a reader of the norcal site, I want the same readable heroes, so that both clients get the same quality.
25. As the commissioner, I want each hero to pass the readability floor, so that no change ships with weak contrast.
26. As a future builder, I want the reason the plate went in an ADR, so that no one puts the box back by habit.
27. As a future builder, I want a contrast check that reads the art layer, so that a later change to the glow cannot fail contrast unseen.
28. As a reader of the Finder, I want its wait to stay as it is, so that a page with no trade on stage does not show a scale that weighs nothing.
29. As a reader with a big trade, I want the stage to stay compact, so that a trade of 4 sides and 10 players still fits the hero.
30. As a reader who builds a trade, I want the players once on the page, so that the hero and the Stack do not repeat each other.
31. As a reader of a result, I want the players once on the page, so that the reasons sit near the top on a phone.
32. As a reader of a result, I want Edit near the sides of the trade, so that I can change the trade without a long scroll and with nothing over the result.
33. As a reader of a long fairness reason, I want it to fold, so that one side does not push the others off the screen.
34. As a reader in the wait, I want each stage line in full, so that no line is cut off at the edge of the hero.

## Implementation Decisions

### The stage (decision 01)

- The analyzer hero ground is a live mesh on a Canvas 2D, with no WebGL. Idle draws a flat mesh at the 24 px pitch of the hero grid. The build may start from the scrolltide items `mesh-flow` and `light-cove`, but it rewrites them. It does not copy the prototype in `~/plans/analyzer-stage-prototype/`.
- Wait: a weight under each side pulls the mesh down in turn, 1.25 s per side. A trade of three or more sides cycles through each side. Accent pulses, with a bright head and a soft tail, run along the mesh lines and bend with the mesh. A pulse runs faster near a weight that pulls.
- Reveal: the lines of the favored side flash once and fade in about 0.6 s. The mesh then dips toward the favored side and goes flat. A Gut call has no favored side, so the mesh settles flat with no dip.
- The staged reveal of about 1 s follows: the Lean word, then the Lean scale, then the Case and the side tabs. The result cards under the hero use the skeleton reveal recipe of transitions.dev. The Case uses its texts reveal recipe.
- The canvas draws the corner glow low in the bottom-right corner, away from the labels and the chips.
- The canvas cuts a soft hole in the mesh and the glow under each text block and each chip. The hole dims the art only in part, so it never reads as a dark halo. A small muted label gets a deeper hole.
- The canvas pauses when the hero leaves the viewport or the tab hides, and it caps its frame work on a phone.
- With motion off: a still, flat mesh, no pulses, and a plain fade for the reveal.
- The wait has no minimum time.
- The analyze call stays one `POST` with no stream.

### The grade button (decision 01)

- The grade button wraps the ui-sdk `Button`. Under ADR 0035, the wrapper sits in the ui folder of the design package, and no other file imports `@ui-sdk`. The ui folder already holds a shadcn button that other parts use, so the wrapper takes its own name and the shadcn button stays.
- Its click handler returns a Promise, so the button goes pending. It gets `aria-busy`, `aria-disabled`, and `data-pending`, and it keeps focus through the wait. Its pending announcement is "Grading the trade".
- The pending state starts the wait of the hero.
- The label stays "Grade the Trade" while it is pending. The ui-sdk docs advise against a change of text while a button is pending, and the hero already carries the wait. The prototype morph to "Grading…" does not ship.

### The compact stage and Edit (decision 06)

- The stage is one slim row per side, asker first. A row shows the team avatar, the full team name, "gets", then the headshot tokens. The name truncates with an ellipsis when it does not fit.
- A row shows up to 3 headshot tokens, overlapped, then a "+N" token for the rest. A headshot that fails to load shows the initials of the player.
- Idle: a row shows the team and a player count, such as "5 players". A side with no player shows a dashed empty token. No headshot shows in idle, because the Stack below already shows each player.
- Wait: on the pending state of the grade button, the headshots rise into each row, with a stagger by row and by token, and a blur that clears. With motion off, the tokens fade in.
- Result: the same rows sit on the `ReadHero`. The mesh anchors of the rows replace the empty columns, so the dip of the reveal sits under the right row.
- The "The Trade" chapter, with the `SwapCard`, leaves the result. The `SwapCard` stays in the Finder.
- Each panel of "The Sides" keeps its bullets and its week lines, and drops `SidePlayers`.
- In the fairness block, a reason longer than about 3 lines folds, with a "More" control that opens it.
- The `FoldLine` card leaves the page. The stage already shows the trade in the wait and under a result.
- Edit is a text button with a pencil icon at the right of the "The Sides" header. A tap opens the Stack and scrolls to it. The button has a touch target of at least 44 px.
- The players lose their rank lines on the result, because only the hero shows them now. A later ticket can bring the ranks back on a tap of a token.

### The stage lines (decision 02)

- One pure function builds the list of lines from the trade on the stage. Each line names no internal part. It never says Jev, Advisor, Finder, or front door. It says "manager", never "rival".
- No line says that a step is done or finished, and no line gives a percent or a count of steps.
- The list has 12 lines. Lines 1 and 12 are fixed. The lines between them mix general lines with lines that name a player or a team of the trade. A line with a name takes the name from the trade on the stage, so a trade of two players still gets 12 lines.
- Line 1 is "Weighing the sides". Line 12 is "Weighing it all together".
- The general lines come from the measures of the grade, so each one is true: roster fit, standing, trend and usage, injury, upside, schedule, and the playoff race. Examples: "Checking roster fit", "Reading the standings", "Looking at the schedule ahead", "Reading recent usage".
- The lines with a name follow these shapes: "Reading {player}'s season", "Checking {team}'s depth at {position}", "Weighing what {manager} gives up". The trade on the stage gives each value. The function picks names from each side in turn.
- Each line shows for 2.5 s. After line 12, the list starts again at line 2. The line uses the thinking states and the shimmer text recipes of transitions.dev.
- The line is set at `text-body`, one step smaller than `text-lead` (decision 06).
- A line that does not fit the width of the hero scrolls into view from right to left, once, inside its 2.5 s, and never shows cut off. A line that fits does not move.
- With motion off, a long line wraps to a second line and does not scroll.
- The lines are hidden from a screen reader. The status region keeps one label, "Grading the trade", so a screen reader hears one message.
- With motion off, the line swaps with no shimmer and no slide.
- Brian may change the copy of any line at the approval of this spec.

### The Finder (decision 03)

- The Finder wait keeps `Sweep`. The mesh weighs the sides of a trade, and a Finder search has no trade on stage yet. The Finder is also off in cpc now.
- `Sweep` stays in the design of the Finder only. The grade wait no longer uses it.

### Hero text with no plate (decisions 04 and 05, ADR 0036)

- The `plate` utility leaves the site, with every use: the hero slots, the week hero, the manager hero, the grade dial, the grade popover, the midseason opener, the 404 page, the egg banner, and the analyzer result.
- The utility also added vertical padding and a negative inline margin. Both go with it. The hero slots keep their gaps, so the text sits a little tighter. The polish pass checks the rhythm of each hero by eye.
- The glow of the static hero art becomes `radial-gradient(ellipse 38% 46% at 100% 112%, var(--color-accent-glow), transparent 70%)`, from the prototype of decision 05. The old glow was `ellipse 70% 90% at 100% 100%`. The grid does not change.
- The egg banner has its own hero texture, so it takes the same glow.
- The comments that say a hero text sits on a plate change to say why the text needs none.

### The glossary

- **Stage line**: one short line under the analyzer title during a grade wait. It never says that a step is done.
- **Mesh**: the live grid art of the analyzer hero, which weighs the sides of the trade during a grade wait.
- The terms go into `GLOSSARY.md` with this spec. The term "hero scene" does not change: the mesh is not a hero scene, because it fills the whole hero and sits under text.

## Testing Decisions

A good test checks what the reader sees and hears: the text, the states, the order, and the contrast. It does not check the inner math of the mesh or the names of private functions.

### The seams

1. **The readability floor**, the e2e test of the static export in each client. It already runs on the analyzer, the manager pages, and the 404 page. Every hero text must reach 4.5:1 there.
2. **The analyzer e2e test against the local API**, through the evidence harness. It drives idle, wait, and reveal on a real grade. The test holds the analyze request with a Playwright route until it has its samples of the wait, then passes the request on to the real local API. The request is real, and the test adds only a delay.
3. **A unit test of the stage line function**, in vitest. It checks the list for a trade of two players and for a trade of three sides.

Brian checks these seams with the spec.

### The contrast of the art layer

- Axe gives an incomplete result for text over a gradient or a canvas. The floor fails an incomplete result now, so the plate removal fails the floor unless the floor changes.
- The floor gets a pixel scan of hero text, after the method of the prototype of decision 05. The scan hides the text of each hero, takes a screenshot, finds the brightest pixel under the box of each text, and compares it with the color of the text.
- An axe incomplete result passes to the pixel scan only when its node sits inside a hero and its reason is a background image, a gradient, an overlap, or content too short for axe to judge. Every other incomplete result still fails.
- The pixel scan also reads hero text inside an aria-hidden part, such as the big digits of the 404 page. The pixel scan must find at least one text in each hero, so an empty scan fails.
- On the analyzer hero, the scan samples the wait at least 10 times over 3 s and keeps the worst ratio, because the mesh moves. It also samples idle and the end of the reveal.
- The scan runs in both clients, at 390 px and 1280 px.

### What the tests check

- The floor: every hero text reaches 4.5:1 in each client and each width, including the analyzer in idle, wait, and reveal, and the egg banner where eggs are on.
- The analyzer e2e test: the wait starts on the tap, the stage lines change about every 2.5 s, the lines name a player of the trade, the reveal shows the Lean word before the Case, the focus stays on the grade button through the wait, and motion off gives a still hero.
- The analyzer e2e test, for decision 06: idle shows a count and no headshot, the wait shows the headshots, a side of more than 3 players shows "+N", the result has no "The Trade" chapter and no player list in "The Sides", Edit in "The Sides" header opens the Stack, and a long stage line is never cut off at 390 px.
- The unit test: 12 lines, the fixed first and last lines, a name of the trade in at least one line, no internal name, no "rival", and no word of completion such as "done" or "finished".
- No test checks that a plate is absent by its class. The pixel scan and a screenshot are the evidence.

### Prior art

- The floor scans in `apps/site/e2e/floor.ts` and `floor.spec.ts`.
- The evidence harness in `apps/site/e2e/evidence.ts`, which reaches the local API.
- The held routes of `front-door-kept.spec.ts`.
- The analyzer unit tests in the analyzer form package.
- The prototype contrast script in `~/plans/analyzer-stage-prototype/plate-05/`, as a reference for the pixel scan.

## Out of Scope

- The wait of the front door chat. It is a chat surface with its own motion. A quick run can bring the mesh there later.
- Real progress from an API stream. It moves a seam in both apps and makes the spec about twice as big.
- A new loader for the Finder wait. It keeps `Sweep`.
- A change to the hero scene of the other pages. It keeps its own row, so no light sits under text.

## Further Notes

- Every UI ticket follows the design bar: transitions-dev and transitions-polish, apple-design, animate, emil-design-eng, make-interfaces-feel-better, critique, and polish. Brian checks the mesh on his iPhone before the PR.
- Round 5 of the decision 01 prototype measured 2.45:1 for the column label of the other side during the wait. The holes of the canvas must fix that, and the pixel scan proves it.
- The norcal client has a darker band and an orange accent. Its glow must pass the pixel scan too.
- `next dev` printed a security advisory for Next.js 16.4.2. That upgrade is not part of this spec.

## Revisions

- 2026-11-16: Brian widened the pixel scan after ticket 02 found two axe incomplete results with no plate: the reason "content too short", on the week numbers and the score parts, and the aria-hidden 404 digits. Both now go to the pixel scan. The bar stays 4.5:1.
- 2026-11-17: Decision 06 adds the compact stage and moves Edit. The stage shows one row per side. The headshots appear only from the wait on. The result drops the swap card, the side player lists, and the `FoldLine`. Edit moves to the header of "The Sides". The stage lines go one size smaller and scroll when too long.
