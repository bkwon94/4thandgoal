# 03: Add the pipeline into apps/pipeline with its history

Spec: `.scratch/one/PRD.md`. Solution part 1, and Implementation Decisions "The order of the move", "The weekly job", "publish", and "Deploy paths".

**What to build:** The pipeline lives in `apps/pipeline/` with its full history. The weekly build, `publish`, the Fly API, and the daily refresh all run from the merged repo.

**Blocked by:** 02.

**Status:** done

- [x] `git subtree add` brings in the pipeline, and `git log` on a pipeline file shows its old commits.
- [x] `make check` passes inside `apps/pipeline/`.
- [x] `publish` copies into the site's published data in the same repo. It no longer takes a second checkout.
- [x] `make publish` for week 8 with no push changes no files.
- [x] The LaunchAgent and `cornerstone-build` use the merged path. The LaunchAgent is unloaded and loaded again.
- [x] One hand run of `cornerstone-build` from the merged repo, with no push, ends with no error.
- [x] The Fly config and the Dockerfile build from `apps/pipeline/`. One deploy works, and api.cpcfantasy.com answers.
- [x] The daily refresh workflow runs from the root workflows. One manual dispatch passes.
- [x] The site Makefile targets that need the local API point at the pipeline folder.

## Comments

- The merge: `one-03-pipeline` merged as `2722c2d` on 2026-11-03, after the subtree add `439568b` and nine more commits. The untracked pipeline tickets came in as `190c50a`.
- The proof: `make check` passed with 1540 tests. The Pipeline check run passed its check and deploy jobs, and `api.cpcfantasy.com/health` answers 200. The Daily refresh run passed. `run_publish` for week 8 with no push made no change. A `launchctl kickstart` of the weekly job ended with "end (exit 0)" at 14:01.
- The notes: `git log` on a pipeline file shows only the subtree add. Use `git log --full-history` or `git blame` for the old commits. The old repo still has its own Fly deploy job, and ticket 10 stops it. The hand run rebuilt week 8, and its 19 changed files were restored. The Docker build was not proved locally, and the Fly remote builder proved it instead.
- Read 14 files: CLAUDE.md, .scratch/one/PRD.md, .scratch/one/issues/02-move-the-site-into-apps-site.md, .scratch/one/issues/03-add-the-pipeline-into-apps-pipeline.md, docs/agents/issue-tracker.md, apps/pipeline/CLAUDE.md, apps/pipeline/Makefile, apps/pipeline/src/cornerstone/publish.py, apps/pipeline/bin/cornerstone-build, apps/pipeline/launchagents/com.briankwon.cornerstone-weekly.plist, apps/pipeline/fly.toml, apps/pipeline/Dockerfile, .github/workflows/pipeline-check.yml, .pre-commit-config.yaml.
