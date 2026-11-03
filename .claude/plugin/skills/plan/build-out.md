# The build-out: from the decisions to the tickets

`cpc:plan` runs these steps when no fog is left, or when Brian confirms that the feature has no fog. Stop for Brian at each of the three approvals. Work in the worktree of the Spec branch `<slug>`.

## Approval 1: the spec

1. Call the Skill tool for `cpc:to-spec`. Give it the feature slug.
2. It reads the map, the decision tickets, and this conversation. It records the choice of each `spec` decision ticket in the spec.
3. Show Brian the spec. Wait for his approval.
4. After the approval, set each `spec` decision ticket to `done` and move its line to DECISIONS SO FAR. Commit.

## Approval 2: the acceptance tests

1. Call the Skill tool for `cpc:to-acceptance`. Give it the feature slug.
2. Show Brian the list of tests. Wait for his approval.
3. After the approval, commit.

## Approval 3: the tickets

1. Call the Skill tool for `cpc:to-tickets`. Give it the feature slug.
2. Show Brian the breakdown. Wait for his approval.
3. After the approval, it writes the tickets and the `state.md` row. Run `make check-fast` at the root. Commit.

## The end

Tell Brian that the plan of the feature is done. Name the Spec branch and the first ticket.
