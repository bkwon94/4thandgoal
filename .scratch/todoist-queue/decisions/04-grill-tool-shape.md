# 04: Is the tool one shared script, or inline calls in each skill?

Map: `.scratch/todoist-queue/MAP.md`.

**Kind:** grill

**Blocked by:** 02

**Status:** done

## Question

The skills can push in two ways. One shared script in the plugin reads a ticket file and makes the Todoist task match it. Or each skill calls `td` inline with its own flags. The spec needs one shape. The choice sets where the key lookup, the soft fail, the PATH fix, and the import live, and how the shape gets tested.

## Decision

Brian decided this in the grill of 2026-11-12. He took option (A): one shared script, `scripts/queue.py`.

1. **The script follows the pattern of `scripts/verdict.py`.** It uses only the Python standard library. Its tests sit beside it in `scripts/test_queue.py`, and `make check-fast` runs them through the `scripts-check` target. A skill calls it with `python3 scripts/queue.py`.
2. **The subcommands:**
   - `push <ticket path>` makes the task of one ticket or decision ticket match the file.
   - `pull <feature>` writes the labels of the queue into the `Status:` lines of that feature.
   - `wait <feature> <approve-prd|approve-acceptance|approve-tickets|merge-pr N>` makes a wait task.
   - `sweep` runs the merge sweep of decision 03.
   - `import` loads the open work once, after the audit.
3. **The script owns the hard parts.** These are the nvm PATH, a timeout of about 10 seconds per `td` call, the one read of the project, the key match, the label map, the order of the archive, and the soft fail. A failed call prints one warning line and exits 0. Each skill adds one line per push point from the table of decision 03.
4. **The tests use real input and no mock.** They cover the pure parts: a real ticket file from `.scratch/` into the task it should become, and a compare of that task with saved JSON output of `td`. The `td` calls get a real run in the evidence of the spec.

Reason: the status map, the key match, the label replacement, and the archive order are real logic. Tested code holds them better than prose in six skills, which agents would read in different ways. The `scripts/` folder is the precedent, and its tests already run in `make check-fast`.

Glossary: this ticket added the terms Queue, Wait task, and Merge sweep to the Workflow section of `GLOSSARY.md`.
