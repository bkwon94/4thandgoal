# 03: The live eval reads the 28 trades

Spec: `.scratch/manager-brain/PRD.md`. Acceptance tests AT-19, AT-20, and AT-34.

**App:** pipeline

**What to build:** One command runs the real Advisor and the real Jev on the 28 trades of the test set of decision 04, each as of its week. It saves the fact sheet and the read of each trade, and it prints a summary with the 28 Leans, the cost, and the time. It checks every read against its sheet: the fact ids, the numbers and names, and the inner words. The test set and the output stay out of the repo, because they name league managers. Later tickets use the saved sheets as evidence.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] The command runs on the 28 trades and prints the summary with the cost and the time.
- [ ] Each trade has a Lean, a Case, and 3 to 5 Bullets per side, with no check failure after the retry.
- [ ] At least one Lean is Gut call.
- [ ] No read holds a number, a name, or a fact id that is not on its sheet, and no read holds "trade value" or "return bet".
- [ ] `git status` shows no test set file and no output file.
- [ ] `make check-fast` passes.
