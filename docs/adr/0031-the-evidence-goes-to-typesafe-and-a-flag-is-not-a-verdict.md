# The evidence goes to TypeSafe, and an Evidence flag is not a Test verdict

The evidence stage of `cpc:implement` records each acceptance test. The `evidence-flags` spec adds a step. The command `cornerstone evidence-flags` sends the evidence of each test to TypeSafe Jev. Jev answers typed questions with a probability. A yes past the cut of a question is an Evidence flag. This record extends ADR 0029, which covers blurbs and fact sheets only.

## The data that goes to TypeSafe

1. **The text of the test.** The command sends the entry of the test in `ACCEPTANCE.md` and its entry in `EVIDENCE.md`.
2. **The files of the evidence.** It sends `output.txt`, `fields.diff`, `steps.json`, and the other text files of `evidence/AT-<n>/`.
3. **The screenshots.** It sends each shot of `evidence/AT-<n>/`, cut into tiles when a shot is tall.

The shots show the site as a reader sees it. So they show the names of managers and players. The text files hold the same names. The names are the same data as in ADR 0029.

TypeSafe does not train on the data. This account has no zero data retention, as in ADR 0029.

## An Evidence flag is not a Test verdict

1. **A flag is advice to the evidence agent.** The agent records the test again, hands a product defect to a fix group, or writes why it disagrees.
2. **A flag never reaches the Judge.** The flags go into `.scratch/<slug>/FLAGS.md`. The Judge reads neither that file nor any flag, and `judge.md` does not change.
3. **A flag never gives PASS, FAIL, or BLOCKED.** Only the Judge gives a Test verdict (ADR 0026). A false flag costs a few minutes and cannot fail a test.
4. **A missing flag weakens no check.** A Jev miss leaves the Judge as the gate, as it is now. A Jev error gives no flag, and the evidence stage goes on.

## Consequences

- The data that leaves the repo grows. A reader finds what leaves, and why, in this record and in ADR 0029.
- `FLAGS.md` is committed with the evidence, so a later spec can set the cuts from real labels.
- No test calls TypeSafe. The command runs against the live API by hand, for the evidence.

We rejected two alternatives:

- **Put the flags in `EVIDENCE.md`.** The Judge reads that file, and a flag tells the Judge where to look.
- **Let a flag block the merge.** A false flag would then fail a good test.
