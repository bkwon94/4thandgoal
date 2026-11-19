# 05: The verify skill and one flow

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-1, AT-6, AT-8 and AT-11.

**App:** site

**What to build:** The `verify` skill boots the local API in its evidence mode and the export of a client, then runs the Week report flow through the evidence runner. Codex finds the skill through a tracked link. The evidence runner gets the verb `expect`, and fails on a missing element, a failed `expect`, a page error, a console error, an API response of 4xx or 5xx, or an overlap.

**Blocked by:** none

**Status:** in-review

- [ ] The skill lists of Claude Code and of `codex` each name `verify` once, from one source file.
- [ ] A smoke run of the Week report of cpc 2026 week 10 passes, at 390x660 WebKit and 1280x800, light theme.
- [x] A seeded `expect` of "Week 99" fails the run and names the flow and the step.
- [x] A seeded overlap fails the run and names the two elements.
- [x] An evidence round with no widths still shoots 375, 768, and 1280 in both themes.
