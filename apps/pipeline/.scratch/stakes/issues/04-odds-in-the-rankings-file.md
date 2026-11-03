# 04 — Odds in the rankings file

**What to build:** the rankings file carries the odds, so the site can show the `Playoff %` column.
Each row of the current week gains an optional `odds` object: `playoff` and `bye` as whole numbers,
`seed` as a number or null, `status` as `in`, `out`, or `open`. Rows of past weeks keep no `odds`
key. The schema version stays 1. The publish step copies the file as it does today. Demo: run the
rankings write for week 6 on the fixture and read the file.

Spec: `.scratch/stakes/PRD.md`, "The rankings file and the site".

**Blocked by:** 03 — Odds facts and chapters.

**Status:** done

- [x] The rankings writer takes the odds of the current week and puts an `odds` object on each of its rows.
- [x] The object holds `playoff`, `bye`, `seed` or null, and `status`.
- [x] Rows of past weeks have no `odds` key, and the file never shrinks.
- [x] The schema version stays 1.
- [x] Tests: the current week's rows carry `odds`; a past row does not; a rerun keeps the past rows as they were.
- [x] Ruff clean, the full suite passes.
