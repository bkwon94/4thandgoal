# 03: The six verbs, the narrowing, and the choice of tests

Spec: `.scratch/faster-evidence/PRD.md`. Acceptance tests AT-5, AT-6, and AT-11.

**App:** site

**What to build:** A `steps.json` can list steps with the six verbs: `click`, `fill`, `scroll`, `wait`, `shot <name>`, and `url`. A named shot is `<name>-<width>-<theme>.png`. The `url` verb writes `url-<width>-<theme>.txt`. With no `shot` step, the runner takes one shot after the last step. The optional `widths` and `themes` narrow the shots. An optional list of test ids after the slug runs only those tests.

**Blocked by:** 02

**Status:** done

- [x] A test on a small real folder proves each verb: a click, a fill, a scroll to a selector and to the end, a wait on a selector, the URL, and a time.
- [x] The same test proves a named shot before and after a click, and the `url` file holds the URL after the click.
- [x] A test proves `widths: [768, 1280]` writes no 375 file, and `themes: ["light"]` writes no dark file.
- [x] A real run with one test id runs only that test.
- [x] `pnpm check:fast` of the site passes.

## Comments
- Closed by the merge of PR #12.
