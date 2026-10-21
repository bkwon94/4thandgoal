# 02: The recap chapter on the sheet and in the writer

**What to build:** A trade chapter is a trade recap. Its fact scope is the sides fact, the impact facts, the swing fact, and the late fact. The writer gets one recap rule in place of the two grade rules and returns no grades. The weekly build no longer makes grade input facts and no longer fetches the chart.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Each trade chapter's fact ids are exactly the sides, impact, swing, and late facts of that trade. No `.got`, `.gave`, `.team`, `.need`, `.usage`, `.targets`, `.redzone`, `.injury`, or `.value` fact is on the weekly sheet.
- [ ] The builders for those facts stay in the sheet module, unused by the weekly build, with a comment that says the analyzer uses them.
- [ ] The chart fetch leaves the bundle builder and the pipeline. The `chart` command stays as a hand check. The build record's chart source flag is optional, so a verify file from before still reads.
- [ ] The chapter brief has no "Grade keys" line and no grade keys. The blurb output has no grades map. A saved blurbs file from before, with a grades map, still parses.
- [ ] The writer rules 18 and 19 are replaced by one recap rule: say who moved, then how the week went for each side from the impact and swing facts; humor is allowed within the tone rules; give no grade, no letter, and no verdict on the trade as a whole; say a trade decided or cost a game only in a sentence that cites a swing fact whose gap is at least the margin.
- [ ] The chapter sentence range for a trade recap is one to three.
- [ ] The vocabulary keeps trade impact, trade swing, and late trade. The terms for trade grade, trade value, roster need, snap share, target share, red-zone use, and injury before the trade leave the writer's vocabulary.
- [ ] The verifier's check for a chart value number in a trade sentence goes, with its tests.
- [ ] Tests on the week 6 fixture bundle: the chapter scope above, no grade input facts on the sheet, a brief with no grade keys, and a build from disk with no chart fetcher wired that writes everything.
- [ ] `uv run pytest -q` passes with no failed test.
