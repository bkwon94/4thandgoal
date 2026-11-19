# 05: The verify skill and one flow

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-1, AT-6, AT-8 and AT-11.

**App:** site

**What to build:** The `verify` skill boots the local API in its evidence mode and the export of a client, then runs the Week report flow through the evidence runner. Codex finds the skill through a tracked link. The evidence runner gets the verb `expect`, and fails on a missing element, a failed `expect`, a page error, a console error, an API response of 4xx or 5xx, or an overlap.

**Blocked by:** none

**Status:** done

- [x] The skill lists of Claude Code and of `codex` each name `verify` once, from one source file.
- [x] A smoke run of the Week report of cpc 2026 week 10 passes, at 390x660 WebKit and 1280x800, light theme.
- [x] A seeded `expect` of "Week 99" fails the run and names the flow and the step.
- [x] A seeded overlap fails the run and names the two elements.
- [x] An evidence round with no widths still shoots 375, 768, and 1280 in both themes.

## Comments

Closes with the squash merge of the spec PR: `trusted-green-05` (`567f68ff`) merged into `trusted-green` as `c2cefe99` on 2026-11-18.
The Playwright project `rules` gained 8 tests, and AT-1, AT-6, AT-8, and AT-11 have PASS.
A Next.js `SecurityFatalError` stops the first build of each run from an agent session, and a second run builds.
The builder did not count the files it read; the ticket commit changed 12 files: .agents/skills/verify, .claude/skills/verify/SKILL.md, .claude/skills/verify/flows.json, apps/site/AGENTS.md, apps/site/e2e/evidence-rules.spec.ts, apps/site/e2e/evidence.ts, apps/site/e2e/smoke-rules.spec.ts, apps/site/e2e/smoke.spec.ts, apps/site/e2e/smoke.ts, apps/site/package.json, apps/site/playwright.config.ts, apps/site/scripts/smoke.mjs.
