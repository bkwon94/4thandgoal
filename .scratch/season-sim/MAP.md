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
- The weekly build writes `week-NN/sim.json`, and the page reads it first and calls the API only for a What-if with a pick. The sim replaces `rankings/odds.py` in full, swings too, at 10,000 runs. The past odds stay. `decisions/02-grill-the-weekly-build.md`.

- A pick uses a conditional draw with a weight, which is exact up to sample noise. 10,000 runs take 0.64 to 0.92 s on the Mac. Fly is about 1 to 1.5 s on burst and 11 to 15 s at the baseline. The API image needs the `sim` package. Sleeper blanks each week of an absence. `decisions/01-research-pick-draw-speed.md`.
- The page answers, for Your team: how many more wins you need (the median counts), the four results of this week with the odds after each, and what to root for if you lose. Layout D "Cards": one week page at a time under a week switch. A tap on a result sets a What-if. The replay is three screens on one stage (season in the Race style, playoffs one round at a time, champion), and "Sim the week" shows games then standings. Each screen is tested at 390x660 WebKit, iPad, and 1280. `decisions/04-prototype-the-sim-page.md`.

## NOT YET SPECIFIED

- How live are the inputs of the What-if, does a season-ending injury lower the level of a team, and what size is the API machine? `decisions/03-grill-live-inputs-injuries.md`.
- How does the live sim hold a median result, and what does one call return? `decisions/07-research-median-result-draw.md`.
- What does the Announcement look like? `decisions/05-prototype-the-announcement.md`.
- What does the weekly report tile show, and how does the page act in the playoff weeks and after the season? `decisions/06-grill-tile-and-season-end.md`.

## OUT OF SCOPE

- A TypeScript copy of the sim in the browser. The API runs the one Python copy, so no parity test is needed.
- A change to the midseason report. It is a published one-time page.
- A pick of a bracket game whose teams are not set. A tree of choices is hard to show on a phone.
- A record of a dismissed Announcement on the server. The site has no accounts.
- A grid to pick any game of any week. Brian's test of round 1 showed that the job of the page is what Your team needs, not a board of every game.
- A cache of live sim answers. The cost is under 10 minutes of CPU each week.
