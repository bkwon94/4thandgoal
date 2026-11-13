# 01: What is the shape of a quick run?

Map: `.scratch/quick-runs/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

How does a bug or a small change get to a merged PR fast, and still keep the One rules?

## Decision

Brian decided each point in the grill of 2026-11-13. The records are ADR 0033 and the Workflow terms Quick run, Bug, Quick win, and Done condition in `GLOSSARY.md`.

1. **Destination.** A new skill `4ag:quick`. `4ag:plan` stays for features. The other skills get only a pointer.
2. **Boundary.** One branch and one PR, up to five items of one kind. No new glossary term, no ADR, and no moved seam. Each item has a done condition of one sentence. The skill states its call on the rules, and Brian can override it. If a rule fails mid-work, the run stops and hands off to `4ag:plan` with what it learned.
3. **Record.** `.scratch/bugs/<slug>.md` for Bugs, `.scratch/quick-wins/<slug>.md` for Quick wins. It holds the items, the kind and done condition of each, the cause found, the evidence, the Judge lines, and the close comment. It is not under `issues/`, so it gets no `state.md` row. The PR body names no league manager (ADR 0021).
4. **Proof.** Red first, green after, from the same loop. A fresh Judge asks two questions per item: does the red evidence show the bug of the done condition, and does the green evidence come from the same loop at the fixed commit? The Judge writes PASS, FAIL, or BLOCKED into the quick file. An item whose evidence is only a diff of text or config skips the Judge. No `verdict` gate.
5. **Method.** A Bug uses `mattpocock-skills:diagnosing-bugs`, all phases; its Phase 1 command is the red evidence. A Quick win uses `mattpocock-skills:tdd`. A text-only item uses neither. A loop uses the one fake of a port (ADR 0015) or real data, never a new mock. A phone-only bug gets its red evidence from a screenshot of a LAN probe page from Brian. The spec installs `diagnosing-bugs` into `~/.agents/skills/` for Codex.
6. **Build.** One worktree from `main`. Items run in sequence, one subagent per item: `opus` for a Bug, `sonnet` for a Quick win. The orchestrator edits a text-only item itself. Each commit runs the prek hook; CI runs the full suite.
7. **Checkpoints.** One, at the start: Brian reads the items, kinds, and done conditions, and replies "go" or a fix. Then the run goes to an open PR with no stop, except a `STUCK`, a failed boundary rule, or a phone screenshot that an item needs. Brian merges.
8. **Queue.** The folder names the section: `bugs` and `quick-wins`. One run is one task, with the key line `4ag: <path>`. The skill pushes it as `in-progress` at the start. The last commit before the push sets `Status: done` and writes the close comment. A wait task for the PR lets the merge sweep close both. The sweep never archives `bugs` or `quick-wins`. Brian can drop a task into either section from his phone; `4ag:quick <task name>` reads it, writes the file, and adds the key line to the same task.
9. **Kinds per run.** One kind per run. A mixed list becomes two runs and two PRs, and the skill can start both from one call.
10. **Terms and ADR.** The four terms above, a wider meaning of Test verdict, Judge, and ADR 0033, which amends ADR 0026.
