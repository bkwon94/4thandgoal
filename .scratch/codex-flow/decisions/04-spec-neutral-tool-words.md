# 04: The neutral words for the tools

Map: `.scratch/codex-flow/MAP.md`.

**Kind:** spec

**Blocked by:** 02, 03

**Status:** done

## Question

The skill text says "call the Skill tool" and "start one subagent with the Agent tool". Codex has no tool with those names. The spec picks the neutral words that each harness reads the same way, and the place for the words that only one harness needs. Decisions 02 and 03 give the facts.

## Decision

The spec records it under Implementation Decisions, and Brian approved the spec on 2026-11-11. The skill text says "load the skill `<name>`" and "start a fresh subagent", with "with the strong model" for the Judge. A section "The harness words" in the root `AGENTS.md` maps each phrase to the tool of each harness.
