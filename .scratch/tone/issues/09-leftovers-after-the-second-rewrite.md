# 09: The leftovers after the second week 6 rewrite

**What to build:** The tone 07 pass fixed the openers and the no-number blurbs in most chapters. Four habits remain after the second rewrite of week 6. Fix each in the prompts or the chapter build, then rewrite the chapters that show them and read the result.

1. The game changer chapter repeats the matchup chapter. "without Bernard, that is a loss" and "and that's an upset" mirror the matchup lines. The matchup-of-the-week note from ticket 07 went to the recap only. Give it to the game changer chapter too, and to the awards chapter when the Game Changer is in the matchup of the week.
2. One closer repeats: "and that's an upset" ends sentences in two chapters, and "and that's your Game Changer" uses the same shape. Add the ", and that's X" closer to the banned patterns, with the cap of one per page across chapters as a prompt line.
3. The rankings chapter repeats its own openers: "Scoring has dipped to" twice, "despite 2 straight losses" twice, and every one of 24 sentences carries a number. The chapter is one call, so the writer can see all twelve. Add a rankings rule: no two teams share an opener; at least four teams get a sentence with no number; "form" is a stat term, say "the last 3 weeks".
4. The cut wording reads two ways for three 6-6 teams: "still on the outside" for one and "right at the cut" for two. The facts support both, but a reader sees a contradiction. Give the `PR.` fact or the standing fact one phrase per case: "in the last playoff spot", "one spot outside", "two spots outside".

Spec: `.scratch/tone/PRD.md`. This ticket amends "The voice" and the rankings chapter rule.

**Blocked by:** None. Main holds tickets 01 to 07.

**Status:** ready-for-human

- [x] The matchup-of-the-week note reaches the game changer chapter and, when it applies, the awards chapter, with tests.
- [x] The ", and that's X" closer is a banned pattern in the prompt, with a test.
- [x] The rankings chapter rule has the three lines, with a prompt test; a code check fails a rankings blurb where two teams share the first three words, with a test.
- [x] The cut phrase is one of three fixed phrases in the fact text, with a test.
- [x] Rewrite `game_changer`, `awards`, and `rankings` on main, one call each, no fallback. Paste the before and after in a comment at the bottom of this file.
- [ ] Brian publishes.

## Comments

- 2026-10-22: found after the tone 07 rewrite. Also: next_week's "a true showdown of the awful" is the sharpest jab on the page; Brian decides if it stays. recap_3 says "the trade haul dogged its own team" right before a good Tuten line.

- 2026-10-22: built on branch tone-09 at 7728eaf, checkboxes 1 to 4. make test: 697 passed. make lint: 123.

The writer adds the Matchup of the Week note to the game changer and awards chapters when the Game Changer plays for a team of that matchup. The check reads the `AW.game_changer` fact and the scope of the `motw` chapter, so it works on a saved sheet. The game changer chapter gets no note when its matchup is not the Matchup of the Week, because the note would then name a chapter that never told that game.

The tone prompt bans the ", and that's X" closer, with a cap of one sentence per page across every chapter. The approved example "Return of T Mac flattened Unsolicited Dak Picks 120.29 to 81.47, and that's an upset." now ends "in an upset." The opener line no longer shows the closer as its example.

Writer rule 21 has three more lines: no two teams share an opener, at least 4 teams get a sentence with no number, and "form" becomes "the last 3 weeks" with the `.trend` fact cited for the 3. The code check fails a rankings blurb when the first sentences of two teams share their first 3 words, case and edge punctuation ignored.

A standing fact for a team level with the cut now ends in one fixed phrase: "in the last playoff spot", "one spot outside the playoff spots", or "two spots outside the playoff spots". A tie that reaches further keeps the old text. The rewrite reads the saved `facts.json`, so the week 6 facts need a rebuild before the rankings rewrite shows the phrase.

The review made three decisions. First, the ", and that's X" closer is an outright ban with a code check, in place of the cap of one per page: each chapter is one call, so a page-wide cap cannot hold. Second, the `PR.` fact text says "the last 3 weeks" in place of "form", so the fact carries the 3 and the writer cites no `.trend` fact for it. Third, the cut phrase covers any distance: "in the last playoff spot", "level with the last playoff spot" for a tied team above it, and "one spot", "two spots", and so on "outside the playoff spots" for a tied team below it.

Brian approves the new tail of the example that ended ', and that's an upset'.

