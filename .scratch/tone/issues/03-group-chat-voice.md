# 03: The group chat voice

**What to build:** The tone prompt opens with the voice: the league group chat, a member who watched every game and types like a person. Short sentences, varied length, contractions allowed. No chill. Roast freely. Deadpan allowed, not required. The "every blurb has at least two jokes" line is gone. "No filler sentence" replaces it: every sentence states a fact or reacts to the one before. The number rules stay. Writer rule 4 says: when you name a stat, use its vocabulary term; you need not name the stat; a plain phrase the cited fact supports is fine. Writer rule 15 keeps "lead with the claim" for a sentence that makes a claim. The gated words stay gated. The examples stay as they are in this ticket; ticket 05 replaces them.

Spec: `.scratch/tone/PRD.md`, sections "The voice" and "Vocabulary out of the prose".

**Blocked by:** None (can start immediately).

**Status:** done

- [ ] The tone prompt opens with the chat voice as the spec words it.
- [ ] The tone prompt has no "two jokes" line and has the "no filler sentence" line.
- [ ] Writer rule 4 reads as the spec words it. Rule 15 keeps "lead with the claim".
- [ ] Prompt text tests guard the voice line, the absent "two jokes" line, and the new rule 4.
- [ ] Every existing prompt test still passes.
- [ ] `make test` passes. Lint count on the branch is no higher than on main.

## Comments

- 2026-10-22: built on `tone` at `9d55907, fixes in 021f5f0`, two Opus reviews, one fix pass. Awaits Brian merge with `--no-ff`.

- 2026-11-02: `main` holds the merge, on the word of tone ticket 09, `09-leftovers-after-the-second-rewrite.md`. Status set to done by the state-file sweep of agent-habits 02.
