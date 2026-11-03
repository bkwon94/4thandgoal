# 03: Add the pipeline into apps/pipeline with its history

Spec: `.scratch/one/PRD.md`. Solution part 1, and Implementation Decisions "The order of the move", "The weekly job", "publish", and "Deploy paths".

**What to build:** The pipeline lives in `apps/pipeline/` with its full history. The weekly build, `publish`, the Fly API, and the daily refresh all run from the merged repo.

**Blocked by:** 02.

**Status:** ready-for-agent

- [x] `git subtree add` brings in the pipeline, and `git log` on a pipeline file shows its old commits.
- [x] `make check` passes inside `apps/pipeline/`.
- [x] `publish` copies into the site's published data in the same repo. It no longer takes a second checkout.
- [x] `make publish` for week 8 with no push changes no files.
- [ ] The LaunchAgent and `cornerstone-build` use the merged path. The LaunchAgent is unloaded and loaded again.
- [ ] One hand run of `cornerstone-build` from the merged repo, with no push, ends with no error.
- [ ] The Fly config and the Dockerfile build from `apps/pipeline/`. One deploy works, and api.cpcfantasy.com answers.
- [ ] The daily refresh workflow runs from the root workflows. One manual dispatch passes.
- [x] The site Makefile targets that need the local API point at the pipeline folder.
