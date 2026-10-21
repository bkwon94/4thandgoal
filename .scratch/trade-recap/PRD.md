# Trade recap: a fixed trade window and no grade on the weekly page

Status: ready-for-agent
Date: 2026-10-21
Amends: `design/specs/2026-10-20-history-trades-drops-design.md` (the window),
`design/specs/2026-10-20-trade-grade-v2-design.md` and `.scratch/trade-grade-v3/PRD.md` (the grade)
Ships before: the week 7 job on Tuesday 2026-10-27 08:00

## Problem Statement

The week 6 page shows a trade made on Tuesday at 11:56, after the week's games. The trade window
ends at the build's fetch time, and Brian built week 6 by hand at 11:58. The 08:00 job would have
left that trade out, so the page depends on when someone ran the build. The trade also played out
in week 7, not week 6, so every impact and swing fact on it is empty.

The page grades each trade. Brian no longer wants a grade on the weekly page. The grade belongs to
the trade analyzer, which gets its own rubric. On the weekly page the trade chapter is a recap of
the week, with humor, and nothing more. Three trade cards also fell back to "No grade" on the last
rebuild, which a recap never needs.

## Solution

The trade window is a calendar span: from the Tuesday cutoff that opens week N to the Tuesday
cutoff that opens week N+1. Build time plays no part. A Tuesday or Wednesday trade lands on the
page of the week whose games come next, where it played out.

The trade chapter becomes a trade recap: who moved, and how the week went for each side, from the
impact and swing facts, in the page's tone with humor allowed. The card shows the two sides and
the player rows. The letter, the toggle, and the grade facts go. Week 6 is rebuilt from the saved
data and republished with five trades. The Bijan trade moves to week 7.

## User Stories

1. As the commissioner, I want a trade made on Tuesday or Wednesday on the page of the week whose
   games come next, so that the recap can say how it played out.
2. As the commissioner, I want the same trades on a page no matter when the build ran, so that a
   hand rebuild and the Tuesday job agree.
3. As the commissioner, I want no trade on two pages, so that the Bijan trade shows on week 7 only.
4. As the commissioner, I want no grade on the weekly page, so that the page recaps and the
   analyzer grades.
5. As the commissioner, I want each trade recap to say what the traded players did this week for
   each side, so that the page is about the week.
6. As the commissioner, I want humor in a recap, so that the trades read as fun as the recaps do.
7. As the commissioner, I want a recap that says a trade decided a game only when the swing fact
   allows it, so that the page never overstates a trade.
8. As the commissioner, I want a late trade recapped as a late trade, so that the page explains why
   a player's points went to his old roster.
9. As the commissioner, I want a recap with no verdict on the trade as a whole, so that no manager
   reads "fleeced" or "won the trade" on the page.
10. As the commissioner, I want the trade card to keep the two sides, the player rows, and the
    headshots, so that the look of the page holds.
11. As the commissioner, I want the recap text on the card with no toggle, so that one tap less
    stands between a reader and the recap.
12. As the commissioner, I want a card with a failed writer call to show the sides sentence, so
    that the page never says "No grade".
13. As the commissioner, I want the weekly build to skip the chart fetch, so that the build has one
    network source less and no Claude image read.
14. As the commissioner, I want week 6 rebuilt from the saved data and republished, so that the
    live page carries the recap and five trades.
15. As the commissioner, I want the week 7 job on 2026-10-27 to build a page with recaps and the
    Bijan trade, so that no hand step follows the first scheduled run.
16. As the writer, I want the recap chapter scoped to the sides, impact, swing, and late facts,
    so that no grade input leaks into a recap.
17. As the writer, I want one rule for a recap in place of the two grade rules, so that the brief
    is short and clear.
18. As the verifier, I want the grade-only checks gone, so that a recap is checked on citations
    alone.
19. As the maintainer, I want the grade input builders kept in code for the analyzer, so that the
    analyzer spec reuses them with no rewrite.
20. As the maintainer, I want the glossary terms for the window and the recap to match the code,
    so that the next reader finds no contradiction.

## Implementation Decisions

### The window

- The window of week N is: after the Tuesday cutoff of week N, up to and including the Tuesday
  cutoff of week N+1. The cutoff function that exists is the one source of both bounds.
