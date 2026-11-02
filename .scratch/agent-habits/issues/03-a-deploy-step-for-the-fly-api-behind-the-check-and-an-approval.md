# 03: A deploy step for the Fly API behind the check and an approval

Spec: `.scratch/agent-habits/PRD.md`, part 3. One 0014: a human decides, and a check gates.

**What to build:** A GitHub Actions job `deploy` runs `fly deploy` from `main` after the `check` job passes and
Brian approves it in a GitHub environment named `fly`. A new ADR records why a deploy is gated and approved, and
why it never runs on a push alone. `make deploy` stays for a deploy from the shell.

**Blocked by:** `rules-as-checks` pipeline ticket 01, which adds the `check` job this one needs.

**Status:** ready-for-agent

- [ ] The ADR. Next free number after the `rules-as-checks` ADRs. Title: "A deploy of the API runs after the check
  and on an approval". It says: the check gates, Brian approves, the deploy runs from `main` only, and the shell
  path stays as the fallback.
- [ ] Decision for Brian before the build: approve each deploy by hand, or deploy on every green `main` push.
  The ADR records the answer. The default here is approve by hand, because a deploy changes what the site serves.
- [ ] The job `deploy` in `.github/workflows/check.yml` needs `check`, runs on `main` only, and has
  `environment: fly`. The environment has Brian as its required reviewer.
- [ ] The job runs `flyctl deploy --remote-only` with the `superfly/flyctl-actions/setup-flyctl` step. The secret
  `FLY_API_TOKEN` is a repo secret. The ADR says the token is a deploy token, not a personal one.
- [ ] `fly.toml` is unchanged. The Dockerfile is unchanged.
- [ ] `docs/runbook-site-api.md` gains three lines: how to approve, how to
  read the job, and when to use `make deploy` instead.
- [ ] Brian watches the first deploy through the job. The close comment names the run, the image, and the
  `/health` answer after it.
- [ ] `make check` passes.
