# 02: evidence-flags gives a flag for a fact that no file shows

Spec: `.scratch/evidence-flags/PRD.md`. Acceptance tests AT-3, AT-5, AT-6, AT-10, AT-11, and AT-12.

**App:** pipeline.

**What to build:** `cornerstone evidence-flags <slug> [AT-<n> ...] [--root <path>]` reads each acceptance test, its entry in `EVIDENCE.md`, and its files, and makes one Jev request per test. The questions module holds question (a), the facts, with its cut. Each yes past the cut is an entry in `FLAGS.md` with `Action: open`, and the command prints it. The state holds each text file in full and every shot, scaled and cut into tiles of 1568 px or less. The run logs one line of counts. A `JevError` or a missing key gives no flag and exit 0.

**Blocked by:** 01.

**Status:** ready-for-agent

- [x] On easter-eggs AT-3 at `8d646bd0`, in a temp root, the live run writes an (a) entry at 0.7 or more (AT-3).
- [x] On all of hero-slots at `f9304b5e`, the run exits 0 with one log line, and its counts match `EVIDENCE.md` and `FLAGS.md` (AT-5).
- [x] With `TYPESAFE_API_KEY` unset, the run exits 0, writes no entry, and logs one error per test (AT-6).
- [x] A CLI test with `FakeJev` and the real shots of easter-eggs AT-32 shows a tile of every shot, each 280 to 1568 px per side (AT-10).
- [x] A CLI test with a state over 32 MiB shows the shots that fit, in the order of `Files:`, and the log ends with `, 1 cut` (AT-11).
- [x] A CLI test shows no request for a test at `Files: none` (AT-12).
- [x] The command prints the question keys that it asked for each test.
