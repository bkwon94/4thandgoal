# Ledger — nflverse follow-up tickets 11 to 18

Base: main e29e2b4. Worktrees ../cornerstone-fantasy-sleeper-weekly-report.nflverse-NN, branch nflverse-NN.
Flow: Opus builder with TDD per ticket -> two Opus reviewers (standards, spec with real-data check) -> one fix pass -> rebase on main, merge --no-ff, suite on main, push.

## State
- 2026-10-24: worktrees nflverse-11..18 made from main e29e2b4. Eight Opus builders dispatched in parallel. Reports land in .scratch/nflverse/ledger/NN-build.md.
- 16: built 0046ae6, 1038 pass, ruff 135. Reviewers out (standards sonnet, spec opus).
- 11: built ba200a5, 1038 pass. Reviews: standards clean (minor: test via grade), spec minor: handcuff zero gap now reachable. Ruling: fix both. Fix round 1/5 sent.
- 12: built f95732f, 1037 pass, concerns (live run misses the branch; seller branch out of scope). Reviewers out.
- 14: built 3cf0bee, 1042 pass, 20 of 11879 names change. Standards clean (minor tuple vs set, left). Spec review out.
- 16: spec review Important: float drift before r2 (21 of 288 rows). Fix round 1/5 sent. Standards clean.
- 17: built f553825, 1038 pass. Standards: Important, degraded refetch loses saved drops; 3 minors. Spec review out. Fix round batched after it.
- 12: standards 3 minors (quote style, docstring phrase, two-player test). Hold for spec review.
- 14: spec Important: in-scope St. Brown trips out-of-scope Brown check in verifier.py:311. Fix round 1/5 sent. Week 6 blurbs unchanged either way.
- 18: built 6e9b528, 1038 pass, live line names all six. Ruling: 14 changed assertions accepted, the ticket reverses the rule they pinned; cost if wrong: a test that guarded something else is now weaker. Reviewers out; spec reviewer checks the site missing-list render.
- 17: spec Important same as standards (degraded refetch loses drops); real data: refetch gains usage, expected, next_games, environment; drops and gsis equal. Fix round 1/5 sent: merge None fields from saved.
- 12: spec clean; real data: Meyers for Jacobs reads 'gains after Josh Jacobs returns in week 7'. Fix pass sent for 3 minors + 2 tests.
- 18: standards 2 Important (tautology test; fragile index-2 derivation) + 4 minors. Ruling: plain dict of 7 names + a test that asserts equality with REFRESHED_SOURCES names and SLOW_SOURCES; overrides my brief. Cost if wrong: two lists to keep in step by hand, caught by the test. Hold for spec.
- 16: fix round 1/5 done 204cbdd, 1040 pass. Scoped re-review sent.
- 11: fix round 1/5 done e974438, 1040 pass. Scoped re-review sent.
- 14: fix round 1/5 done 34fb301, 1043 pass. Scoped re-review sent.
- 16: complete (commits 0046ae6..204cbdd, review clean). Minor deferred: no comment on the r2(float) round trip for noisy file text.
- 18: spec clean; site types missing as string[] and never renders it; no DOCUMENT_VERSION bump. Fix round 1/5 sent (plain dict, drift test, 3 minors).
- 11: complete (commits ba200a5..e974438, review clean).
- 14: complete (commits 3cf0bee..34fb301, review clean). Minor deferred: verifier test checks only A.J. Brown.
- 17: fix round 1/5 done 0ee436a, 1039 pass. Scoped re-review sent.
- 12: fix pass done cea7a80, 1039 pass, mutation-checked. Scoped re-review sent (sonnet).
- 12: complete (commits f95732f..cea7a80, review clean). Minor deferred: _gain_when docstring first line is a fragment.
- 13: built 2461b9a, 1039 pass, no DOCUMENT_VERSION bump. Reviewers out (standards sonnet, spec opus with key-stability check).
- 17: re-review: 3 addressed, 1 NEW Important (merged flags let a degraded extract save). Fix round 2/5 sent: save on fresh flags only.
- 13: standards clean, 2 minors deferred (test ids tied to fixture rosters; dense comprehension). Spec review pending.
- 15: built dd1474c per chapter, 1039 pass. Builder found week 6 says lucky 3 times across chapters; per-chapter check misses it. Ruling: extend to page-wide via a carried lucky_used flag through write_and_verify, feedback loop rewrites; chapter order decides who keeps the word. Cost if wrong: an early chapter uses the word before the awards chapter, and ~100 lines more than the ticket planned. Fix round 1/5 sent.
- 18: fix round 1/5 done f851530, 1038 pass. Scoped re-review sent.
- 13: spec Important (judgment): full projection hash misses cache on every Sleeper update. Ruling: hash only due-back rows from return week on, plus a not-None flag. Cost if wrong: a projection change for a healthy player does not clear a grade; the grade never reads it, so none. Keys stable across processes (f5fa211c twice). Fix round 1/5 sent.
- 18: complete (commits 6e9b528..f851530, review clean). Minor deferred: cli.py:133 comment describes history; delete the line.
- 17: fix round 2/5 done 2ce5492, 1039 pass. Scoped re-review sent.
- 17: round 2 re-review: frozen save ADDRESSED; round-1 Important still open (None-fill misses smaller dicts). Fix round 3/5 sent: saved keys win, refetch fills absent keys only.
- 13: fix round 1/5 done 6f88a56, 1041 pass. Scoped re-review sent.
- 15: fix round 1/5 done e33f039 (page-wide, used_words set), 1045 pass; week 6 flags game_changer[1] and awards[3]. Both reviewers out over the full branch.
- 13: complete (commits 2461b9a..6f88a56, review clean). Keys stable 0c752c40 twice; healthy-player projection change leaves key unchanged.
- 15: standards clean, 3 minors (passive comment, why None, local import). Hold for spec.
- 15: spec Critical: awards chapter can be denied its own Lucky award name. Ruling: when AW.lucky exists, awards owns the word; other chapters get it pre-used. Cost if wrong: a recent-add 'lucky' line in motw is blocked in award weeks; the prompt rule already prefers the award. Also: seed first-attempt feedback from used_words. Fix round 2/5 sent.
- 17: fix round 3/5 done f4117a6, 1040 pass. Scoped re-review sent.
- 17: complete (commits f553825..f4117a6, review clean after 3 rounds). Minor deferred: a degraded refetch's partial usage is not shown in the build record.
- Merge chain: 16, 13, 18, 11, 14, 17, 12 rebased and merged --no-ff, no conflicts; main at bcda118. Suite + ruff on main running. 15 waits on round 2.
- 15: fix round 2/5 done 81d6f58, 1050 pass. Scoped re-review sent.
- Main after 7 merges: 1065 passed.
- 15: complete (commits dd1474c..81d6f58, review clean after 2 rounds). Minors deferred: writer.py:190 attempt saves 2 on a first-try pass with used words; retry feedback drops the used-word line (verifier.py:497).
- 15 merged after a test-file conflict (both sides kept). Main 3dfd0fd: 1079 passed, ruff 135. All eight merged. Final whole-branch review out (opus).
- Final review: 0 Critical, 2 Important (retry drops used-word lines -> page; cache key hashes past-return players -> cost only), 6 Minor, 17 STE rows. One fix wave dispatched on nflverse-final (opus).
