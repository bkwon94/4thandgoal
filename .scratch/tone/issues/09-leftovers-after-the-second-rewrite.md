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
- [ ] Rewrite `game_changer`, `awards`, and `rankings` on main, one call each, no fallback. Paste the before and after in a comment at the bottom of this file.
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
