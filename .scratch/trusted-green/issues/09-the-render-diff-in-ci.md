# 09: The render diff in CI

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-25, AT-26 and AT-36.

**App:** pipeline

**What to build:** A CI job runs on each PR that changes the pipeline, the API, or a package, as the scope script selects. It reads its script from `main`. It runs `page-json` of the latest week of each client with the code of `main` and with the code of the PR, then diffs `page.json`, `topics.json`, and `waiver.json`. While `main` has no facts-only rebuild, it runs the render diff only and prints "render only".

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] The base and head render diff of cpc and norcal 2026 week 10 reports 0 diffs in under 60 s.
- [ ] With `main` as the base, the run prints "render only" and exits 0.
- [ ] The workflow checks out its script from the default branch.
- [ ] The workflow names no `ANTHROPIC_API_KEY` and no `TYPESAFE_API_KEY`.
