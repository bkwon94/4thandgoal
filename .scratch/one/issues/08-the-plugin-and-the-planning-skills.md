# 08: The plugin and the planning skills

Spec: `.scratch/one/PRD.md`. Solution parts 5 and 6, and Implementation Decisions "The plugin" and "The new feature shape".

**What to build:** Every session in the repo has the `cpc` plugin. Brian can take an idea to a map, clear the fog, and get a spec, an acceptance file, and tickets.

**Blocked by:** 06.

**Status:** done

- [x] The `cpc` plugin has a manifest, the repo marketplace file names it, and the repo settings turn it on.
- [x] `cpc:plan` writes a map with the four sections and one decision ticket for each fog item. It skips the map when no fog exists.
- [x] `cpc:plan` sends each decision ticket to `grilling`, `research`, `prototype`, or a spec, and records the decision on the map.
- [x] `cpc:to-spec` writes the PRD in our format. `cpc:to-acceptance` writes numbered tests with site or pipeline evidence. `cpc:to-tickets` writes the tickets and the `state.md` row.
- [x] Each skill checks at start that the global skills it calls exist. It stops and names a missing skill.
- [x] One dry run in a throwaway feature goes from idea to tickets. The throwaway feature is deleted after.

## Comments

- The merge: `one-08-plugin` merged as `45c3fd2` on 2026-11-03, with commits `d640371`, `4b1c22b`, `ec72553`, and `68b8218`. The fix of the pronouns in the skill text landed as `9430032`.
- The proof: `claude plugin validate .` passed. With `--plugin-dir`, a session lists `cpc:plan`, `cpc:to-spec`, `cpc:to-acceptance`, and `cpc:to-tickets`. A dry run in `.scratch/zz-dry-run/` made a map, 2 decision tickets, a PRD, 4 acceptance tests, and 2 tickets, and the root `make check-fast` passed with it in place. Commit `4b1c22b` holds the dry run.
- The notes: the dry run found 8 unclear steps, and `ec72553` fixed them. `cpc:to-tickets` adds the `state.md` row, not `cpc:plan`, because a row with no open ticket fails the tracker rule. The research skill is `mattpocock-skills:research`. A session loads the plugin only after a one-time install of the marketplace `cpc-local`.
- Read 16 files: CLAUDE.md, docs/agents/issue-tracker.md, docs/agents/state.md, GLOSSARY.md, .scratch/one/PRD.md, .scratch/one/issues/08-the-plugin-and-the-planning-skills.md, docs/adr/0018 to 0021, and in `~/repos/zero` branch `one`: marketplace.json, plugin.json, settings.json, plan/SKILL.md, build-out.md, to-acceptance/SKILL.md.
