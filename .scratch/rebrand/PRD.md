# Rebrand: the folder becomes 4thandgoal and the plugin becomes 4ag

Status: ready-for-agent
Date: 2026-11-11
Apps: both. The site changes only its package name. The pipeline changes its weekly build script and its LaunchAgent. The root changes the plugin, the docs, and the scripts. No page and no build output changes.
Spec branch: `rebrand`.
Source: the map `.scratch/rebrand/MAP.md` and decision tickets 01 to 07, from the session of 2026-11-11. ADRs 0018 and 0019.
Tickets: none yet. `cpc:to-tickets` writes them.

## Problem Statement

The product has three names. Managers see 4th & Goal at `4thandgoal.app`. The GitHub repo is `bkwon94/4thandgoal`. The local folder is `~/repos/cpcfantasyfootball`, and the plugin is `cpc`.

Brian types the plugin name in each skill call, such as `cpc:plan`. `cpc` is also the slug of the first client, so one word names two things. The local folder name does not match the repo name on GitHub.

A new Product name for a fantasy AI expert is the long-term goal. It costs a new domain, 35 files, and 7 manual steps in Cloudflare and Fly. That cost buys nothing for the managers of our two leagues today, so this spec does only the local part.

## Solution

The local folder becomes `~/repos/4thandgoal`, so it matches the GitHub repo. The plugin becomes `4ag`, so the skills are `4ag:plan`, `4ag:implement`, and so on. The domain, the Fly app, the Workers, and every page stay as they are.

After the merge, Brian moves the folder by a runbook with exact commands. After the move, the memory, the worktrees, the venv, the weekly LaunchAgent, and the plugin all work from the new folder.

## User Stories

1. As Brian, I want the local folder named `4thandgoal`, so that it matches the GitHub repo `bkwon94/4thandgoal`.
2. As Brian, I want the plugin named `4ag`, so that a skill call never reads like the client `cpc`.
3. As Brian, I want each skill call to start with `4ag:`, such as `4ag:plan` and `4ag:implement`, so that I type one short prefix.
4. As Brian, I want the marketplace named `4ag-local`, so that the plugin and its marketplace share a name.
5. As Brian, I want the root `CLAUDE.md` to list the skills as `4ag:`, so that an agent new to the repo calls the right name.
6. As Brian, I want the docs under `docs/agents/` to name the skills as `4ag:`, so that no doc names a plugin that does not exist.
7. As Brian, I want each skill file of the plugin to call the other skills by `4ag:`, so that one skill hands off to the next one by a name that loads.
8. As Brian, I want the subagent prompts of `4ag:implement` to name the repo as `4thandgoal`, so that a subagent knows the repo by its one name.
9. As Brian, I want the `verdict` check to keep the marker `<!-- cpc:agent -->`, so that it still finds the agent comments on an open PR.
10. As Brian, I want the message of the `verdict` check to say `4ag:review`, so that it names the skill that fixes a FAIL.
11. As Brian, I want the site package named `4thandgoal-site`, so that no package holds the old folder name.
12. As Brian, I want the weekly build script to find the repo from its own place on disk, so that a folder move does not break it.
13. As Brian, I want the LaunchAgent in the repo to name the new folder, so that I copy a file that is right after the move.
14. As Brian, I want one runbook with each step of the folder move, so that I run them in order with no guess.
15. As Brian, I want each step of the runbook to have one check command, so that I know the step worked before the next one.
16. As Brian, I want the runbook to remove the worktrees of merged specs first, so that `git worktree repair` has less to fix.
17. As Brian, I want the runbook to move the Claude memory folder, so that each memory of this repo stays with it.
18. As Brian, I want the runbook to fix the marketplace path in `~/.claude/settings.json`, so that the plugin loads from the new folder.
19. As Brian, I want the runbook to rebuild the venv and the node modules, so that `uv run` and `pnpm` work from the new folder.
20. As Brian, I want the runbook to stop the weekly LaunchAgent before the move and load it after, so that no weekly build runs from a folder that is gone.
21. As Brian, I want the runbook to say "do not move on a weekly build day", so that the Tuesday build is safe.
22. As a manager, I want each page and each address to stay the same, so that my saved links and my league site still work.
23. As a manager, I want the trade analyzer and the API to stay the same, so that nothing I use goes down.
24. As an agent, I want a plain list of the old names that stay on purpose, so that I do not rename a package, an ADR, or old evidence by mistake.
25. As the Judge, I want each acceptance test to have evidence from a command, so that I give a Test verdict from facts.

## Implementation Decisions

