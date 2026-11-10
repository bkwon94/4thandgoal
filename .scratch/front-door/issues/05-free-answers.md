# 05: Free answers stream with tools and a Jev check

Spec: `.scratch/front-door/PRD.md`. Acceptance tests AT-11, AT-12, AT-19, AT-20, AT-21, AT-22, AT-44, AT-55.

**App:** both

**What to build:** A free answer streams from Claude Sonnet 5.5 at `low` effort, run by Pydantic AI on the API and read by `useChat` on the site, through `VercelAIAdapter`. Claude has tools over this season and the nflverse game logs, with at most 4 tool calls. Each tool call shows as a plain step. After the last word, Jev checks each claim against the tool results: "checking" turns into "checked", a failed claim shows "Fixing a number…" and one more text, and a second fail gives the honest miss. A half fit shows the top Topic as a chip under the answer. The words sharpen from a blur as they stream. No control stops a stream.

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] The first commit pins `pydantic-ai`, `ai`, and `@ai-sdk/react` to a pair that the adapter supports.
- [ ] "highest scoring team this season" names the team with the most points for in weeks 1 to 8 (AT-11), with the top Topic chip under it (AT-12).
- [ ] "week 1 results" shows plain tool steps, and no copy names Jev, the Advisor, or the Finder (AT-19).
- [ ] The mark turns from "checking" to "checked" in the ink color, with no bounce (AT-20).
- [ ] A pytest run with one failed claim shows the rewrite, and one with two shows the honest miss (AT-21, AT-22).
- [ ] Each new word shows blurred, then sharp (AT-44). No stop control shows (AT-55).
