# 05: One record set

Spec: `.scratch/one/PRD.md`. Implementation Decisions "The records".

**What to build:** A reader finds one ADR series, one glossary, and one root CLAUDE.md. Each app keeps a short CLAUDE.md with its own commands.

**Blocked by:** 03.

**Status:** done

- [x] The ADRs of both apps form one series in the root `docs/adr/`.
- [x] A map file lists each old number, its app, and its new number.
- [x] Each old ADR number in a doc, a ticket, or a code comment gets its new number.
- [x] One root `GLOSSARY.md` holds the terms of both apps. A term with two meanings stops the ticket, and the agent names the conflict to Brian.
- [x] The root CLAUDE.md explains both apps, the flow, and the tracker. Each app CLAUDE.md holds only its commands and its rules.
- [x] The rule tests that read the ADRs, the READMEs, or the glossary pass at the new paths.

## Comments

- The merge: `one-05-records` merged as `db483c6` on 2026-11-03, with commits `e8eaf8c`, `4e533fa`, `18566f1`, `0367834`, and `27333a4`. The fix of ADR 0017 and the Best adds entry landed as `59073df`.
- The proof: `make check` in the pipeline passed with 1540 tests, and `pnpm check:fast` passed with 565 tests. `git grep` finds no old ADR path outside the map. `git log --follow -m` on a moved pipeline ADR shows its old commits.
- The notes: the map is `docs/adr/README.md`. Plain `git log --follow` stops at the move, because the old history sits behind the subtree merge, so add `-m`. Brian chose four renames: Test verdict, Proposed trade, Top pickups, and Prose block. Ticket 11 renames `chapter` in the pipeline code. Ticket 04 made ADR 0017 false, and `59073df` fixed it.
- Read 12 files: CLAUDE.md, .scratch/one/PRD.md, .scratch/one/issues/05-one-record-set.md, docs/agents/issue-tracker.md, GLOSSARY.md, apps/pipeline/GLOSSARY.md, apps/pipeline/CLAUDE.md, apps/pipeline/docs/agents/domain.md, docs/adr/0018-the-site-and-the-pipeline-live-in-one-repo.md, docs/adr/0019-main-is-the-record-branch.md, docs/adr/0020-a-spec-pr-merges-on-the-verdicts-of-its-acceptance-tests.md, docs/adr/0021-the-tracker-is-local-markdown.md.
