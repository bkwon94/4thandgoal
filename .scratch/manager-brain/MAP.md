# Manager brain: map

App: both. The pipeline package `analyzer`, the API, and the analyzer page of the site.
Spec branch: `manager-brain`.

## DESTINATION

One spec that changes the analyzer and the Finder to judge a trade as a manager of the league does. Code gives the facts and the candidates, Jev gives the small judgments at scale, and Claude makes the call and writes it.

## DECISIONS SO FAR

- Claude judges from a fact sheet, and code gives the facts. The rubric and the adjusters move no letter. Brian, 2026-11-09, in the Stage 1 grill.
- One spec covers the analyzer and the Finder, so the two never disagree on one trade. Brian, 2026-11-09.
- No letter grade. The judge gives the decision for the asker, the fairness, and the reasons. The page already shows no letter (`analyze-result.tsx:3`). Brian, 2026-11-09.
- The roles: code gives the facts, the candidates, and the hard rules. Jev answers atomic manager questions at scale, and later checks the text. Claude makes the final call and writes it. Brian, 2026-11-09.
- The judge is a league-mate who advises the asker. It gives an honest read of the other manager, in the voice folder of the client. Brian, 2026-11-09.
- The page keeps the hero, the fairness line, and the swap card. The factor rows become 3 to 5 manager bullets per side, each with a fact and a lean mark. A Finder trade gets 2 to 3 bullets. Brian, 2026-11-09.
- The adjusters stay as measures and become facts with no step. Known bad reads get a fix as facts, such as the Trend that reads only snaps. The rubric, the start letter, the breakdown, and the rank by steps go. Brian, 2026-11-09.
- The guards: the check that each number and name comes from the sheet stays, and so does the check on inner words. The upside rule and the letter rule go. A Jev faithfulness check starts log-only. Brian, 2026-11-09.
- The fallback: after two failed Claude calls, the analyzer shows an honest error and the call does not count toward the grade limit. The Finder shows the Jev shortlist with plain fact lines and a fallback flag. Brian, 2026-11-09.
- The Finder searches all partners. Jev first asks four questions per partner: does he have your need, can he spare it, do you have his need, can you spare it. Code counts the depth, and only the partners with four yes answers get a full search. The partner picker stays as an option. With no match, the Finder says so in plain words. Brian, 2026-11-09.
- The test set has 30 trades with stats as of their week. Brian gives a playbook and reacts to the prototype output, and his reactions are the key. `decisions/01-grill-answer-key.md`.
- The hero shows one of five leans: Send it, Lean yes, Gut call, Lean no, Pass. The judge advises in Brian's voice, with a condition, and backs claims with data. `decisions/01-grill-answer-key.md`.
- Each client has a playbook in its voice folder. The cpc playbook: RBs first in half PPR, a gut call on trends and schedule, contenders firm up, bubble teams take risks, a top 3 to 5 player beats two good ones, managers here chase recent points, usage trends matter. `decisions/01-grill-answer-key.md`.
- History claims carry a past-season split from the sheet. With no split, Claude may state history in words but with no number. `decisions/01-grill-answer-key.md`.
- The terms: Advisor, Grade with no letter, Lean and Case, Bullets with a Mark, Measure, Playbook, Partner filter, Shortlist. The race group and the odds replace Contender, Seller, and Middle team. ADR 0030 records the change. `decisions/02-grill-glossary-terms.md`.
- The trade value chart is one fact with no gates: unlisted players stay in the Finder, a week with no chart still works, and the playbook wins over the chart. The chart cache trusts a hash of the PNG, not file times, and one manual step gives a chart before a build. `decisions/07-grill-chart-role.md`.
- The finder narrows with no math filter: the partner filter, then Jev picks the targets on each side, code builds the offers from the targets only, Jev makes the shortlist, and the Advisor picks three. Code keeps only the hard rules. `decisions/03-research-search-cost.md`.
- History comes from the nflverse weekly player file for the last 3 seasons, cached for good: weeks 1 to 8 against weeks 9 to 17, and cold games, each with its game count. `decisions/06-research-history-splits.md`.

## NOT YET SPECIFIED

- Which Advisor arm does Brian agree with most, what are the exact Jev questions, and do the targets make sense? `decisions/04-prototype-judge-arms.md`.
- What layout do the bullets and their marks take on the page? `decisions/05-prototype-bullet-layout.md`.

## OUT OF SCOPE

- Trades of 2-for-2 and larger in the Finder. Keep the candidate shapes the same, so a gain comes from the judge alone.
- A free-text trade request, such as "find me a WR". It is a later spec on the Jev roadmap.
- The Jev checks of the weekly copy. The `jev` spec and its later specs own them.
