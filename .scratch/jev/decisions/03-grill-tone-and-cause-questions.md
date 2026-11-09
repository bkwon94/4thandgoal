# 03: Which tone and cause questions does the Jev check ask, and where do the flags show?

Map: `.scratch/jev/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** open

## Question

The rules of `prompts/tone.md` and `midseason/prompts/voice.md` have no code check today. `GATED_WORDS` in `facts/verifier.py` catches only a fixed list of cause words.

Choose the questions. Candidates:

- "Does this sentence joke about a player's injury or health?"
- "Does this sentence mention life outside fantasy?"
- "Does this sentence explain its own joke?"
- "Does this sentence say one event caused the result?"

Choose where a flag shows: the build log, a file in `clients/<slug>/build/<season>/`, or the publish prompt.

## Decision

None yet.
