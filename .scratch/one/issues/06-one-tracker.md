# 06: One tracker

Spec: `.scratch/one/PRD.md`. Implementation Decisions "The tracker" and "The new feature shape".

**What to build:** One root `.scratch/` and one `state.md` hold every feature of both apps. The tracker rules keep the file true.

**Blocked by:** 04.

**Status:** done

- [x] The nine shared features keep `site/` and `pipeline/` subfolders, each with its own PRD and `issues/`. No ticket is renumbered.
- [x] Every other old feature moves as it is.
- [x] One `docs/agents/state.md` has an `App` column with the value site, pipeline, or both. It holds every open row of both old files.
- [x] The tracker rules of both apps read the root `.scratch/` and the root `state.md`, and the root `make check` runs them.
- [x] One `docs/agents/issue-tracker.md` describes the old shape and the new shape: map, decision tickets, spec, acceptance file, tickets.
- [x] The pipeline Makefile comment that calls `.scratch` untracked is true or gone.

## Comments

- The merge: `one-06-tracker` merged as `14300db` on 2026-11-03, with commits `7fde21d`, `256bbb5`, and `c60ce1f`.
- The proof: the root `make check` passed, with 566 site tests and 1541 pipeline tests. `git ls-files apps/pipeline/.scratch apps/pipeline/docs/agents` prints 0. The new `state.md` holds all 23 open rows of the two old files.
- The notes: the 9 shared features have `site/` and `pipeline/` subfolders. The two tracker rules disagree on two edge cases of a Status line: a plain `Status: done` line, and an empty bold line. No ticket hits either case today. The close removed the hold about the prek hook, because the hook runs on every commit.
- Read 11 files: CLAUDE.md, apps/site/CLAUDE.md, apps/pipeline/CLAUDE.md, .scratch/one/PRD.md, .scratch/one/issues/06-one-tracker.md, docs/agents/issue-tracker.md, docs/agents/state.md, docs/adr/0021-the-tracker-is-local-markdown.md, apps/site/src/tracker-rule.test.ts, apps/pipeline/tests/test_rule_tracker.py, apps/pipeline/Makefile.
