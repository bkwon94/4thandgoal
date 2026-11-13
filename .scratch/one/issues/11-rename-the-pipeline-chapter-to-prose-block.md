# 11: Rename the pipeline chapter to prose block

Spec: `.scratch/one/PRD.md`. Implementation Decisions "The records". Glossary: **Prose block**, **Chapter**.

**What to build:** The pipeline code names its unit of prose a prose block, as the glossary does. "Chapter" then names only the site card.

**Blocked by:** 05.

**Status:** wontfix

- [ ] The pipeline code, its tests, and its prompts name the unit of prose `prose_block`, not `chapter`.
- [ ] The `--chapter` option of `cornerstone rewrite` gets a new name, and the README and the Tuesday runbook say it.
- [ ] A published file keeps its keys, or the site schema and `PAGE_SCHEMA_VERSION` change together.
- [ ] The **Prose block** entry of `GLOSSARY.md` drops the line that says the code still names it `chapter`.
- [ ] `make check` passes in `apps/pipeline`, and the golden files show no change in the rendered text.

## Comments

Closes as wontfix in the audit of `todoist-queue` on 2026-11-12. Brian dropped it, because it fixes no real bug and changes nothing that a manager sees.
Proof: `apps/pipeline/src/cornerstone` holds 72 `chapter` names and `rewrite --chapter` stays, and `GLOSSARY.md` line 225 still says the code names it `chapter`. Its blocker 05 is done.
Read 1 file: .scratch/todoist-queue/audit.md.
