# The Advisor judges, and code measures

Status: accepted. The spec `manager-brain` builds it. Prototype 04 of that spec set the work of Jev and of Claude.

The analyzer and the finder graded a trade with a rubric. The chart ratio gave a start letter, and seven
adjusters each moved it by one step. Brian found that the rules "sometimes work, but also often (more times
than not) don't work". The week 8 finder called Gibbs for Bijan and Henry for Tuten and Higgins good for
both. Each fix added one more rule, and each new rule had its own edge cases. We decided that the trade
analyzer advises as a manager of the league does, and code no longer grades.

## The roles

1. **Code measures.** It builds the trade fact sheet: the chart value, the ranks, the trends, the race
   group and the odds, the injuries, the schedule, the depth, and past-season splits. It lists the
   candidates of the finder and checks the hard rules: a legal trade, real players, and no number that
   is not on the sheet. A measure moves nothing.
2. **Jev judges small things at scale.** It answers atomic questions, such as "can he give that player up
   with no hole in his lineup?". It runs the partner filter and the shortlist of the finder, where a
   Claude call per candidate costs too much. Later it checks that each bullet follows from its fact.
3. **Claude, the Advisor, makes the call.** It reads the facts, the Jev answers, and the playbook of the
   client. It gives the lean, the case, the fairness, and the bullets, in the voice of a manager who
   advises the asker.

## What goes

The rubric, the start letter, the breakdown, the adjuster steps, the rank of the finder by the sum of
steps, the letter of a side, and the factor rows of the page. Each adjuster becomes a measure.

## Considered options

- **Keep the rubric and let Claude overrule it.** Rejected because the bad steps still anchor the call,
  and the finder keeps the same bugs.
- **Jev gives yes or no alone.** Rejected for now: one probability gives no reason, and a close trade
  lands near 0.5. Prototype 04 tests it as one arm.
- **Jev answers atomic questions and a code table decides.** Rejected for now because a table of weights
  brings back the sum of steps. Prototype 04 tests it as one arm.

## Consequences

- The same trade can get a different read on two calls. The result cache of a week covers a repeat.
- A failed Advisor call shows an honest error in the analyzer, not a code answer. The finder falls back
  to the Jev shortlist with plain fact lines.
- ADR 0003 is superseded in part: roster fit stays as a measure of depth, but it moves no letter.
- ADR 0004 is superseded in part: a bye in the trade week is a fact of the sheet for every side, and the
  Advisor weighs it with the race group.
- ADR 0005 and ADR 0009 stand as measures.
- The glossary drops Rubric, Start letter, Breakdown, Adjuster, Factor, Verdict, Decision, Answer,
  Contender, Seller, and Middle team. It adds Advisor, Playbook, Lean, Case, Mark, Measure, Partner
  filter, and Shortlist. Grade now means the whole read, with no letter.
