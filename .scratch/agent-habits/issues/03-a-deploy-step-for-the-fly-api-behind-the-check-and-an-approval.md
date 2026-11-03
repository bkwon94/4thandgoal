# 03: A deploy step for the Fly API on every green main push

Spec: `.scratch/agent-habits/PRD.md`, part 3. One 0014: a human decides, and a check gates.

**What to build:** A GitHub Actions job `deploy` runs `flyctl deploy` from `main` after the `check` job passes.
No human approves it, and no environment gate holds it. A green check is the approval. A new ADR records why
the check gates the deploy and why no human approves it. `make deploy` stays for a deploy from the shell.

**Blocked by:** none. `rules-as-checks` 01 is merged, so the `check` job exists.

**Status:** ready-for-agent

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
- [ ] Brian watches the first deploy through the job. The close comment names the run, the image, and the
  `/health` answer after it.
- [x] `make check` passes.
