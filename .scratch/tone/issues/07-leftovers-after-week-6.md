# 07: The leftovers after the week 6 rewrite

**What to build:** The week 6 rewrite under the new prompts still shows five old habits. Fix each one in the prompts and, where cheap, in the code check, then rewrite the chapters that show them and read the result.

The habits, from a read of every week 6 blurb:
1. One opener repeats across chapters: "In an upset," starts four sentences in four chapters. Each chapter is one call, so the writer cannot see the others. Fix in the prompt: vary the opener; put "upset" mid-sentence or at the end at least half the time. Fix in code: none.
2. A sentence repeats word for word between the matchup of the week and its recap chapter, because both chapters hold the same facts. Fix: the recap of the matchup of the week cites different facts from the matchup chapter, or the recap gets a note that the matchup chapter already told the headline, so lead with something else.
3. Three chapters have no joke at all. "No filler" removed "two jokes" and the writer took the easy road. Fix in the prompt: every blurb has at least one joke, and a reaction sentence counts.
4. Every sentence carries a number in six chapters. Fix in the prompt: at least one sentence per blurb carries no number. Fix in code: a blurb of 3 or more sentences where every sentence has a digit fails the code check.
5. "decider", "margin driver", and "the biggest gap of any decider" still appear where a plain phrase fits. Fix: the gated word list keeps the marker rule, and the prompt gives one plain phrase per stat term as an example.

Also: "a 8.13 projection" needs "an". Add a code check for "a" before a digit that reads as a vowel sound (8, 11, 18, 80s), or a prompt line.

Spec: `.scratch/tone/PRD.md`. This ticket amends "The voice".

**Blocked by:** None. Main holds tickets 01 to 06.

**Status:** done

- [ ] The prompt changes above are in, with a prompt text test for each new line.
- [ ] The code check fails a blurb of 3 or more sentences where every sentence has a digit, with a test.
- [ ] The code check or the prompt handles "a" before 8, 11, 18, with a test.
- [ ] Rewrite week 6 chapters `game_changer`, `recap_3`, `recap_4`, `next_week`, `position_leaders`, and `rankings` on main, one call each, no fallback. Paste the before and after of two of them in a comment at the bottom of this file.
- [ ] Brian publishes.

## Comments

- 2026-10-22: found after the tone 06 rewrite. Flags listed by the rewrite agent: four "In an upset" openers; "without him, that is a loss" twice; "is now listed Out" in four recaps; a "who" tail in recap_2; "decider" in three chapters; zero jokes in recap_3, recap_4, game_changer; recap_4 repeats motw sentences 0 and 2 verbatim.

- 2026-11-02: `main` holds the merge, on the word of tone ticket 09, `09-leftovers-after-the-second-rewrite.md`. Status set to done by the state-file sweep of agent-habits 02.
