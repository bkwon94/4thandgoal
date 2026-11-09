# 03: The ADR, the glossary, and the README name the Jev port

Spec: `.scratch/jev/PRD.md`. Acceptance tests AT-12, AT-13, and AT-14.

**App:** pipeline

**What to build:** A reader learns why the pipeline calls TypeSafe, and what data leaves the repo, from the records alone. A new ADR, numbered after 0028, records TypeSafe Jev as the second model vendor, the blurbs and fact sheets with names that go to TypeSafe, and the rule that a Jev answer passes no check alone and a failed call never counts as a pass. It names the Jev port as the third port with one fake. The glossary term **Jev check** says that it runs beside the Claude check in the weekly build and logs only. The README of the pipeline package lists the Jev port beside the `Writer` port and names `TYPESAFE_API_KEY` beside `ANTHROPIC_API_KEY`. Nothing outside the pipeline changes.

**Blocked by:** 01

**Status:** in-review

- [x] The new ADR exists in `docs/adr/` and states the three choices and the third port.
- [x] `GLOSSARY.md` and the README of the pipeline package hold the lines above.
- [x] `docs/adr/README.md` lists the new ADR, if it lists each ADR.
- [ ] `git diff --stat main...jev` shows no change under `apps/site/`, `apps/api/`, `packages/analyzer/`, or `packages/midseason/`, and no change to the `publish` command.
