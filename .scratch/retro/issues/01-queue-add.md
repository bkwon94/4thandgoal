# 01: `queue.py add` files a task in Bugs, Quick Wins, or Ideas

Spec: `.scratch/retro/PRD.md`. Acceptance tests AT-3, AT-4, AT-5, AT-6, and AT-7.

**App:** both

**What to build:** A new subcommand `add` of the queue script. `python3 scripts/queue.py add <section> <title> --description <text>` makes one task in the section `Bugs`, `Quick Wins`, or `Ideas` of the project `4thandgoal`. The task has the label `needs-triage` and no key line. The subcommand makes the section first if it is missing. A section outside the three plans no command, prints one warning that names the three, and exits 0. `--dry-run` prints the plan and sends nothing. A pure plan function takes a queue snapshot and returns the `td` commands, in the same shape as the plan functions of `push`, `wait`, and `take`. `4ag:quick` can take the new task with `queue.py take`.

**Blocked by:** none

**Status:** in-review

- [x] A unit test of the plan function covers each of the three sections, a missing section, a bad section, and the label `needs-triage`. It passes.
- [x] `add Bugs` and `add "Quick Wins"` with `--dry-run` each plan one `td task add` in the named section, with no `4ag:` key line.
- [x] `add Backlog ... --dry-run` plans no command, prints one warning, and exits 0.
- [x] A real task that `add` made gets the key line from `take --dry-run`, above its old description. The probe task is then deleted.
- [x] The section "The queue" of `docs/agents/issue-tracker.md` names the subcommand `add`.
