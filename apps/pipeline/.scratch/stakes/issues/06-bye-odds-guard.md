# 06 — Bye odds never show 0 or 100 without proof

**What to build:** a bye number follows the same rule as the playoff number. It shows 0 only when the
team cannot reach the 2nd seed with 2 wins in every remaining week, and 100 only when no team outside
the top 2 can reach its wins the same way. Every other bye shows a whole percent from 1 to 99, capped at
the shown playoff odds. A team that is `out` shows a bye of 0, since no playoffs means no bye. A team
that is `in` with an open bye shows 1 to 99. Brian's rule, 2026-10-23: a percent is never 0 unless it is
truly 0.

Spec: `.scratch/stakes/PRD.md`, "The engine", the status and clamp lines.

**Blocked by:** None — can start immediately.

**Status:** done

- [x] A plain check for the bye: `bye_sure` when no team outside the top `bye_count` by wins can reach the team's wins with 2 wins per week left; `bye_gone` when the team cannot reach the wins of the team in the last bye spot the same way.
- [x] The shown bye is 100 for `bye_sure`, 0 for `bye_gone` or for status `out`, else the rounded share clamped to 1 to 99 and capped at the shown playoff odds.
- [x] With no weeks left the real table sets the bye to 100 or 0.
- [x] The `ODDS.` fact text and the rankings row use the shown bye as before; no text change.
- [x] Tests on the 4-team fixture: a bye of 0 only with `bye_gone`; a team the sim never gives a bye but that can still catch 2nd shows 1; `bye_sure` shows 100; the cap at the playoff odds holds; `out` gives 0.
- [x] The spec's engine section gains one line on the bye rule.
- [x] Ruff adds no finding from the diff; the full suite passes.