- **The scope.** The rename covers the local folder, the plugin, the marketplace, the site package name, the docs that name the plugin or the folder, the weekly build script, and the LaunchAgent. Decision 02 keeps the domain `4thandgoal.app`. Decision 07 keeps the Fly app `cpcfantasy-api`.
- **The plugin name.** The plugin is `4ag` and the marketplace is `4ag-local` (decision 05). `claude plugin validate` passed a test plugin named `4ag` on 2026-11-11. The project settings enable `4ag@4ag-local`. The marketplace source stays a relative path to the repo root, so the project settings need no folder path.
- **The skill text.** Each skill of the plugin keeps its folder name and its steps. Only the prefix `cpc:` becomes `4ag:`, and the repo name `cpcfantasyfootball` becomes `4thandgoal`. The client slug `cpc` stays wherever it names the client.
- **The verdict marker.** The marker `<!-- cpc:agent -->` stays, and the fixtures of the `verdict` check stay. The marker is a machine key in old PR comments, not a skill name. Only the human message that names the skill changes to `4ag:review`.
- **The weekly build script.** The script finds the pipeline folder from its own path, one level up from its `bin/` folder, and does not name `~/repos/<folder>`. So the merge and the folder move can happen at different times, and the build still runs.
- **The LaunchAgent.** The plist in the repo names `/Users/brian.kwon/repos/4thandgoal`. The loaded copy in `~/Library/LaunchAgents/` keeps the old path until the runbook copies the new file. A launchd plist needs an absolute path, so it cannot find the repo on its own.
- **The site package name.** `cpcfantasyfootball-site` becomes `4thandgoal-site` in the site package, in the test of the changed apps, and in the lock file. The `@cpc/*` npm names and the `cpc-*` Python names stay.
- **The runbook.** One new doc in `docs/agents/` holds the folder move, in the order of the research notes `decisions/03-research-the-cutover.notes.md`, Part 3, step 8. The steps are: stop the LaunchAgent, remove the worktrees of merged specs, move the folder, run `git worktree repair`, move the Claude memory folder, fix the marketplace key and path in `~/.claude/settings.json`, rebuild the venv and the node modules, copy and load the LaunchAgent, then open a new session and call one `4ag:` skill. Each step has one check command. The remote URL already names `4thandgoal`, so it needs no change.
- **The order.** The spec PR merges to `main` by the flow. Brian runs the runbook after the merge, in one sitting. Until Brian fixes `~/.claude/settings.json`, the user settings still name `cpc-local`, so the plugin may load twice or not at all. The runbook fixes it in the same sitting.
- **The build waits.** `cpc:implement rebrand` starts after `front-door` merges to `main`. The plugin rename and the folder move break the open worktrees of front door.
- **The records.** The ADRs and the text under `.scratch/` keep the old names. They record what happened. ADR 0018 keeps "the home is `bkwon94/cpcfantasyfootball`".
- **The terms.** The **Product name** stays 4th & Goal. **Brand** keeps its meaning, the identity of one client. `GLOSSARY.md` holds both terms.

## Testing Decisions

A good test checks what Brian or an agent sees: a name in a file, a plugin that loads, a check that passes. It does not check how a file got its text.

The seams, from the highest down:

1. **The old-name sweep.** One `git grep` for `cpcfantasyfootball` and for the skill prefix `cpc:` outside `.scratch/`, `docs/adr/`, the lock files, and the verdict marker lines. The evidence is the command and its output. An empty output passes. This is the one seam for most of the stories.
2. **The plugin validator.** `claude plugin validate .claude/plugin` passes, and the manifest name is `4ag`. The marketplace validates too.
3. **The repo checks.** `make check-fast` of the scripts, the site, the pipeline, and the API passes. The scripts tests cover the `verdict` check with the old marker fixtures and the test of the changed apps with the new site package name. Prior art: `scripts/test_changed_apps.py` and the `verdict` tests under `scripts/`.
4. **The build script.** A run of the path logic of the weekly build script from a worktree prints the pipeline folder of that worktree, not of the main checkout. The evidence runs only the path lines, not a full build.
5. **The runbook, after the merge.** Brian runs it. The evidence of the merge PR cannot hold this, because the move happens after the merge. The runbook checks are: `git worktree list` shows `/Users/brian.kwon/repos/4thandgoal` with no `prunable`, `launchctl list` shows the weekly job, `/plugin` lists `4ag@4ag-local` as enabled, and a `4ag:` skill loads in a new session.

The fifth seam is a manual check by Brian after the merge. The acceptance tests mark it so.

## Out of Scope

- A new Product name and a new domain. Choose them when front door serves a league that we do not know. The candidates are in `decisions/01-research-name-candidates.notes.md`.
- A new Fly app. Fly has no rename, and a move risks the eggs SQLite and the API certificate.
- A product brand on the page, and a landing page at the bare domain.
- A rename of `cornerstone`, `cornerstone_api`, the `@cpc/*` npm names, and the `cpc-*` Python names.
- A rename of the client `cpc`, its folder, its Worker, or its secrets.
- A rewrite of the ADRs or of the text under `.scratch/`.
- A change to the verdict marker `<!-- cpc:agent -->`.
- A rewrite of the memory files of Claude. They move with their folder and keep their text.

## Further Notes

- The research notes of decision 03 list 45 worktrees on 2026-11-11. Most belong to merged specs. The runbook removes them before the move, so few remain to repair.
- The untracked files in the main checkout, such as `.codex/` and `AGENTS.md`, move with the folder.
- The memory of Claude for a worktree lives in its own project folder under `~/.claude/projects/`. Those folders do not move. Only the folder of the main checkout carries the memory.
- Give Brian each manual step of the runbook at the time he runs it, with the exact value and the check.
