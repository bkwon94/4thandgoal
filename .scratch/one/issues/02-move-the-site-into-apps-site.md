# 02: Move the site into apps/site

Spec: `.scratch/one/PRD.md`. Solution part 1, and Implementation Decisions "The order of the move" and "Deploy paths".

**What to build:** The site lives in `apps/site/`, and it still builds and deploys from `main`. The root keeps only what the whole repo shares: `.scratch/`, `docs/`, the glossary, the CLAUDE.md, `.claude/`, and the workflows.

**Blocked by:** 01.

**Status:** done

- [x] The move is one commit of renames, so `git log --follow` shows one rename for each file.
- [x] `pnpm install`, `pnpm check`, `pnpm build`, and `pnpm check:export` pass inside `apps/site/`.
- [x] The Pages workflow builds from `apps/site/` and runs only on changes there and in the workflow itself.
- [x] The Pages deploy from `main` works, and the live site serves the week 8 page.
- [x] The pipeline's `publish` still works against the new path for one run, so a publish between 02 and 03 does not break.

## Comments

- The merge: `one-02-site-move` merged as `32aae08` on 2026-11-03, with commits `2a6723b`, `c11f0eb`, `2a87c5e`, and `5b0784a`. The paired pipeline change `one-02-publish-path` merged as `5b5e803`.
- The proof: `pnpm check` passed with 565 tests, and `build` and `check:export` passed. The Deploy run passed, and `/2026/week-08/` answers 200. `run_publish` for week 8 with no push wrote into `apps/site/public/` and made no commit.
- The notes: the move commit is 332 renames with 0 changed lines. The export lost 4 unused CSS rules, because Tailwind no longer scans `.scratch/` and `docs/`. `publish` still stages the whole tree with `add -A`. Ticket 07 narrows it.
- Read 9 files: CLAUDE.md, .scratch/one/PRD.md, .scratch/one/issues/02-move-the-site-into-apps-site.md, docs/agents/issue-tracker.md, docs/adr/0018-the-site-and-the-pipeline-live-in-one-repo.md, .github/workflows/deploy.yml, .github/workflows/check.yml, .pre-commit-config.yaml, src/tracker-rule.test.ts.
