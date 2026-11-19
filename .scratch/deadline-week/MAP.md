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
- Each Finder trade shows the Lean, the Case, and folded Bullets of the Advisor, and opens in the analyzer already graded. Terms: Deadline week, Lock (00:00 Eastern Tue 2026-11-24), Deadline banner, Trade wire, Deadline board. `decisions/04-grill-terms-and-shared-brain.md`.
- The Finder skips the Partner filter for one picked partner, gives the Shortlist variety, and lets an unsure "spares" answer pass. `decisions/01-research-few-offers.md`.
- The Finder gets four free cuts (short offer labels, sheets at the same time, paced waves, late log checks) to about 25 s, keeps one pick call, and streams its progress. No prewarm. `decisions/02-research-finder-speed.md`.
- The Trade wire reads a new Fly route (30 s cache, no rate count) every 60 s until the Lock, and lists every trade of the season with teams, players, and FAAB, week 11 marked new. No draft picks. `decisions/03-research-trade-feed-source.md`.
- One Jev tree, the Spares tree: per-player Nouls "would he start over the weak starter?", chart values as facts, code decides. It replaces the Partner filter questions and feeds the Deadline board. The backtest set is Brian's marks on one week 11 run plus each later bad trade. A change breaks no mark, never lowers the count, and never fits thresholds or names players. `decisions/05-grill-jev-trees-and-backtest.md`.
- The polish fixes two issues from Brian's phone walk: the cause of a failed first call of a trade Topic, with one log line per failed stream, and the bad trade ideas (Walker for Mahomes, Flowers for Goff), which are the first two Backtest marks. `decisions/06-grill-trade-tools-polish-list.md`.

## NOT YET SPECIFIED

- Why does the target step of the Finder want QBs for roster 6, and does the split of the target question move into this spec? `decisions/09-research-qb-targets.md`.
- What does the Finder look like, and how does it show progress while it runs? `decisions/07-prototype-finder-look.md`.
- What do the Deadline banner, the deadline look, the deadline board, and the feed look like? `decisions/08-prototype-event-look.md`.

## OUT OF SCOPE

- A push alert. Brian said it is not necessary.
- Norcal. The dinner is a CPC event.
- A stream of Finder results per partner. It loses the one pick across partners and costs about a day more (decision 02).
- A prewarm of the Finder cache. It costs $0.85 to $1.70 for each roster change (decision 02).
- A theme for the whole site. The deadline look stays on the trade pages and the banner.
- The Accept tree ("would the other manager accept?" split per the playbook). Real trades give only accepted labels, so it needs made-up rejects and its own backtest. After the event (decision 05).
- The split of the target question into "would start" and "would fill a weak spot". After the event (decision 05).
- A Jev tree for fair. A tree that combines fair answers ranks trades by a score, against `no-math-filters` (decision 05).
