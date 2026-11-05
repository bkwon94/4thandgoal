# 04: The form of a row, and the deal, roster, and standing rows

Spec: `.scratch/grade-clarity/PRD.md`. Acceptance tests AT-19, AT-20, AT-22, AT-23, and AT-35.

**App:** pipeline

**What to build:** A row shows only when it moves the grade or says something new. Each row is one plain sentence, and its mark shows the step. No bullet, row, or verdict reason uses an inner word. The deal row, the roster row, and the standing row read as decision 03 says.

**Blocked by:** 01, 02, 03.

**Status:** in-review

- [x] A row that says nothing, such as "No player it gets is a handcuff", is not in the document.
- [x] No row says "one step up", "one step down", or "no step".
- [x] A check rejects each banned word of decision 03 in a bullet, a row, and the verdict reason. The analysis prompt lists the same words. Rule 10 of the prompt goes.
- [x] The roster row counts the players in the top N at each position the trade touches, before and after, such as "You keep 3 WRs in the top 36, and you get the better player."
- [x] The standing row names the race, the need, and whether the trade meets it, in one sentence.
- [x] No document has an expected gap row.
- [x] `make check-fast` passes at the root.

## Comments

- A silent row is an adjuster with `silent=True`: a step of 0 and no new fact. Three are silent now: "No player it gets is a handcuff.", "No player it gets is out for long or often on the injury report." with no data note, and "No player it gets is a star out now or has an opportunity." A check that did not run is a fact, so its row shows. The document shows a row with a step even when it is silent. The deal, roster, and standing rows always show.
- The check rejects each inner word, plus its plural, in each bullet and in the verdict reason. The finder reasons do not run it, because the finder prompt does not change. "hole" matches as a word only, and "the line" never matches "the lineup".
- The test for the code text covers the deal, roster, and standing rows only. Ticket 05 rewords the usage, injury, upside, handcuff, and schedule rows, then adds them to `PLAIN_ROWS` in `apps/pipeline/tests/test_adjuster_rows.py`. The upside row still says "star" and "opportunity" until then.
- No row text uses `STEP_WORDS`. The prompt breakdown and the CLI still name the step in words, because Claude and Brian read the steps there. The prompt now lists "one step" and "no step" as inner words.
- The roster row drops the due-back note and the note of the missing schedules, so it stays one sentence. The schedule row still names the missing schedules, and the document lists missing sources. The tests of the projection ahead now read `lineup_value`.
- Brian checks these word choices: "your lineup scores more" and "your lineup scores less" for the lineup change; "but you get more players than you can start" for the one-for-two rule; "Outside a playoff spot but still in the race, so you need points now" for a middle team; "In a playoff spot, so you need points by the playoffs, and Jacobs is due back before them." for a return bet; and "and no player in the trade is clearly better" for a seller in a tie.
- Trade A, roster 6: its lineup changes by 0.87 points, under the fit threshold, so the standing row says "this trade keeps your points about the same", not decision 03's "gives some up". The row says "gives some up" only past the fit threshold, the same rule as the step.
- The roster row uses the line of the client as N. For `cpc` the RB line is 36, so the row says "in the top 36" at RB, not "top 24" as in decision 03.
- The depth fact now reads "the WRs in the top 36 go from 2 to 1", and the hole fact reads "the trade leaves WR2 short:". Their old words "above the line" and "is a hole" would lead Claude to an inner word that the check rejects.
- Open for Brian: the fairness line shows the reason of the first step up of a side, else the start letter reason, such as "It gets far more trade value than it gives.", or an upside reason with "star". The fairness line is not a bullet, a row, or a verdict reason, so this ticket leaves it. It now shows the roster row text in a finder card too, in the voice "you".
- `DOCUMENT_VERSION` goes to 14, because a stored document holds the old row text and the silent rows.
- The merge: `aa97207` into `grade-clarity` on 2026-11-05. `make check BASE=main` passed.
- Open: the fairness line can still show a reason with an inner word. Ticket 05 takes it.
