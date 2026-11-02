# 01: One check command, a prek hook, and CI on every push

Spec: `.scratch/rules-as-checks/PRD.md`, part 1 and "Decisions". One 0013.

**What to build:** `pnpm check` runs typecheck, test, build, and `check:export`. `pnpm check:fast` runs
typecheck and test. A prek hook runs `pnpm check:fast` on each commit. A CI job runs `pnpm check` on every
push. ADR 0006 records the rule.

**Blocked by:** None (can start immediately).

**Status:** done

- [ ] `package.json` scripts: `"check": "pnpm typecheck && pnpm test && pnpm build && pnpm check:export"` and `"check:fast": "pnpm typecheck && pnpm test"`.
- [ ] `Makefile`: the `check` target runs `pnpm check`. Its four lines go, so the list of steps lives in one place.
- [ ] `.pre-commit-config.yaml` at the root holds one `repo: local` hook: id `check-fast`, `entry: pnpm check:fast`, `language: system`, `pass_filenames: false`, `always_run: true`.
- [ ] Choice: the hook runs on the whole tree. The subset takes about 17 seconds, under the 30-second target of One 0013.
- [ ] Choice: the hook does not run `pnpm install`. In a worktree with no `node_modules`, it fails, and the fix is `pnpm install`.
- [ ] `README.md` gains one setup line: `prek install`, one time per clone. Each worktree then reads its own branch's config.
- [ ] `.github/workflows/check.yml`: `on: push` with no branch filter, and `workflow_dispatch`. One job `check`. The steps copy the setup of `deploy.yml`, then run `pnpm install --frozen-lockfile` and `pnpm check`.
- [ ] `deploy.yml`: its four steps `pnpm typecheck`, `pnpm test`, `pnpm build`, and `pnpm check:export` become one step, `pnpm check`.
- [ ] Choice: `deploy.yml` keeps its own check. A separate workflow cannot gate the deploy without `workflow_run`, and a deploy must never ship an unchecked build. A push to `main` thus runs the check twice.
- [ ] `docs/adr/0006-the-rules-are-checks.md` states: one command, the same rules in the hook and in CI, the hook runs a subset under 30 seconds, CI runs all. Later tickets add a section each.
- [ ] `pnpm check` passes. `time pnpm check:fast` shows under 30 seconds.
- [ ] Proof of the hook: in the worktree, stage a `.ts` file with a type error and run `git commit`. The hook refuses it. Remove the file.
- [ ] Proof of the publish path: `cornerstone publish` commits this repo from Brian's shell, so the hook runs there too. The launchd job only builds and never commits. After the hook install, run one `make publish` by hand with the hook in place before the week 9 publish.
- [ ] If the hook fails under that PATH, stop and return `STUCK:`. A failed hook stops the Tuesday publish.
- [ ] Ask Brian before the first push of the branch. The Check run on that push is green.

## Comments

- 2026-11-02: merged into `main` from branch `rules-as-checks-01-check`, commits c73e594, b781cf7, and df14a66, with `--no-ff`. Two reviewers passed it in the earlier session. The hook is not installed yet: `pnpm hook:install` runs in the main checkout after the week 8 page is live, so the first hooked publish is watched. The first push runs the Check job for the first time. Built before the files-read habit, so no file list.
