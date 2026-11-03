# 08: The plugin and the planning skills

Spec: `.scratch/one/PRD.md`. Solution parts 5 and 6, and Implementation Decisions "The plugin" and "The new feature shape".

**What to build:** Every session in the repo has the `cpc` plugin. Brian can take an idea to a map, clear the fog, and get a spec, an acceptance file, and tickets.

**Blocked by:** 06.

**Status:** ready-for-agent

- [ ] The `cpc` plugin has a manifest, the repo marketplace file names it, and the repo settings turn it on.
- [ ] `cpc:plan` writes a map with the four sections and one decision ticket for each fog item. It skips the map when no fog exists.
- [ ] `cpc:plan` sends each decision ticket to `grilling`, `research`, `prototype`, or a spec, and records the decision on the map.
- [ ] `cpc:to-spec` writes the PRD in our format. `cpc:to-acceptance` writes numbered tests with site or pipeline evidence. `cpc:to-tickets` writes the tickets and the `state.md` row.
- [ ] Each skill checks at start that the global skills it calls exist. It stops and names a missing skill.
- [ ] One dry run in a throwaway feature goes from idea to tickets. The throwaway feature is deleted after.
