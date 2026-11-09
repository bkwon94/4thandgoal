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

## NOT YET SPECIFIED

- Which trades make the answer key, and what is Brian's answer for each? `decisions/01-grill-answer-key.md`.
- Which glossary terms go, which change, and which are new? `decisions/02-grill-glossary-terms.md`.
- What does the search across all partners cost, and how long does it take, on real rosters? `decisions/03-research-search-cost.md`.
- Which judge wins against the answer key, and what are the exact Jev questions and the shortlist table? `decisions/04-prototype-judge-arms.md`.
- What layout do the bullets and the lean marks take on the page? `decisions/05-prototype-bullet-layout.md`.

## OUT OF SCOPE

- Trades of 2-for-2 and larger in the Finder. Keep the candidate shapes the same, so a gain comes from the judge alone.
- A free-text trade request, such as "find me a WR". It is a later spec on the Jev roadmap.
- The Jev checks of the weekly copy. The `jev` spec and its later specs own them.
