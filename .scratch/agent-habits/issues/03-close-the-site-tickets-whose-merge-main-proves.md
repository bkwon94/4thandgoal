# 03: Close the site tickets whose merge `main` proves

Spec: `.scratch/agent-habits/PRD.md`, part 2. The finding in the close comment of ticket 02.

**What to build:** `docs/agents/state.md` lists 11 features, and about 8 of them shipped. Their tickets still
read ready-for-agent. For each ticket whose merge `git log main --oneline --merges` proves, set the Status to
done and append one comment line that names the merge. Then rebuild the state file. The pipeline did the same
sweep inside its ticket 02, commit 2edb6f4; follow that form.

**Blocked by:** none.

**Status:** ready-for-agent

- [ ] For each feature in the state file, list its open tickets and the merges on `main` that name the feature or the ticket.
- [ ] A ticket closes only when a merge proves it, or when a later ticket of the feature says `main` holds it. Name the proof in the comment line.
- [ ] A ticket with no proof stays open. List each one under "Notes" in the state file, one sentence, for Brian.
- [ ] Rebuild the state file: each row names the lowest open ticket, one fact per cell.
- [ ] `pnpm check` passes. The rule `tracker/state-file` passes.
