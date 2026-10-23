# 03 — Odds facts and chapters

**What to build:** the report cites the odds. The engine runs in the facts step of the build, from
week 7 on, with the saved weekly scores, the real records, the next-week pairs, and the remaining
schedule. The sheet gains one `ODDS.{roster_id}` fact per team and one `SW.{a}v{b}` fact per Must
Watch game, with the texts from the spec. The standings chapter cites `ODDS.` with a rule to cite
only the odds that change the story. The next-week chapter cites `SW.`, with a rule to state the
swing for the Must Watch games, and its cap rises to 3 sentences. The rankings chapter may cite
`ODDS.`. The odds land in the saved facts, so a rewrite reuses them and never reruns the engine.
The glossary gains the four terms. Demo: rebuild the week 6 facts, then rewrite the standings and
next-week chapters and read them.

Spec: `.scratch/stakes/PRD.md`, "Facts and chapters".

**Blocked by:** 01 — Schedule fetch, 02 — Odds engine.

**Status:** needs-info

- [x] The facts step runs the engine once per build for the current week, from week 7 on, and the odds are in the bundle.
- [x] `ODDS.{roster_id}` text for `open`: "{team} makes the playoffs in about {p}% of runs, with a bye in {b}%, most often as the {s} seed." The seed clause drops when the seed is none.
- [x] `ODDS.` text for `in`: "{team} has clinched a playoff spot." For `out`: "{team} is out of the playoff race." Neither holds a digit.
- [x] `SW.{a}v{b}` text, one per Must Watch game, pair order as the `NX.` fact: "A win puts {team} at {w}%, a loss at {l}%." once per side.
- [x] Every digit in an odds or swing text is in the fact's numbers, so the existing bundle checks pass.
- [ ] The standings chapter lists `ODDS.` and its prompt gains the "only when it matters, never all 12" rule.
- [x] The next-week chapter lists `SW.`, its cap is 3 sentences, and its prompt gains the "state the swing for Must Watch" rule.
- [x] The rankings chapter lists `ODDS.`.
- [x] A rewrite reads the saved facts and does not call the engine.
- [x] Glossary entries: Playoff odds, Swing, Clinched, Out.
- [x] Tests: the week 6 fixture bundle holds 12 `ODDS.` facts and 2 `SW.` facts; the `in` and `out` texts hold no digit; one prompt text test per new rule; a week before 7 has no odds facts.
- [x] Ruff clean, the full suite passes.

**Open question:** the sheet has no standings chapter. The chapters are motw, game_changer, awards,
position_leaders, recap_{id}, median, next_week, and rankings. The `S.` facts go to median, next_week,
rankings, motw, and each recap. The odds rule is in `writer.md` as rule 23 and covers any chapter. A
decision must say which chapter lists `ODDS.`, or whether a new standings chapter is needed.
