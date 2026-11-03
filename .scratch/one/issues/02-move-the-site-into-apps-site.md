# 02: Move the site into apps/site

Spec: `.scratch/one/PRD.md`. Solution part 1, and Implementation Decisions "The order of the move" and "Deploy paths".

**What to build:** The site lives in `apps/site/`, and it still builds and deploys from `main`. The root keeps only what the whole repo shares: `.scratch/`, `docs/`, the glossary, the CLAUDE.md, `.claude/`, and the workflows.

**Blocked by:** 01.

**Status:** ready-for-agent

- [x] The move is one commit of renames, so `git log --follow` shows one rename for each file.
- [x] `pnpm install`, `pnpm check`, `pnpm build`, and `pnpm check:export` pass inside `apps/site/`.
- [x] The Pages workflow builds from `apps/site/` and runs only on changes there and in the workflow itself.
- [ ] The Pages deploy from `main` works, and the live site serves the week 8 page.
- [ ] The pipeline's `publish` still works against the new path for one run, so a publish between 02 and 03 does not break.
