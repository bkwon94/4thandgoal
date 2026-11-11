# 03: Where is each old name wired, and in what order does the cutover run?

Map: `.scratch/rebrand/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

List each place that holds `4thandgoal`, `cpcfantasyfootball`, `cpcfantasy.com`, or the plugin name `cpc`: the repo files, the GitHub Actions secrets and workflows, the Cloudflare Workers and their custom domains, the Fly app and its certificate, CORS, the Claude memory folder of the local path, and the open worktrees. Find from the Cloudflare, Fly, and GitHub docs how each rename behaves: a GitHub repo rename redirect, a Fly app rename or a new app, and a Worker custom domain move. Give one cutover order with no downtime for a manager. The notes go to `decisions/03-research-the-cutover.notes.md`.

## Decision

The notes are `decisions/03-research-the-cutover.notes.md`, checked 2026-11-11. The orchestrator checked three facts in the repo: the Fly app name, the `cpc:agent` marker, and the URL in `refresh.yml`.

- 54 files outside `.scratch/` hold an old name. Live code holds the domain in `publish.py`, `config.ts`, `eggs/keys.py`, and `refresh.yml`.
- `scripts/verdict.py` reads the marker `<!-- cpc:agent -->` in old PR comments. The spec keeps it or accepts both markers.
- The Workers `cpc` and `norcal` take client slugs, so they need no rename. A new Custom Domain sits beside the old one.
- Fly has no app rename. A new app needs a new volume and a copy of the eggs SQLite. Decision 07 decides it.
- The move of the local folder breaks the venv, the LaunchAgent `com.briankwon.cornerstone-weekly`, the plugin path in `~/.claude/settings.json`, the memory folder, and 45 worktrees. The notes give each fix step.
- The cutover order: zone, Custom Domains, API cert, code PR with the old CORS origins kept, a redirect of the old zone, `cpcfantasy.com`, the GitHub repo, then the folder move last.