- The previous build's fetch time and this build's fetch time no longer bound the window. The
  helper that reads the previous fetch time goes, with its tests. The fetch time stays in the
  build record for the page footer and the history.
- Both Sleeper transaction legs, N and N-1, are still fetched and merged, because Sleeper's leg
  does not follow the cutoff. The merge and the sort by creation time stay as they are.
- The module docstring that says a trade belongs to the week whose build first saw it is wrong and
  changes to the calendar rule.

### The recap chapter

- One chapter per trade stays, keyed as today, one to three sentences.
- The chapter's fact scope is: the sides fact, the impact facts, the swing fact, and the late fact.
  The per-player grade inputs, the team record fact, the need fact, the usage facts, the injury
  facts, and the value facts leave the weekly sheet. Their builders stay in the sheet module,
  unused by the weekly build, for the analyzer.
- The writer rules for the grade are replaced by one recap rule: say who moved, then how the week
  went for each side from the impact and swing facts; humor is allowed within the tone rules; give
  no grade, no letter, and no verdict on the trade as a whole; say a trade decided or cost a game
  only in a sentence that cites a swing fact whose gap is at least the margin. The "Grade keys"
  line and the grades map leave the chapter brief and the blurb output.
- The vocabulary keeps trade impact, trade swing, and late trade. The terms for the grade, the
  trade value, roster need, snap share, target share, red-zone use, and injury before the trade
  leave the writer's vocabulary. The analyzer spec carries them in its own prompt.
- The chart fetch leaves the weekly build and the bundle builder. The `chart` command stays as a
  hand check. The build record keeps an optional chart flag so old verify files still parse.
- The verifier's check for a chart value number in a trade sentence goes with the value facts.

### The card

- The card keeps the header, the two sides with team name and avatar, and the player rows with
  headshots. The grade letter, the "No grade" fallback, the toggle button, and the hidden panel
  go. The recap text sits under the rows, always visible.
- A chapter whose writer call fails after the retries the build has today renders the sides
  sentence as the recap.
- The stylesheet and the script drop the grade and toggle rules for the trade card. The page is
  checked at 390 wide with no horizontal scroll, as every page change is.

### The rebuild

- After the change lands on `main`, week 6 is rebuilt with the saved raw data, so no fetch runs.
  The window then holds five trades. Brian reviews the page on disk, then publishes.
- The week 7 window opens at 2026-10-20 08:00 Eastern and holds the Bijan trade.

### Docs

- The glossary already carries the new window and recap terms. The handoff and the todo file note
  that the grade left the page and where it went.

## Testing Decisions

- A good test feeds inputs at a seam and asserts text, numbers, or markup. It never asserts how a
  helper is built.
- Seams, all existing:
  1. The window function, on the week 6 fixture: the five week 6 trades are in, the Tuesday trade
     is out, and a week 7 window holds it. The tests that assert the fetch-time bound change to
     the cutoff bound.
  2. The bundle builder on the week 6 fixture: each trade chapter scopes exactly the sides,
     impact, swing, and late facts, and no `.value`, `.need`, `.team`, `.got`, `.gave`, usage, or
     injury fact exists on the sheet.
  3. The renderer on a bundle and saved blurbs: the card holds the sides and the rows, no grade
     element, no toggle, and the recap text; a chapter with no blurb shows the sides sentence.
  4. The build from disk: it writes everything with no chart fetcher wired, and an old verify file
     with a chart flag still reads.
- Prior art: the window tests, the `tbundle` fixture tests, the render tests, and the build-from-
  disk tests.
- The writer prompt change is checked by the real week 6 rebuild, which Brian reads.

## Out of Scope

- The trade analyzer, its rubric, and its service. See `.scratch/site-api/PRD.md`.
- The React port of the page. See the site repo.
- A retry loop for a chapter that falls back to the template. A recap fallback is the sides
  sentence, which is acceptable.
- The "lucky" count across chapters.
- Draft picks in the sides line, which render as today.

## Further Notes

- A trade made exactly at a cutoff belongs to the earlier week, because the window is open at the
  start and closed at the end, as the code is today.
- The trade deadline is week 11. Weeks 12 and on build with no trades and no trade chapters, which
  the renderer already handles.
