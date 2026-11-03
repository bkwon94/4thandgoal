# 03: A deploy step for the Fly API on every green main push

Spec: `.scratch/agent-habits/PRD.md`, part 3. One 0014: a check gates. Brian chose no human gate on 2026-11-03.

**What to build:** A GitHub Actions job `deploy` runs `flyctl deploy` from `main` after the `check` job passes.
No human approves it, and no environment gate holds it. A green check is the approval. A new ADR records why
the check gates the deploy and why no human approves it. `make deploy` stays for a deploy from the shell.

**Blocked by:** none. `rules-as-checks` 01 is merged, so the `check` job exists.

**Status:** done

- [x] The ADR. Next free number after the `rules-as-checks` ADRs. Title: "A deploy of the API runs on every green main
  push". It says: the check gates, no human approves, the deploy runs from `main` only, and the shell
  path stays as the fallback.
- [x] Decision, 2026-11-03: deploy on every green `main` push. Brian: "Deploy on green is fine". The ADR records it.
- [x] The job `deploy` in `.github/workflows/check.yml` needs `check`, runs on `main` only, with no
  environment gate. A green `check` is the approval.
- [x] The job runs `flyctl deploy --remote-only` with the `superfly/flyctl-actions/setup-flyctl` step. The secret
  `FLY_API_TOKEN` is a repo secret. The ADR says the token is a deploy token, not a personal one.
- [x] `fly.toml` is unchanged. The Dockerfile is unchanged.
- [x] `docs/runbook-site-api.md` gains three lines: when the job deploys, how to
  read the job, and when to use `make deploy` instead.
- The repo secret `FLY_API_TOKEN` is a Fly deploy token Brian set on 2026-11-03.
- [x] Brian watches the first deploy through the job. The close comment names the run, the image, and the
  `/health` answer after it.
- [x] `make check` passes.

## Comments

- 2026-11-03: merged into `main` from branch `agent-habits-03-deploy`, commits daa494f, 7f0b5ee, 2dab205, and b1d78a7, with `--no-ff`. 1527 passed, 9 deselected. The `deploy` job in `check.yml` needs `check`, runs only on a push to `main`, pins `setup-flyctl@v1`, holds one concurrency group, and reads the token from the repo secret `FLY_API_TOKEN` that Brian set the same day. ADR 0017 records the decision: deploy on every green `main` push, no approval gate. The runbook says when the job deploys and when to use `make deploy`. The first deploy through the job runs on the next push; the orchestrator watches it and writes the run, the image, and the `/health` answer here. Two reviewers passed it after one fix pass. Read 13 files: CLAUDE.md, docs/agents/state.md, the ticket, .scratch/agent-habits/PRD.md, .github/workflows/check.yml, .github/workflows/refresh.yml, fly.toml, Dockerfile, Makefile, docs/runbook-site-api.md, docs/adr/0015-a-port-has-one-fake.md, the docs/adr listing, gh secret list.
- 2026-11-03 17:25 ET: the first deploy ran through the job on push 509497b, run 41682401769. The first try failed in 20 seconds with "no access token available", because the secret was set empty at the prompt. Brian set it again with `--body`, and the rerun deployed Fly release v20, image `cpcfantasy-api:deployment-01M6H72NJ690G38KQ4HAB19QD1`, machine started, `/health` 200.
