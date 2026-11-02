# 01: Reaction sentence

**What to build:** A blurb may hold one sentence that cites no fact, if it has no digit, no team name, no player name, and fewer than 8 words. "Rough week." is legal. The writer rule says so. The Claude verifier accepts a sentence with no fact IDs and no claim. The code check rejects a second uncited sentence, an uncited sentence with a digit, with a scope team or player name, or with 8 or more words. The failure feeds back to the writer on the second attempt like every other code failure. The reaction sentence counts in the sentence range. The glossary defines "reaction sentence".

Spec: `.scratch/tone/PRD.md`, sections "The reaction sentence" and "Glossary".

**Blocked by:** None (can start immediately).

**Status:** done

- [ ] Writer rule 1 says every claim cites a fact, and one reaction sentence per blurb may cite none, with the four limits and "put it after the sentence it reacts to".
- [ ] The verifier prompt has one line: a sentence with no fact IDs and no claim is supported.
- [ ] The code check fails a second uncited sentence, with the sentence index in the message.
- [ ] The code check fails an uncited sentence with a digit, a scope name, or 8 or more words.
- [ ] A fixture blurb with one legal reaction sentence passes the code check.
- [ ] A fake writer that returns two reactions gets feedback and passes on the second attempt with one, at the `write_and_verify` seam.
- [ ] A prompt text test guards the new writer line and the new verifier line.
- [ ] The glossary defines "reaction sentence" as in the spec.
- [ ] `make test` passes. Lint count on the branch is no higher than on main.

## Comments

- 2026-10-22: built on `tone` at `e0e11a9`, two Opus reviews, one fix pass. Awaits Brian merge with `--no-ff`.

- 2026-11-02: `main` holds the merge, on the word of tone ticket 09, `09-leftovers-after-the-second-rewrite.md`. Status set to done by the state-file sweep of agent-habits 02.
