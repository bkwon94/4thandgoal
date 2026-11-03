# 04: One root check, one hook, and one CI file

Spec: `.scratch/one/PRD.md`. Solution part 2, and Implementation Decisions "The root check".

**What to build:** One command at the root runs every rule in both apps. The hook and CI run that same command.

**Blocked by:** 03.

**Status:** ready-for-agent

- [ ] The root `make check` runs the site check, then the pipeline check, and it fails on the first failure.
- [ ] The root `make check-fast` does the same with the fast checks.
- [ ] A diff option takes a base branch and runs only the apps with changed files. A change at the root runs both apps.
- [ ] One prek hook at the root runs `make check-fast`. It is installed in the main checkout. The per-app hooks are gone.
- [ ] One CI file runs `make check` on each push and each PR. The old check workflows are gone.
- [ ] A commit with a broken rule in each app fails the hook. Prove each case once.
