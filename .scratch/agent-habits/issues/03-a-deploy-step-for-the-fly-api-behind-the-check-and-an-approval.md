# 03: A deploy step for the Fly API behind the check and an approval

Spec: `.scratch/agent-habits/PRD.md`, part 3. One 0014: a human decides, and a check gates.

**What to build:** A GitHub Actions job `deploy` runs `fly deploy` from `main` after the `check` job passes and
Brian approves it in a GitHub environment named `fly`. A new ADR records why a deploy is gated and approved, and
why it never runs on a push alone. `make deploy` stays for a deploy from the shell.

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
- Before the first run: the repo has no secret `FLY_API_TOKEN` on 2026-11-03. `gh secret list` shows only
  `CORNERSTONE_PASSPHRASE`. Brian creates a deploy token with `fly tokens create deploy -x 999999h`. Then he sets
  it with `gh secret set FLY_API_TOKEN`. Without it, the first deploy job fails at the deploy step.
- [ ] Brian watches the first deploy through the job. The close comment names the run, the image, and the
  `/health` answer after it.
- [x] `make check` passes.
