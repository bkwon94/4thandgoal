# 02: queue.py take claims a phone task

Spec: `.scratch/quick-runs/PRD.md`. Acceptance tests AT-4 and AT-5.

**App:** both

**What to build:** Brian files a bug or a small change from his phone as a task in `Bugs` or `Quick Wins`. The subcommand `take` finds the open task of that name in one of the two sections, prints its title and description, and puts the key line `4ag: <path>` first in its description. The task keeps its id, its section, and its old text. A name with no open task in the two sections plans no command, prints one warning, and exits 0.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] A test shows that `take` plans one update that puts the key line first and keeps the old description.
- [ ] A test shows that `take` of an unknown name plans no command and exits 0.
- [ ] `take` honors `--dry-run` and `--root`, like the other subcommands.
- [ ] A real `take` on one task in `Bugs` keeps its id and its section.
- [ ] `make check-fast` passes at the root.
