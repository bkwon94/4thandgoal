# 01 — Playoff odds column

**What to build:** the rankings page shows each team's playoff odds beside its record. The rankings
types gain an optional `odds` object per row: `playoff` and `bye` as whole numbers, `seed` as a
number or null, `status` as `in`, `out`, or `open`. The loader accepts a row with or without it,
under schema version 1. The power rankings table gains a `Playoff %` column after `W-L`, in the
header and in each row, at every width. The cell shows the number for `open`, "In" for `in`, "Out"
for `out`, and stays blank when the row has no `odds`. The open row of a team shows the bye odds
and the seed on one line beside the component cells when the row has them. Demo: open the rankings
page on the fixture with odds on the current week.

Spec: `.scratch/stakes/pipeline/PRD.md`, "The rankings file and
the site".

**Blocked by:** None — can start immediately.

**Status:** done

- [x] The row type gains the optional `odds` object, and the loader accepts rows with and without it.
- [x] The table shows a `Playoff %` column after `W-L` at every width, with a footnote line that reads "Playoff odds from 5,000 simulated seasons."
- [x] The cell shows the number, "In", "Out", or blank.
- [x] The open row shows "Bye {b}%, most often the {s} seed" when the row has a seed, and "Bye {b}%" when it has none. The line sits on its own line under the component cells, before the blurb, at every width.
- [x] The rankings fixture gains `odds` on the current week only, with one `in`, one `out`, and open rows.
- [x] Tests: the loader test covers both row shapes; the component test renders the number, "In", "Out", the blank cell, and the open-row line.
- [x] Lint clean, the full suite passes.
