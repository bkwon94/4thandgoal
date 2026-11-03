# 04: One root check, one hook, and one CI file

Spec: `.scratch/one/PRD.md`. Solution part 2, and Implementation Decisions "The root check".

**What to build:** One command at the root runs every rule in both apps. The hook and CI run that same command.

**Blocked by:** 03.

**Status:** done

- [x] The root `make check` runs the site check, then the pipeline check, and it fails on the first failure.
- [x] The root `make check-fast` does the same with the fast checks.
- [x] A diff option takes a base branch and runs only the apps with changed files. A change at the root runs both apps.
- [x] One prek hook at the root runs `make check-fast`. It is installed in the main checkout. The per-app hooks are gone.
- [x] One CI file runs `make check` on each push and each PR. The old check workflows are gone.
- [x] A commit with a broken rule in each app fails the hook. Prove each case once.

## Comments

- The merge: `one-04-root-check` merged as `bf40f2b` on 2026-11-03, with commits `266e557` and `a077705`.
- The proof: the root `make check` passed in 6 min 32 s, and `make check-fast` passed in about 20 s. The four diff cases ran the right apps. A broken rule in each app failed the hook. The first Check run and the first Deploy API run passed, and `api.cpcfantasy.com/health` answers 200. This close commit ran the root hook in the main checkout.
- The notes: a push that changes `apps/pipeline/` runs the check twice, once in Check and once inside Deploy API. The pipeline tests take most of the 6.5 minutes.
- Read 8 files: CLAUDE.md, .scratch/one/PRD.md, .scratch/one/issues/04-one-root-check-hook-and-ci.md, docs/agents/issue-tracker.md, .pre-commit-config.yaml, apps/site/package.json, apps/site/Makefile, apps/pipeline/Makefile.