- 2026-10-22: rewrote `game_changer`, `awards`, `recap_4`, and `rankings` on main after the merge. `recap_4` joined the list because it held the banned closer. The first rankings rewrite fell back: the cut fact spelled "two" while the writer wrote "2", and the writer read "12th in the last 3 weeks" as scoring. Commit `958c1ee` fixed both: the cut fact uses a digit, and the form word is "results over the last 3 weeks". The second rankings rewrite passed on attempt 2. The saved week 6 facts also moved behold the lamb to 7th and Brock to 8th, which matches the published rankings table; the old blurb said 8th. Before and after:

  **game_changer, before:**
  > Germie Bernard, the new pickup, dropped 20.2 on an 8.13 projection for behold the lamb, and that's your Game Changer.
  > He outscored the margin on his own, so without Bernard, that is a loss.
  > A side sitting 11th knocked off the team in 2nd, and that's an upset.
  > Lucky waiver grab, and he has beaten projection in 3 straight weeks.
  > Meanwhile the actual Lamb on the roster, CeeDee, came in 5.51 under his projection.
  **game_changer, after:**
  > Germie Bernard has beaten projection in 3 of the last 3 weeks.
  > This week the new pickup hit 20.2 on an 8.13 projection, a lucky waiver add for behold the lamb.
  > He won it, and since this side sat 11th before the week, knocking off Bo Girds goes down as an upset.
  > Without Bernard, that is a loss.
  > Waivers pay.

  **awards, before:**
  > To Infinity and Bijan got 6.3 from Bijan Robinson, the Underperformer at 16.78 under projection.
  > Germie Bernard, a lucky recent add off waivers, put up 20.2 on a 8.13 projection to take Game Changer for behold the lamb.
  > Trevor Lawrence was Top Scorer at 28.34, and Amon-Ra Dawg Your Team still lost.
  > London Cooking left Jayden Daniels and his 21 on the bench for MVB and won by 66.4 anyway.
  **awards, after:**
  > To Infinity and Bijan named the whole franchise after Bijan Robinson, and he paid them back with 6.3 points, 16.78 under projection, for Underperformer honors.
  > Ladd McConkey and Terry McLaurin, also on that roster, are now listed Out.
  > Tre Tucker took a 7.58 projection and turned it into 24.2 for All You Need Is Love, the week's Overachiever.
  > Germie Bernard, a recent waiver add for behold the lamb, scored 20.2 on a projection under half that and takes Game Changer, about as lucky as a pickup gets.

  **recap_4, before:**
  > Bo Girds had the girds but none of the grip, as their starters dropped 7 passes worth about 17.8, and those drops cost them the game.
  > Butterfingers all the way down.
  > behold the lamb got lucky with the new pickup Germie Bernard, whose 20.2 won it for a side that sat 11th before the week, and that's an upset.
  **recap_4, after:**
  > Bo Girds' starters dropped 7 passes worth about 17.8, and those drops cost them the game.
  > The side sitting 11th before the week won it in an upset, with the new pickup Roschon Johnson posting 13.5.
  > Meanwhile the losing side's own new pickup, the Colts defense, finished below zero.

  **rankings, before:**
  > Lil Fridge holds the top spot at 10-2, 4 games clear of the cut.
  > Scoring has dipped to 113.91 a week lately, under the 123.28 season average.
  > London Cooking has won 4 straight to hold at 9-3.
  > The last 3 weeks ran at 122.9 a week, above the season average.
  > Bo Girds holds at 8-4 despite 2 straight losses.
  > They still rank 2nd in scoring, so the panic can wait.
  > Maye d'force B with U climbs 2 spots to 4th.
  > At 7-5, they sit just 1 game above the cut.
  > Return of T Mac jumps 3 places to 5th with the top form in the league.
  > A 3-game win streak, and they're still on the outside at 6-6.
  > All You Need Is Love slides 1 spot to 6th.
  > Scoring has dipped to 97.48 a week, and 1 game above the cut is all the cushion left.
  > Brock ‘N’ Roll drops 3 places and sits right at the cut at 6-6.
  > Form ranks 8th, and the last 3 weeks dipped to 111.81 a week.
  > behold the lamb climbs 3 places to 8th.
  > They're 6-6 and right at the cut while ranking 10th in scoring.
  > Amon-Ra Dawg Your Team moves up a spot despite 2 straight losses.
  > At 4-8, they're 2 games below the cut.
  > Unsolicited Dak Picks falls 3 places to 10th with the worst form in the league.
  > Losers of 3 straight, they've averaged 92.05 a week lately.
  > To Infinity and Bijan drops 2 places to 11th.
  > The last 3 weeks averaged 77.06, about as far from infinity as it gets.
  > Pukancun on 3 stays dead last at 1-11.
  > Scoring is up to 93.93 a week lately, with the cut still 5 games away.
  **rankings, after:**
  > Lil Fridge stays on top at 10-2, 4 games clear of the cut.
  > The scoring has cooled to 113.91 a week over the last 3 weeks.
  > London Cooking has won 4 straight and holds 2nd.
  > Nobody is stopping them right now.
  > Bo Girds has lost 2 straight and still holds 3rd.
  > That leaves a cushion of 2 games over the cut.
  > Maye d'force B with U climbs to 4th after 2 straight wins.
  > Still, that 7-5 record is just 1 game above the cut.
  > Return of T Mac jumps to 5th on 3 straight wins.
  > The catch: they still sit outside the playoff spots.
  > All You Need Is Love stays 6th while holding a playoff spot at 7-5.
  > Turns out they also need points.
  > behold the lamb leaps 4 places to 7th.
  > Behold, a 6-6 team that has faced the 2nd toughest schedule played.
  > Brock ‘N’ Roll falls 4 places to 8th while clinging to the last playoff spot.
  > The scoring has slipped too.
  > Amon-Ra Dawg Your Team slips to 9th after 2 straight losses.
  > At 4-8, the dog days are here, 2 games below the cut.
  > Unsolicited Dak Picks has lost 3 straight and owns the last-ranked results over that stretch.
  > Nobody asked for these picks, and nobody is asking for this record either.
  > To Infinity and Bijan sits 11th at 4-8.
  > Infinity is a stretch for an offense averaging 77.06 a week lately.
  > Pukancun on 3 stays last at 1-11, 5 games below the cut.
  > At least the scoring is up to 93.93 a week lately.
