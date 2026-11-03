# 03: The rankings chapter

**What to build:** One blurb per team in the file, from one writer call per week. Twelve new facts with the prefix `PR.` and the roster ID, one per team, hold the power rank, the movement, and the four component ranks as ordinals. A chapter `rankings` with all twelve teams in scope carries those facts plus each team's standing, streak, and trend facts, with a sentence range of 12 to 24. Every sentence in the chapter carries a roster ID, through an optional field on the sentence that other chapters leave empty. The writer rule for this chapter: tag every sentence, give every team 1 or 2 sentences, cite the team's `PR.` fact in its first sentence, order the teams from rank 1 to 12. The code check enforces the tags for this chapter. The season file carries the current week's blurbs, grouped by team, and past weeks keep the blurbs they had. The `rankings` command makes the one writer call for the current week. The blurb writes under the tone prompts and adds no tone rule.

Spec: `.scratch/rankings/PRD.md`, sections "The facts and the chapter" and "The season file".

**Blocked by:** 02 The season file. Tone tickets 01 to 03 should land first so the blurb writes in the new voice; they do not block the code.

**Status:** ready-for-agent

- [ ] The sheet has twelve `PR.` facts, each with the team and every ordinal in its numbers list.
- [ ] The chapter `rankings` holds every team and the four facts per team, in a sheet test.
- [ ] The code check fails a rankings sentence with no roster tag, a team with no sentence, a team with 3 sentences, and a first sentence without the team's `PR.` fact. A good blurb passes. A tagged reaction sentence counts toward the team's 2.
- [ ] Other chapters pass with no roster tag.
- [ ] The file render puts each team's sentences in its row for the current week and keeps past weeks' blurbs from the last file.
- [ ] The `rankings` command on the real week 6 makes one call, no fallback, and the file holds twelve blurbs for week 6. Paste two of them in a comment at the bottom of this file.
- [ ] `make test` passes. Lint count on the branch is no higher than on main.

## Comments

- 2026-10-22: built on `rankings-chapter` at `24a14a3`, two Opus reviews, one fix pass. Awaits Brian merge with `--no-ff`.
- Two week 6 blurbs from the real run, attempt 1, no fallback:
  - Rank 1: "Lil Fridge holds 1st at 10-2 and leads the league in scoring." `PR.3`, `S.1`. "The form has cooled, though, at 113.91 per week over the last 3 weeks." `H.3.trend`
  - Rank 2: "London Cooking stays 2nd and has won 4 straight." `PR.5`, `H.5.streak`. "At 9-3, they sit 3 games above the cut." `S.2`
- Before the publish, run `make rankings WEEK=6` again on main so `facts.json` and `blurbs.json` hold the chapter; the review runs restored them.
