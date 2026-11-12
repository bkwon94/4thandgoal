# The push table of the PRD, beside the grep hits

Each row is a row of the push table in `.scratch/todoist-queue/PRD.md`, "The push points in the skills". The right column names the hit of `grep -rn 'scripts/queue.py' .claude/plugin/skills/` in `output.txt`, with the heading above it.

| Skill and step | Queue action | Grep hit |
| --- | --- | --- |
| Start of each `4ag` skill | `sweep` | `plan/SKILL.md:17`, `to-spec/SKILL.md:15`, `to-acceptance/SKILL.md:15`, `to-tickets/SKILL.md:15`, `implement/SKILL.md:17`, `review/SKILL.md:17`, each under `## The queue` |
| `4ag:plan` stage 1, after the commit | `push` each decision ticket | `plan/SKILL.md:51`, under `## Stage 1: write the map`, step 9 |
| `4ag:plan` stage 2 start | `pull <feature>` | `plan/SKILL.md:55`, under `## Stage 2: clear one decision ticket`, step 1 |
| `4ag:plan` stage 2 end | `push` the decision ticket | `plan/SKILL.md:66`, under `## Stage 2: clear one decision ticket`, step 9 |
| `4ag:to-spec` end | `wait <feature> approve-prd` | `to-spec/SKILL.md:52`, under `## The end` |
| `4ag:to-acceptance` start and end | complete `approve-prd`, then `wait <feature> approve-acceptance` | `to-acceptance/SKILL.md:17` under `## The queue`, and `to-acceptance/SKILL.md:51` under `## The end` |
| `4ag:to-tickets` start and end | complete `approve-acceptance`, then `wait <feature> approve-tickets`, then `push` each ticket after the approval, and complete `approve-tickets` | `to-tickets/SKILL.md:17` under `## The queue`; `to-tickets/SKILL.md:35` step 9 and `to-tickets/SKILL.md:36` step 10, under `## Steps` |
| `4ag:implement` start | `pull <feature>` | `implement/build.md:20`, under `### The Spec branch`, step 5 |
| `4ag:implement` stage 1 | `push` each ticket that changes to `in-review` or `blocked` | `implement/build.md:69` under `### Merge one ticket`, and `implement/build.md:78` under `### A blocked ticket` |
| `4ag:implement` stage 5, before the push to GitHub | no queue action | no hit in `implement/pr.md` before line 29 |
| `4ag:implement` stage 5, after `gh pr create` | `wait <feature> merge-pr <N>` | `implement/pr.md:29`, under `## Open the PR`, step 5, after `gh pr create` in step 4 |
| `4ag:review` | `push` each ticket whose status changes | `review/SKILL.md:60`, under `## The rules` |
