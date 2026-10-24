# Final review: nflverse tickets 11 to 18

Range: `e29e2b4..3dfd0fd` on main. Read only. I ran no suite and no script.

Verdict: ship the weekly build on Tuesday. No Critical finding. Two Important findings: one reaches the page and has a one-line fix. The other affects the API cache only.

## Cross-ticket checks

1. 11 and 12 (`rubric.py`, `adjusters.py`). Both read `lineup_value` and `_due_back` as ticket 10 left them. Neither change makes the other's text or test false. The fallback in `_highest_value_player` counts a handcuff at 0. `_gain_when` names only starters that the side gets. The real-data reason from the 12 review ("gains after Josh Jacobs returns in week 7") holds on main.
2. 14 and 15 (`verifier.py`). The two changes do not overlap. `page_words` removes the scope names before the count, the same as `bare` in `code_check`. So a "St. Brown" name or a "Lucky" team name never counts. The "St." title in `analysis.py:141` already keeps "St. Brown" from ending a sentence in a grade reason.
3. 15 and 17 (`pipeline.py`). The two changes are in different functions and share no state. A refetch that fills `expected` in an old week can add `AW.lucky`, so `reserved_words` then reserves the word. That is the intended result.
4. 13 and 10 (`cache.py`). The key filter does not match the ruling of ticket 13. See Important 2.
5. 13 and 11, 12, 18. These three tickets change the stored document but do not bump `DOCUMENT_VERSION`. 11 and 12 change the grade. 18 changes the `missing` field at `analyzer.py:158` and `analyzer.py:237`. The key shape change in 13 makes every key new, so no old document serves now. See Minor 2.
6. 15 and the writer prompt. The first-attempt feedback from 15 makes rule 14 of `prompts/writer.md` false. See Minor 1.

## Critical

None.

## Important

1. `src/cornerstone/verifier.py:511`: the retry replaces the feedback, so the used-word lines drop out. Suppose attempt 1 fails for a number. Attempt 2 then does not hear "Do not say 'lucky'". If attempt 2 says it, the chapter falls to the template, and the reader sees that template sentence. Week 6 shows that non-award chapters do say "lucky". Fix: `feedback = "\n".join(filter(None, [page_word_feedback(used_words), _feedback(result)]))`.
2. `src/cornerstone_api/cache.py:63` and `:65`: the key hashes the rows of every rostered player in `snapshot.returns`, not only a player due back. `data/2026/returns.json` is kept by hand and holds `"5850": 7` (Jacobs). From Tuesday, `stats_through` is 7, so Jacobs is not due back. But his projection rows for weeks 7 to 17 stay in the key. Sleeper moves those rows daily, so each grade with his roster misses every day. The grade stays correct, so only cost and latency change. The test at `tests/test_api.py:555` uses `returns={}` and does not catch this. Fix: add the filter `snapshot.returns[player] > snapshot.as_of.stats_through` to both comprehensions, and add a test with a past return week.

## Minor

1. `src/cornerstone/prompts/writer.md:20`: rule 14 says "If a feedback section appears, the last attempt had an unsupported sentence." With 15, attempt 1 of each non-award chapter gets a feedback section in most weeks, and no last attempt exists. `writer.py:175` adds the header "Feedback from the last attempt:" on that call too. The command in it is plain, so the risk is low. Fix: give the used words their own prompt argument with an exact header. That fix also clears Minor 3.
2. `src/cornerstone_api/cache.py:22`: the comment says a grade rule change bumps `DOCUMENT_VERSION`, but 11, 12, and 18 changed the document with no bump. Fix: set `DOCUMENT_VERSION = 5`. All keys change already, so the bump costs nothing.
3. `src/cornerstone/writer.py:190`: a first-try pass saves `attempt: 2` when used words exist. The only readers are `blurbs.json` and the log at `pipeline.py:284`. Fix: pass the attempt number from the loop in `write_and_verify`.
4. `src/cornerstone_api/cache.py:50-51`: the docstring says "A new injuries file lands daily and moves return weeks". Return weeks come from the hand-kept `data/2026/returns.json` (`history.py:33`), not from the injuries file. Fix: "The commissioner edits the returns file by hand, and Sleeper moves projections daily."
5. `src/cornerstone/verifier.py:370`, `prompts/writer.md:14`, `prompts/tone.md:54`: the code holds "unlucky" to one sentence per page, but no prompt says so, and the comment names "lucky" only. A second "unlucky" in the awards chapter fails attempt 1. The retry feedback names the failure, so attempt 2 usually fixes it. Fix: add "Say "unlucky" at most once per page." to `writer.md` rule 8.
6. `src/cornerstone/pipeline.py:321`: the comment says each word appears "once per page" and leaves out the reserved words. Fix: "... each appear at most once per page, so each chapter gets the words that earlier chapters used and the award words it does not own."

