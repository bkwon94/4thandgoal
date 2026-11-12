# 07: The skills call the script at each push point

Spec: `.scratch/todoist-queue/PRD.md`. Acceptance tests AT-29.

**App:** both. The `4ag` plugin skills, with no product code.

**What to build:** Each `4ag` skill keeps the queue current with no extra step from Brian. Each skill starts with the merge sweep. At each row of the push table in the spec, the skill calls `push`, `pull`, or `wait` with one line. The skill names each missed push in its final report. `4ag:plan` stage 2 and `4ag:implement` commit the result of `pull` on the spec branch.

**Blocked by:** 04 and 05

**Status:** ready-for-agent

- [ ] Each of the six skills starts with the merge sweep.
- [ ] Each row of the push table has a call in its skill, at its step.
- [ ] Each skill tells the agent to name each missed push in the final report.
- [ ] A grep of the skills for the script, laid beside the push table, shows no gap.
