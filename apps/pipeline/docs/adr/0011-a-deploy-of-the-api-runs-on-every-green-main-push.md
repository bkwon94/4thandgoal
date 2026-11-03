# A deploy of the API runs on every green main push

The API on Fly deployed by hand from a shell. No check gated it, and no record said when it ran. Now the
job `deploy` in `.github/workflows/check.yml` deploys the API after each push to `main` with a green check.

## The decision

- The check gates the deploy. The job `deploy` needs the job `check`, so a red check stops it.
- No human approves the deploy. The job has no environment gate. A green check is the approval.
- The deploy runs from `main` only. The job runs only on a push event to `refs/heads/main`. A push to a
  branch or a run by hand runs the check and no deploy.
- Two deploys never overlap. The job holds the concurrency group `fly-deploy`, so a second deploy waits.
- The job runs `flyctl deploy --remote-only`. A Fly builder builds the image, so the runner needs no Docker.
- `make deploy` stays as the fallback from the shell. It still checks for `main` and a clean tree.

## The token

The job reads `FLY_API_TOKEN` from a repo secret. The token is a Fly deploy token for the app
`cpcfantasy-api`, not a personal token. A deploy token can change only that app, so a leak cannot touch
the rest of the Fly account. The token is never in the tree.

## Why no approval gate

The PRD of `agent-habits` first asked for an approval by Brian in a GitHub environment. On 2026-11-03 Brian
chose a deploy on every green `main` push: "Deploy on green is fine". Two facts support the choice:

1. The check is the review. The check runs on each push to `main`, and `make check` runs on it.
2. A deploy changes only the API. The site calls the API, but a deploy never publishes a page. The publish
   rule holds: only `cornerstone publish` pushes the site.

A bad deploy is cheap to fix. Revert the commit on `main`, and the next green push deploys the fix.
