# 03: grade-bar in CI

Spec: `.scratch/trusted-green/PRD.md`. Acceptance tests AT-29.

**App:** site

**What to build:** The full site check runs the grade-bar project in its norcal pass, so CI runs each check that exists.

**Blocked by:** none

**Status:** done

- [x] The full site check runs the grade-bar project while the export holds norcal.
- [x] The site job of `Check` on the PR shows grade-bar as passed.
- [x] The site job ends in under 25 min, and the ticket notes its time: 10 min 47 s on PR #70.

## Comments

Closes with the squash merge of the spec PR: `trusted-green-03` (`b499249f`) merged into `trusted-green` as `30695bbe` on 2026-11-18.
`client-steps.test.mjs` has 3 tests, and AT-29 has PASS on the `site-browser` job of PR #70, which took 10 min 47 s.
Fix E1 builds a client with the finder on two times, because the floor of `analyzer-stage.spec.ts` needs the normal build.
The builder did not count the files it read; the ticket commit changed 5 files: apps/site/AGENTS.md, apps/site/package.json, apps/site/scripts/build-each-client.mjs, apps/site/scripts/client-steps.mjs, apps/site/scripts/client-steps.test.mjs.
