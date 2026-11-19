# Deadline week: map

App: both. The site, the API, and the pipeline package that the API imports.
Spec branch: `deadline-week`.

## DESTINATION

One spec makes the trade deadline of week 11 a special event on the CPC site, live by Fri 2026-11-20 night. The event turns off by itself after Sleeper locks trades on Mon 2026-11-23 night. The Finder turns on in CPC only after Brian checks it on the phone.

## DECISIONS SO FAR

- CPC only. Live by Thu 2026-11-19 night, Fri 2026-11-20 night at the latest. Sleeper locks trades after the week 11 games end, on Mon 2026-11-23 night. Brian, in the Stage 1 grill.
- All four parts are in: the event, the Finder, the Jev questions, and the polish. The flag `finder` stays off in CPC until Brian checks the Finder on the phone and says go. Brian, in the Stage 1 grill.
- The event holds the Deadline banner with a countdown, a deadline look on the trade pages, a deadline board, a live feed of Sleeper trades, and a closed state after the lock. Brian, in the Stage 1 grill.
- Jev answers tiny yes or no questions, and code combines the answers in a decision tree. Each bad case joins a backtest set. Source: the Rivet post that Brian shared, and the 28 labelled trades of manager-brain.
- The UI uses `ui-sdk`, parts from scrolltide and transitions.dev, and the design skills of design-bar. Brian, in the Stage 1 grill.

## NOT YET SPECIFIED

- Why does the Finder give no offer or one offer, and which step cuts the most? `decisions/01-research-few-offers.md`.
- Where does the Finder spend its time, and can it be fast enough without a stream? `decisions/02-research-finder-speed.md`.
- Where does the live feed of trades get its data, and how often? `decisions/03-research-trade-feed-source.md`.
- What are the terms of the event, and how do the Finder and the analyzer share one brain and one voice? `decisions/04-grill-terms-and-shared-brain.md`.
- Which Jev questions and which decision trees does the Finder use, and what bar must the backtest pass? `decisions/05-grill-jev-trees-and-backtest.md`.
- Which issues of the trade tools does the polish fix? `decisions/06-grill-trade-tools-polish-list.md`.
- What does the Finder look like, and how does it show progress while it runs? `decisions/07-prototype-finder-look.md`.
- What do the Deadline banner, the deadline look, the deadline board, and the feed look like? `decisions/08-prototype-event-look.md`.

## OUT OF SCOPE

- A push alert. Brian said it is not necessary.
- Norcal. The dinner is a CPC event.
- A theme for the whole site. The deadline look stays on the trade pages and the banner.
