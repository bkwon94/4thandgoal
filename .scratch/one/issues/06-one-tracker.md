# 06: One tracker

Spec: `.scratch/one/PRD.md`. Implementation Decisions "The tracker" and "The new feature shape".

**What to build:** One root `.scratch/` and one `state.md` hold every feature of both apps. The tracker rules keep the file true.

**Blocked by:** 04.

**Status:** ready-for-agent

- [ ] The nine shared features keep `site/` and `pipeline/` subfolders, each with its own PRD and `issues/`. No ticket is renumbered.
- [ ] Every other old feature moves as it is.
- [ ] One `docs/agents/state.md` has an `App` column with the value site, pipeline, or both. It holds every open row of both old files.
- [ ] The tracker rules of both apps read the root `.scratch/` and the root `state.md`, and the root `make check` runs them.
- [ ] One `docs/agents/issue-tracker.md` describes the old shape and the new shape: map, decision tickets, spec, acceptance file, tickets.
- [ ] The pipeline Makefile comment that calls `.scratch` untracked is true or gone.
