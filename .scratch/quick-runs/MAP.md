# Quick runs: map

App: neither. The work changes the plugin, `scripts/queue.py`, `AGENTS.md`, `GLOSSARY.md`, and `docs/adr/`.
Spec branch: `quick-runs`.

## DESTINATION

One spec that adds the skill `4ag:quick`, which takes a bug or a small change to a merged PR fast, with
debug skills first. It adds the records: four glossary terms and ADR 0033.

## DECISIONS SO FAR

- `4ag:quick` is a new skill. The six skills keep their steps; `4ag:plan` and `AGENTS.md` get a pointer. `decisions/01-grill-the-quick-flow.md`.
- A quick run is one branch and one PR, up to five items of one kind, under four boundary rules; a failed rule hands off to `4ag:plan`. `decisions/01-grill-the-quick-flow.md`.
- The record is `.scratch/bugs/<slug>.md` or `.scratch/quick-wins/<slug>.md`, on a branch `bug-<slug>` or `win-<slug>`, with no `state.md` row. `decisions/01-grill-the-quick-flow.md`.
- A Bug uses `diagnosing-bugs`, a Quick win uses `tdd`, and a text-only item uses neither. Red first, green after, a narrow Judge, no `verdict` gate. `decisions/01-grill-the-quick-flow.md`.
- One worktree, items in sequence, one subagent per item, one checkpoint with Brian at the start. `decisions/01-grill-the-quick-flow.md`.
- The queue gets the sections `bugs` and `quick-wins`, which the sweep never archives. Brian drops a task there; `4ag:quick` takes it as input and adds the key line. `decisions/01-grill-the-quick-flow.md`.

## NOT YET SPECIFIED

None.

## OUT OF SCOPE

- Parallel items in their own worktrees. Most runs hold one or two items; add it if a run of five hurts.
- A `verdict` gate on a quick PR. Add it if a FAIL slips into a merge.
- Capital section names, such as "Bugs". The lower-case folder slug is enough.
- A change to the flow of `4ag:implement` or `4ag:review`. A quick run has its own short steps.
