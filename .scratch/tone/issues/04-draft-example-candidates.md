# 04: Draft the example candidates

**What to build:** Fifteen candidate sentences in the new voice, from week 6 facts, for Brian to pick from. Run the rewrite command on week 6 for five chapters under the new prompts: the matchup of the week, the awards, two recaps, and the median. Each run makes one Claude call on this Mac. From the output, list 15 sentences that passed the verifier, each with the chapter, the fact IDs it cites, and the old sentence from the saved week 6 blurb beside it. Pick for variety of shape: some with no number, one reaction sentence, one roast by team name, one plain phrase in place of a stat term. This ticket ends with that list in a comment at the bottom of this file. It makes no prompt edit and no publish.

Warning: the rewrite command overwrites the chapter in the saved blurbs. Copy the week 6 blurbs file aside first, and restore it at the end, so the published page and the saved blurbs stay the same until ticket 06.

Spec: `.scratch/tone/PRD.md`, section "The example set".

**Blocked by:** 01 Reaction sentence, 02 Banned phrases and the ", which" cap, 03 The group chat voice.

**Status:** done

- [ ] The week 6 blurbs file is copied aside before the first rewrite and restored after the last.
- [ ] Five chapters rewritten under the new prompts, one call each, no fallback.
- [ ] A list of 15 candidate sentences, each with its chapter, its fact IDs, and the old sentence, in a comment at the bottom of this file.
- [ ] The list has at least 3 sentences with no number, 1 reaction sentence, 1 roast by team name, and 1 plain phrase for a stat.
- [ ] No prompt file changed. No publish.

## Comments

Candidates from the week 6 rewrite under the prompts at `tone` `021f5f0`. Every sentence below is from a passed attempt.

1. `motw`: "It was an upset: behold the lamb, 11th before the week, beat the team sitting 2nd." Facts: `M4.upset`, `M4.result`. Old: "behold the lamb beat Bo Girds by 5.34, and it was an upset: the lamb was 11th before the week."
2. `motw`: "Lucky recent add Germie Bernard came off waivers and scored 20.2 on a 8.13 projection, and without him, that is a loss." Facts: `M4.move.13274`, `M4.swing.13274`, `M4.driver.13274`, `M4.result`. Plain phrase: "without him, that is a loss" in place of swing. Old: "Recent add Germie Bernard scored 20.2 on a 8.13 projection, a lucky waiver pickup and the biggest decider on the field."
3. `motw`: "Bo Girds starters dropped 7 passes worth about 17.8, and those drops cost the game." Facts: `M4.dropswing`, `M4.result`. Old: "Bo Girds's starters dropped 7 passes worth about 17.8, so the drops cost the game."
4. `motw`: "Matthew Golden alone dropped 3, worth about 14.2." Facts: `D.12501`, `D.12501.value`. Old: "Matthew Golden's drops alone were worth about 14.2."
5. `motw`: "Brutal pickup." Facts: none. Reaction sentence; it follows "The Colts defense, a recent add, finished at -0.85 and still counts as a decider." Old: "Bo Girds also started recent add Indianapolis Colts, a free agent pickup that scored -0.85."
6. `awards`: "To Infinity and Bijan got 6.3 from Bijan Robinson, the Underperformer of the week." Facts: `AW.underperformer`. Old: "Underperformer is Bijan Robinson at 6.3, a branding problem for a team called To Infinity and Bijan."
7. `awards`: "Ladd McConkey and Terry McLaurin, also on that roster, are now listed Out." Facts: `W.injured`. No number. Old, nearest: "Underperformer is Bijan Robinson at 6.3, a branding problem for a team called To Infinity and Bijan."
8. `awards`: "Trevor Lawrence took Top Scorer for Amon-Ra Dawg Your Team with 28.34." Facts: `AW.top_scorer`. Old: "Top Scorer Trevor Lawrence put up 28.34 for Amon-Ra Dawg Your Team, which lost anyway."
9. `recap_1`: "Lil Fridge rolled Brock ‘N’ Roll 126.79 to 88.31, and at least the Brock in the name showed up, with Brock Purdy as Top Scorer." Facts: `M1.result`, `M1.top.1`. Roast by team name. Old: "Lil Fridge beat Brock ‘N’ Roll by 38.48, with recent add Denver Broncos chipping in 13.35 off the free agent pile."
10. `recap_1`: "Recent add Denver Broncos posted 13.35 for the winners, while the losers' recent add, the Tampa Bay Buccaneers defense, managed 9.65." Facts: `M1.move.DEN`, `M1.move.TB`, `M1.result`. Old: "Brock ‘N’ Roll went to the same pile and came back with recent adds Tampa Bay Buccaneers and Dallas Goedert, who scored 9.65 and 9.1, so the free agent pile plays favorites."
11. `recap_2`: "In an upset, Return of T Mac flattened Unsolicited Dak Picks 120.29 to 81.47." Facts: `M2.result`, `M2.upset`. Old: "Return of T Mac beat Unsolicited Dak Picks by 38.82 in an upset, and the losers' 81.47 was a season low."
12. `median`: "The median sat at 106.83, and To Infinity and Bijan missed it by 60.75." Facts: `MED.value`, `MED.below.7`. Old: "To Infinity and Bijan posted a season low of 46.08, less a median game than a rumor of one."
13. `median`: "That 46.08 is a season low, posted by a side already 2 games below the cut." Facts: `H.7.high`, `S.11`. Old: "To Infinity and Bijan posted a season low of 46.08, less a median game than a rumor of one."
14. `median`: "Not even close." Facts: none. Reaction sentence; it follows candidate 13. Old, nearest: "To Infinity and Bijan posted a season low of 46.08, less a median game than a rumor of one."
15. `median`: "Bo Girds cleared it by 2.79, and Amon-Ra Dawg Your Team missed it by exactly that much." Facts: `MED.closest`. Old: "Bo Girds and Amon-Ra Dawg Your Team landed 2.79 on opposite sides of the line, so only one of them got dogged."

No number: 5, 7, 14. Reaction: 5, 14. Roast by team name: 9. Plain phrase for a stat: 2. Short: 4, 5, 14. Long: 2, 9, 10.

- `motw`: passed on attempt 2, no fallback. Attempt 1 failed on "other recent add" for the Colts.
- `awards`: passed on attempt 2, no fallback. Attempt 1 failed on "holes to fill" after `W.injured`.
- `recap_1`: passed on attempt 1, no fallback.
- `recap_2`: passed on attempt 1, no fallback.
- `median`: passed on attempt 1, no fallback.

Pick 6 to 8 for Brian.

- 2026-10-22: Brian picked 5, 14, 9, 7, 11, 15, 4.

- 2026-11-02: `main` holds the merge, on the word of tone ticket 09, `09-leftovers-after-the-second-rewrite.md`. Status set to done by the state-file sweep of agent-habits 02.
