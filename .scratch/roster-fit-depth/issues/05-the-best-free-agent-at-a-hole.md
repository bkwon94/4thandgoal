# 05: The best free agent at a hole

Spec: `.scratch/roster-fit-depth/PRD.md`, "The free agents", "The facts", "The cache key". Glossary: "Hole",
"Position rank". Decision record: ADR 0003.

**What to build:** The snapshot gains, per position, the free agents who pass the waiver pool's eligibility rule:
not rostered, on an NFL team, Active on Sleeper, or Inactive and out as a stash. The saved path and the live path
both build it from the players file minus the rosters, so a Saturday grade and the Tuesday build agree. The best
free agent at a position is the one with the best position rank. The hole fact of ticket 02 names him and his
rank, so the reader knows whether waivers fix the hole. This read feeds a fact only, never a step. The grade key
and the finder key hash the free-agent ids per position.

**Blocked by:** 02 (A hole steps the grade).

**Status:** ready-for-agent

- [ ] The week 6 fixture snapshot lists the free agents at RB, and a named Inactive player is not among them.
- [ ] A free agent on injured reserve with no out tag is not among them.
- [ ] The live snapshot and the saved snapshot give the same free agents for the same raw.
- [ ] The hole fact for a new RB2 hole names the best free agent at RB and his rank.
- [ ] A hole at a position with no eligible free agent gets a fact that says so.
- [ ] A new free agent at RB changes the grade key and the finder key.
- [ ] The analysis checker accepts a sentence that quotes the cited free agent's rank.
