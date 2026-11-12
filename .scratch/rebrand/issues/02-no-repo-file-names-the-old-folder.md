# 02: No repo file names the old folder

Spec: `.scratch/rebrand/PRD.md`. Acceptance tests AT-5, AT-7, AT-8, AT-9, AT-10, AT-13, AT-14, AT-15, and AT-16.

**App:** both

**What to build:** no tracked file outside the records names `cpcfantasyfootball`, so the folder can move to `~/repos/4thandgoal`. The site package is `4thandgoal-site`, in its manifest, in the lock file, and in the test of the changed apps. The weekly build script finds the pipeline folder from its own path, so it runs from the old folder, the new folder, or a worktree. The LaunchAgent in the repo names `/Users/brian.kwon/repos/4thandgoal`. No page, package, client, API code, domain, Fly app, ADR, or old record changes. Leave `CLAUDE.md` to ticket 01.

**Blocked by:** none

**Status:** done

- [x] The `git grep` of AT-5 prints nothing, and the lock file holds no `cpcfantasyfootball`.
- [x] The site package name is `4thandgoal-site`, and `pnpm check:fast` passes in `apps/site`.
- [x] From a worktree, the `REPO_DIR` lines of the weekly build script print the `apps/pipeline` path of that worktree, and the script names no `repos/` path.
- [x] `plutil -lint` passes on the LaunchAgent, and each of its repo paths starts with `/Users/brian.kwon/repos/4thandgoal/`.
- [ ] The guard commands of AT-13 to AT-16 show no change to pages, packages, clients, API code, the domain, the Fly app, the ADRs, or other features under `.scratch/`.
- [ ] `make check-fast` passes in `scripts/`, `apps/pipeline/`, and `apps/api/`.

## Comments

Merged into the Spec branch `rebrand` as 6c4d31be, on 2026-11-11. Closes with the squash merge of the spec PR.
AT-5, AT-7, AT-8, AT-9, AT-10, and AT-13 to AT-16 have PASS from the Judge; the full check passed at 34477b17.
Read 8 files: CLAUDE.md, .scratch/rebrand/PRD.md, .scratch/rebrand/ACCEPTANCE.md, .scratch/rebrand/issues/02-no-repo-file-names-the-old-folder.md, apps/pipeline/CLAUDE.md, apps/pipeline/bin/cornerstone-build, apps/site/package.json, scripts/test_changed_apps.py.
