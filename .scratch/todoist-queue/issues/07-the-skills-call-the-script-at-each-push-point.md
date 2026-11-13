# 07: The skills call the script at each push point

Spec: `.scratch/todoist-queue/PRD.md`. Acceptance tests AT-29.

**App:** both. The `4ag` plugin skills, with no product code.

**What to build:** Each `4ag` skill keeps the queue current with no extra step from Brian. Each skill starts with the merge sweep. At each row of the push table in the spec, the skill calls `push`, `pull`, or `wait` with one line. The skill names each missed push in its final report. `4ag:plan` stage 2 and `4ag:implement` commit the result of `pull` on the spec branch.

**Blocked by:** 04 and 05

**Status:** done

- [x] Each of the six skills starts with the merge sweep.
- [x] Each row of the push table has a call in its skill, at its step.
- [x] Each skill tells the agent to name each missed push in the final report.
- [x] A grep of the skills for the script, laid beside the push table, shows no gap.

## Comments

Closes with the squash merge of the spec PR. The branch `todoist-queue` holds commit `4e169391`, built on 2026-11-12.
Proof: A grep of the skills beside the push table shows no gap, as AT-29 records.
Read 3 files: .scratch/todoist-queue/PRD.md, .scratch/todoist-queue/ACCEPTANCE.md, .scratch/todoist-queue/VERDICTS.md.
