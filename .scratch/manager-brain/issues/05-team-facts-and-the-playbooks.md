# 05: Team facts and the Playbooks

Spec: `.scratch/manager-brain/PRD.md`. Acceptance tests AT-4, AT-9, and AT-35.

**App:** pipeline

**What to build:** The Advisor knows each team as a manager does. The sheet states for each side the race group (In, Bubble, or Out) and the playoff odds, a bye in the trade week, the RB depth before and after the trade in plain words, and the depth of the other team at the positions of the trade. The pipeline uses the term race group, as the site does. Each old adjuster writes its facts as a Measure and moves nothing, and the trend Measure reads more than snaps. Each client has a Playbook in its voice folder that the Advisor reads: cpc with its tips from decision 01, and NorCal with general tips and no league-specific claim.

**Blocked by:** 02

**Status:** in-review

- [x] The sheet of trade 6 of the eval has a fact "RBs in the top 36 go from N to M" for each side, and N and M match the rosters.
- [x] The sheet states the race group and the odds of each side, and a bye fact for a side with a bye in the trade week.
- [x] The cpc Playbook holds its tips, and the NorCal Playbook holds general tips only.
- [x] The Advisor prompt carries the Playbook of the client.
- [x] `make check-fast` passes.
