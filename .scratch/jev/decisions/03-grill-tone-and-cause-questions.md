# 03: Which tone and cause questions does the Jev check ask, and where do the flags show?

Map: `.scratch/jev/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

The rules of `prompts/tone.md` and `midseason/prompts/voice.md` have no code check today. `GATED_WORDS` in `facts/verifier.py` catches only a fixed list of cause words.

Choose the questions. Candidates:

- "Does this sentence joke about a player's injury or health?"
- "Does this sentence mention life outside fantasy?"
- "Does this sentence explain its own joke?"
- "Does this sentence say one event caused the result?"

Choose where a flag shows: the build log, a file in `clients/<slug>/build/<season>/`, or the publish prompt.

## Decision

Brian decided on 2026-11-09.

The Jev check asks four Noul questions per sentence, beside the facts check:

1. "Does this sentence joke about a player's injury, body, or health?" The rule is `tone.md:5`, `:26`, and `:76`.
2. "Does this sentence mention life outside fantasy, such as a job, a family, a home, or money?" The rule is `tone.md:55` and `midseason/prompts/voice.md:26`.
3. "Does this sentence explain the joke it, or the sentence before it, just made?" The rule is `tone.md:24` and `:45`.
4. "Does this sentence say that one event caused the result of the game?" Code then applies the `.driver` gate of `GATED_WORDS` (`verifier.py:40`). The regex stays.

The filler question and the stock-shape question are out. The code check of the reaction sentence covers filler. A stock shape is a text pattern, so it belongs in code.

The flags show in two places:

1. The Jev log file beside `verify.json`. Ticket 06 sets its format.
2. A summary block in the `publish` prompt, above the y/N at `apps/pipeline/src/cornerstone/cli.py:603`. Each line gives the question, the probability, the prose block, the sentence number, and the sentence.

Brian may mark each flag right or wrong. The mark is optional and goes into the Jev log as a label for the later spec that makes the flags gate the build. With no mark, nothing changes.

The default threshold to show a flag is a probability of 0.7, the starting cutoff in https://docs.typesafe.ai/confidence.md. The spec may change it. A push notification is out, because a log-only check needs no second channel.
