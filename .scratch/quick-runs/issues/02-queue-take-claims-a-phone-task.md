# 02: queue.py take claims a phone task

Spec: `.scratch/quick-runs/PRD.md`. Acceptance tests AT-4 and AT-5.

**App:** both

**What to build:** Brian files a bug or a small change from his phone as a task in `Bugs` or `Quick Wins`. The subcommand `take` finds the open task of that name in one of the two sections, prints its title and description, and puts the key line `4ag: <path>` first in its description. The task keeps its id, its section, and its old text. A name with no open task in the two sections plans no command, prints one warning, and exits 0.

**Blocked by:** 01

**Status:** done

- [x] A test shows that `take` plans one update that puts the key line first and keeps the old description.
- [x] A test shows that `take` of an unknown name plans no command and exits 0.
- [x] `take` honors `--dry-run` and `--root`, like the other subcommands.
- [x] A real `take` on one task in `Bugs` keeps its id and its section.
- [x] `make check-fast` passes at the root.

## Comments

- Closes with the squash merge of the spec PR of `quick-runs`. Commits: `0aaed552`, with the review fix `934b4338`. Date: 2026-11-13.
- `ATake` has 8 tests, and a real `take` on a scratch task kept its id and section; AT-4 and AT-5 have PASS.
- An unknown name prints the shared line "0 commands planned, none sent." after the warning.
- Read 5 files: AGENTS.md, .scratch/quick-runs/PRD.md, .scratch/quick-runs/ACCEPTANCE.md, scripts/queue.py, scripts/test_queue.py.