## STE breaks in new or changed comments

| File:line | Rule | Fix |
| --- | --- | --- |
| `src/cornerstone/adjusters.py:376` | Fragment for a first line | "The function gives the time of the side's lineup gain." |
| `src/cornerstone/cli.py:133` | Describes history; the comment must stay evergreen | Delete the line. |
| `src/cornerstone/cli.py:134` | "drift" is a metaphor | "A cli test fails when the two lists differ." |
| `src/cornerstone/cli.py:139` | 26 words | "The id map only joins the ids of the other files. So the line names it only when it is missing." |
| `src/cornerstone/names.py:9` | Unclear phrase "to every reader" | "To a reader, "Brown" alone names a different player." |
| `src/cornerstone/nflverse_expected.py:34-35` | "it" has no clear referent | "...because float math can put a value just under a half, and then the value rounds down." |
| `src/cornerstone/nflverse_expected.py:78` | Metaphor "pull", and "the round" uses a verb as a noun | "...so a float error cannot move a half down before the function rounds it." |
| `src/cornerstone/pipeline.py:183` | Passive voice | "The build rewrites the file only when the refetch is complete." |
| `src/cornerstone/pipeline.py:199-200` | Passive voice | "...so the build would never fetch a saved one again, though a degraded source cut its rows." |
| `src/cornerstone/verifier.py:39` | Says "one sentence", means one sentence per page | "Each of these words may appear in one sentence of the page only." |
| `src/cornerstone/verifier.py:41` | Passive voice | "...so the awards chapter can always name the award." |
| `src/cornerstone/verifier.py:127` | Passive voice | "The function removes the chapter names first, as the code check does." |
| `src/cornerstone/verifier.py:129` | Passive voice | "...so the function removes no names." |
| `src/cornerstone/verifier.py:370` | Two topics joined by a semicolon | "The writer prompt allows "lucky" once per page. A prompt rule holds most weeks, but a count holds every week." |
| `src/cornerstone_api/cache.py:53-54` | 30 words, and false against the code (Important 2) | Split into two sentences after the fix. Replace "Every other row would miss with no new grade." with "A change to any other row would miss, but the grade would not change." |
| `tests/test_verifier.py:893` | Passive voice | "...so the word gate passes and only the count can fail." |
| `tests/test_verifier.py:975` | Passive voice | "The awards chapter must always name the award, so every other chapter starts with "lucky" used." |

## Fix before Tuesday

1. Important 1, `verifier.py:511`: keep the used-word lines on the retry. Without this fix, the reader can see a template sentence. The fix is one line and one test, about 15 minutes.
2. Important 2, `cache.py:63` and `:65`: filter the projection rows by due back. Do this before the next `make deploy` of the API. The weekly page does not read it. About 20 minutes with the test.

## Leave

These items do not reach a reader. Fold them into a later cleanup.

- 16: no comment on the `r2(float(...))` round trip for noisy file text.
- 14: the verifier test checks only A.J. Brown.
- 12: the first line of the `_gain_when` docstring is a fragment. The STE table above has the fix.
- 13: the test ids depend on the fixture rosters, and one comprehension is dense.
- 18: the history comment at `cli.py:133`. Delete it in the STE cleanup.
- 17: the build record does not show the partial usage of a degraded refetch.
- 15, `writer.py:190`: `attempt: 2` on a first-try pass. This changes the record and the log only, never the page. Fix it with Minor 1.
- New Minors 1, 2, 4, 5, and 6 above, and the STE table.

Ticket 15, Minor 4 (`verifier.py:497`, now line 511) is not in this list. It can change the page, so it is Important 1 above.
