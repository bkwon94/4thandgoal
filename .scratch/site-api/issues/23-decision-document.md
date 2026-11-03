# 23: The result document leads with a decision, not letters

**What to build:** The analyze document gives a decision for the asking side, then the analysis, the data, and the reasoning per side. No letter grade reaches the document or the prose. The rubric keeps its letters inside the code, because they drive the verdict and Claude's one-step move. The site ticket 04 renders the new shape.

**Why:** The commissioner wants a call first, then the why. The letters are machinery a manager cannot act on.

**Blocked by:** None. Ticket 20 adds the share numbers to a factor reason; both can land in either order.

**Status:** done

The new document, `result_document` in `src/cornerstone_api/analyzer.py`:

```
{
  "trade": {as today},
  "decision": {"for_roster": int, "answer": "yes" | "no" | "not_as_is", "reason": str, "differs": bool},
  "sides": [
    {
      "roster_id": int,
      "analysis": str | null,
      "chart": {"lean": "more" | "even" | "less", "reason": str},
      "factors": [{"name": str, "lean": "for" | "against" | "even", "reason": str}]
    }
  ],
  "as_of": {as today}, "fallback": bool, "missing": [...], "stale": [...]
}
```

- `answer` maps from the verdict choice: accept to "yes", decline to "no", counter to "not_as_is".
- `chart.lean` maps from the start letter: A and B to "more", C to "even", D and F to "less". `chart.reason` is the band reason text as today.
- `factors` maps from the adjusters in rubric order: step above zero to "for", below zero to "against", zero to "even". The schedule adjuster has no step; its `lean` maps for, against, or even as today. `reason` is the adjuster reason.
- `start_letter`, `reason`, `final_letter`, `final_reason`, `step`, and the old `verdict` key leave the document.

- [x] `result_document` builds the shape above. The cache key in `src/cornerstone_api/cache.py` gains a document version, so a result cached on the volume in the old shape is never served again.
- [x] `verdict` in `src/cornerstone/rubric.py` writes its reasons with no letter: "The trade favors the asking side.", "The trade costs the asking side too much.", "The two sides are about even, so the trade is fair.", and the two schedule forms with "ask for more" and "worth it". Update the tests that assert those strings.
- [x] `src/cornerstone/prompts/analysis.md` gains one rule: never name a letter grade in the analysis or the verdict reason; say that a side does well or poorly in plain words. `check_response` in `src/cornerstone/analysis.py` fails a side analysis or a verdict reason that matches `grades? [A-F]\b` or the word "letter".
- [x] `tests/fixtures/api/analyze-response.json` holds the new shape for the same trade. The site copies it byte for byte.
- [x] Tests: the document shape; the three answers; the chart lean per start letter; the factor lean per step and for the schedule; the cache version; the letter check in the analysis.
- [x] `uv run pytest -q` passes with no failed test.
- [x] Deployed 2026-10-22, after site ticket 04.
