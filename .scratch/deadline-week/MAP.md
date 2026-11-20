# Deadline week: map

App: both. The site, the API, and the pipeline package that the API imports.
Spec branch: `deadline-week`.

## DESTINATION

One spec makes the trade deadline of week 11 a special event on the CPC site, live by Fri 2026-11-20 night. The event turns off by itself after Sleeper locks trades on Mon 2026-11-23 night. The Finder turns on in CPC only after Brian checks it on the phone.

The Finder is fair-first: it finds fair trades of four shapes by chart value, and shows varied ideas, not only need fills. Source: `.handoff/deadline-week-fair-finder.md`, Brian's rulings of 2026-11-19.

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
- No step asked what the asker gives up. The Spares tree runs on the give side, with a depth count of players who can play now, and the Shortlist gets one gain Noul per side with lineup points as facts. A clear no drops the offer. The target split stays out. `decisions/09-research-qb-targets.md`.
- The analyzer hero gets a switch, "Grade a trade · Find a trade", and the Finder takes the Stage look. Its wait uses the same `StageLines` as the grade, fed by the real steps, plus team avatars that light up. `decisions/07-prototype-finder-look.md`.

- No Deadline Board. The whole Deadline banner opens the Trade Wire in a sheet, with "Grade a trade" and "Find a trade" at its top. Week 11 trades only, a 5 s cache and a 10 s poll. Copy says "trade deadline", never "Lock". `decisions/08-prototype-event-look.md`.

- The Spares tree lists a player when his team has a backup above the line behind him who can play now: 117 of 132 pairs. `decisions/12-spec-spares-tree-reading.md`.
- Without a screen, a press has 95k to 242k candidates, and a 5% band leaves 4k to 10k. One fair Noul each costs $0.02 to $0.05 but runs 5 to 11 times over the rate limit. `decisions/13-research-candidate-size-and-cost.md`.
- The Value screen: four shapes in both directions, the side that gets more players gets 100% to 125% of the other sum, 1-for-1 within 10%, a floor of 5 per player on a multi-player side, no cap. ADR 0038 limits the exception to `no-math-filters`. `decisions/14-grill-value-screen.md`.
- Jev questions in two steps: fair on every offer, asked in both side orders and averaged in code, with chart values in the state; then need and gain on the offers that pass. A clear no on fair or on a gain drops the offer. Need is a reason. The Spares tree builds no offers; its answers are reasons. `decisions/15-grill-jev-questions-per-shape.md`.
- The Value screen is the one source of offers; the targets step and the wider pass go. Spares tree yeses become pick sheet facts. Step 2 gets the best offer per partner and shape direction. The score is fair alone. `varied()` puts the best per shape, then per partner, then per player first, in a Shortlist of 10. One shared pacer per API process. `decisions/16-grill-merge-and-variety.md`.
- The card is A · Ledger: You get and You give columns with rank per player, a trade value total per side, and one plain gap line. 5 picks plus up to 3 near ideas. New wait lines with real counts. A to J labels stay. No time claim in the wait. `decisions/17-prototype-shape-cards.md`.

## NOT YET SPECIFIED

- Which acceptance tests change? `decisions/18-spec-changed-acceptance-tests.md`.

## OUT OF SCOPE

- Why the week 11 chart has no value for 29 pool players. A follow-up; the Spares tree still offers them (decision 14).

- A push alert. Brian said it is not necessary.
- Norcal. The dinner is a CPC event.
- A stream of Finder results per partner. It loses the one pick across partners and costs about a day more (decision 02).
- A prewarm of the Finder cache. It costs $0.85 to $1.70 for each roster change (decision 02).
- A theme for the whole site. The deadline look stays on the trade pages and the banner.
- The Accept tree ("would the other manager accept?" split per the playbook). Real trades give only accepted labels, so it needs made-up rejects and its own backtest. After the event (decision 05).
- The split of the target question into "would start" and "would fill a weak spot". After the event (decision 05).
- A Jev tree for fair. A tree that combines fair answers ranks trades by a score, against `no-math-filters` (decision 05). The Value screen of decision 14 is the one math cut, by ADR 0038.
- A Finder for three-team trades. About $0.11 and 31 to 33 s for each press, and 3 to 4 days of build. Brian scrapped it (decisions 10, 11).
- The Deadline Board. The Finder answers the same question for one manager, and real needs and spares need the Spares tree on each team (decision 08).
