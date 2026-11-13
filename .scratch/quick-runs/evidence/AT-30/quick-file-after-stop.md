# Recaps: a paragraph with no clear subject, and an injury named twice

Kind: bug
Status: blocked
Branch: `bug-recap-subject`.
Source: the queue task `Recaps: a paragraph with no clear subject, and an injury named twice`.
Boundary: fails rule 3, no moved seam. The fix needs a new field in `page.json`: the `.lead` fact must name the team that led, not only its side.

## Items

### 1. A recap paragraph names no team

Done condition: each paragraph of a weekly recap names the team it is about, so no paragraph opens with a bare "They".
Method: diagnosing-bugs
Cause: pending
Red: at `7b75240f`, `cd apps/pipeline && uv run --exact --package cornerstone pytest -q tests/test_recap_subject.py`

```text
E       AssertionError: clients/cpc/published/2026/week-09/page.json blurbs.recap_2: a sentence names no team: ['They still led by 4.65 after Sunday night, then James Cook III posted 16.7 on Monday and the lead flipped for good.']
FAILED tests/test_recap_subject.py::test_no_recap_sentence_opens_with_a_bare_they[clients/cpc/published/2026/week-09/page.json matchup 2]
FAILED tests/test_recap_subject.py::test_no_recap_sentence_opens_with_a_bare_they[clients/cpc/published/2026/week-09/page.json blurbs.motw]
FAILED tests/test_recap_subject.py::test_no_recap_sentence_opens_with_a_bare_they[clients/cpc/published/2026/week-09/page.json blurbs.recap_2]
3 failed, 75 passed in 0.21s
```

Green: pending
Test verdict: pending

### 2. A recap names the same injury twice

Done condition: a weekly recap names each injury once.
Method: diagnosing-bugs
Cause: pending
Red: pending
Green: pending
Test verdict: pending

## Comments

- Boundary stop after the red loop of item 1. The finding: the writer gets the leader of a matchup only by its side, so a recap falls back to a bare "They". The fix needs a new field in `page.json` that names the team that led, which moves a seam. Commits so far: `544a3a82` (the quick file), `7b75240f` (the red loop), `fe8957c2` (the Red block). Item 2 is not built. Date: 2026-11-13.
