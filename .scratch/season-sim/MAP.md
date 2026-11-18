# Season sim: map

App: both.
Spec branch: `season-sim`.

## DESTINATION

A sim page for each client at `/sim/<season>/`, which the weekly build rebuilds, with a What-if that the API runs live. An Announcement, a general part of the site, introduces the page to each browser once.

## DECISIONS SO FAR

- The sim gets its own page, which the weekly build rebuilds. Each weekly report gets a tile that links to the page. Brian, 2026-11-18, grill Q1.
- The spec touches both apps: the pipeline runs the sim each week, and the site builds the page. Brian, Q2.
- A manager can pick the winner of each game left, and the odds update. This reverses decision 08 of `midseason-report`. Brian, Q3.
- No date is set, but the release comes as soon as possible, about this week. The playoff weeks are in scope. Brian, Q4.
- The midseason report stays as it is, with its own replay finale. Brian, Q5.
- The look of the page comes from a prototype. Brian, Q6.
- The Announcement is a general component, and the sim is its first use. A dismiss or a press of its link hides it for good in that browser. Brian, Q7.
- The Announcement opens only on page load, never while another sheet is open, and never on the page it links to. It stops 1 week after the release. Brian, Q8.
- New glossary terms: Announcement and What-if. Brian, Q9.
- A What-if picks only the regular-season games left. In the playoff weeks, it picks only the bracket games that are set. Brian, Q10.
- The page opens on Your team, with its odds and the 3 games left that move its odds the most. Brian, Q11.
- The replay stays on the page, and it plays a run that follows the picks. Brian, Q12.
- The sim is the one source of the playoff odds, so the rankings page and the sim page show one number. Brian, Q13.
- The What-if runs live in Python on the API, with no TypeScript copy of the sim. The published `sim.json` holds the odds with no picks. Brian, 2026-11-18. Measured: 10,000 runs take 0.64 s on the Mac.
- The live sim needs no passphrase. A rate cap per visitor stops abuse. Brian, Q15.
- Each pick runs the sim at once. A new pick cancels the call before it. Brian, Q16.
- The spec takes the CPU cost on Fly with no cache. Brian, Q17.

## NOT YET SPECIFIED

- How does a pick fix the winner in the draw, and how fast is a live sim on Fly? How well do the Sleeper projections zero a long injury? `decisions/01-research-pick-draw-speed.md`.
- Where does each week's `sim.json` live, and how do the rankings odds switch to the sim? `decisions/02-grill-the-weekly-build.md`.
- How live are the inputs of the What-if, and does a season-ending injury lower the level of a team? `decisions/03-grill-live-inputs-injuries.md`.
- What does the sim page look like, with Your team, the 3 games, the picks, and the replay? `decisions/04-prototype-the-sim-page.md`.
- What does the Announcement look like? `decisions/05-prototype-the-announcement.md`.
- What does the weekly report tile show, and how does the page act in the playoff weeks and after the season? `decisions/06-grill-tile-and-season-end.md`.

## OUT OF SCOPE

- A TypeScript copy of the sim in the browser. The API runs the one Python copy, so no parity test is needed.
- A change to the midseason report. It is a published one-time page.
- A pick of a bracket game whose teams are not set. A tree of choices is hard to show on a phone.
- A record of a dismissed Announcement on the server. The site has no accounts.
- A cache of live sim answers. The cost is under 10 minutes of CPU each week.
