# 10: Floor, scope checks, and glossary

Spec: `.scratch/card-polish/PRD.md`. Acceptance tests AT-27, AT-28, AT-29, AT-31, and AT-32.

**App:** site

**What to build:** The floor check covers the new open states: an open game card, an open ladder card, an open Index list row, the stage, and the Season So Far dial. Both clients pass it. The out-of-scope checks prove the manager hero, the pipeline, and the repo stay clean. `GLOSSARY.md` gains Open card, Grade dial, Trend tile, Ready halo, Index list, and the race groups In, Bubble, and Out.

**Blocked by:** 01, 02, 03, 04, 05, 06, 07, 08, and 09

**Status:** ready-for-agent

- [ ] `CLIENT=cpc pnpm check:floor` and `CLIENT=norcal pnpm check:floor` pass with the new open states.
- [ ] No page scrolls sideways at 390 px, and each new control is 44 px or more.
- [ ] The manager hero diff against `main` is empty.
- [ ] `git diff main --stat -- apps/pipeline packages/*/python` is empty.
- [ ] The Scrolltide copy search over the diff finds no match.
- [ ] `GLOSSARY.md` holds the new terms, each with one meaning.
- [ ] `make check-fast` passes.
