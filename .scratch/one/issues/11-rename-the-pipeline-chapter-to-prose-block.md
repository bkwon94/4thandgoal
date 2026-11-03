# 11: Rename the pipeline chapter to prose block

Spec: `.scratch/one/PRD.md`. Implementation Decisions "The records". Glossary: **Prose block**, **Chapter**.

**What to build:** The pipeline code names its unit of prose a prose block, as the glossary does. "Chapter" then names only the site card.

**Blocked by:** 05.

**Status:** ready-for-agent

- [ ] The pipeline code, its tests, and its prompts name the unit of prose `prose_block`, not `chapter`.
- [ ] The `--chapter` option of `cornerstone rewrite` gets a new name, and the README and the Tuesday runbook say it.
- [ ] A published file keeps its keys, or the site schema and `PAGE_SCHEMA_VERSION` change together.
- [ ] The **Prose block** entry of `GLOSSARY.md` drops the line that says the code still names it `chapter`.
- [ ] `make check` passes in `apps/pipeline`, and the golden files show no change in the rendered text.
