# 05: One record set

Spec: `.scratch/one/PRD.md`. Implementation Decisions "The records".

**What to build:** A reader finds one ADR series, one glossary, and one root CLAUDE.md. Each app keeps a short CLAUDE.md with its own commands.

**Blocked by:** 03.

**Status:** ready-for-agent

- [x] The ADRs of both apps form one series in the root `docs/adr/`.
- [x] A map file lists each old number, its app, and its new number.
- [ ] Each old ADR number in a doc, a ticket, or a code comment gets its new number.
- [x] One root `GLOSSARY.md` holds the terms of both apps. A term with two meanings stops the ticket, and the agent names the conflict to Brian.
- [x] The root CLAUDE.md explains both apps, the flow, and the tracker. Each app CLAUDE.md holds only its commands and its rules.
- [x] The rule tests that read the ADRs, the READMEs, or the glossary pass at the new paths.
