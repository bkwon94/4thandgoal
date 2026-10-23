# 03 — Writer rule and the raised cap

**What to build:** the rankings writer cites the why facts. The rankings chapter lists both why
families. Its prompt gains one rule: cite the rank why for every team that moved `WHY_MOVE_AT` or more
places either way; cite the odds why for a team under .500 with odds at or above `WHY_ODDS_AT`, and
for a team over .500 with odds under it. The per-team cap rises from 2 sentences to 3 and the chapter
range to 12 to 36. Glossary entries for the four terms. Demo: rewrite the week 6 rankings chapter on a
copy of the cache in the scratch dir and print it.

Spec: `.scratch/reasons/PRD.md`, "The writer".

**Blocked by:** 01 — Rank why fact, 02 — Odds why fact.

**Status:** done

- [x] The rankings chapter lists `PR.{rid}.why` and `ODDS.{rid}.why` for every team.
- [x] `WHY_MOVE_AT = 2` and `WHY_ODDS_AT = 25` join the tunable table with a one-line why each.
- [x] The writer prompt gains the rule, under 20 words per sentence, with the two thresholds written as digits from the tunables.
- [x] The per-team cap is 3 sentences and the chapter range is 12 to 36.
- [x] Glossary entries: Rank why, Odds why, Projected pace, Season pace.
- [x] One prompt text test pins the rule and the cap.
- [x] Added after the first demo: `Chapter.required` lists the why ids each team must cite, the prompt names them, and the code check fails an uncited one. The prompt rule alone did not hold.
- [x] Ruff adds no finding from the diff; the full suite passes.
