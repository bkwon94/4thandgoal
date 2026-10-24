# 05 — The unlucky and lucky awards

Spec: `.scratch/nflverse/PRD.md`.

**What to build:** The awards chapter gets two new awards. Unlucky goes to the started player with the
largest expected gap under zero in week N, at least 5 points under. Lucky goes to the started player with
the largest gap over zero, at least 5 over. Each fact holds the actual, the expected, and the gap. No fact
when no starter clears the floor. When the expected points read through week N-1, there is no award for
week N. The writer gets a one-line rule per award, as the other awards have, and the verifier rejects an
uncited number as today.

The expected data gives expected points per game only. The gap is the starter's points in this league, the
Sleeper points the sheet already holds for week N, minus his expected points for that game.

**Blocked by:** 03 Expected points and the expected gap.

**Status:** ready-for-agent

- [ ] On the fixture with hand-set gaps, the unlucky fact names the starter with the largest gap under, with his actual, expected, and gap.
- [ ] The lucky fact does the same for the largest gap over.
- [ ] A week where no starter clears 5 points has no fact, and the chapter builds without it.
- [ ] A lagged file gives no award fact for week N.
- [ ] A bench player never gets either award.
- [ ] The awards chapter may cite the two facts and no other chapter may.
- [ ] The awards prompt has one rule line per award, and a prompt text test pins both.
- [ ] Every number in each fact's text is in its numbers.
