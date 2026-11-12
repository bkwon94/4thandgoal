# Codex

This runbook sets up Codex to run the 4ag flow in this repo.
Brian does each step by hand, once. Each step gives the reason, the exact values, and a check.

Do the steps in order. Run the check of each step before the next one. If a check fails, stop.

## 1. Trust the project in Codex

Why: Codex loads the project `.codex/config.toml` only for a trusted project. Without it, the profile `4ag` does not apply.

Brian did this on 2026-11-12. `~/.codex/config.toml` holds these lines:

```
[projects."/Users/brian.kwon/repos/4thandgoal"]
trust_level = "trusted"
```

Check: run `codex doctor` at the root of the main checkout. It shows `restricted fs + enabled network · approval Never`.

## 2. Start Codex at the main checkout root

Why: Codex in a linked worktree cannot write its own gitdir, so it cannot commit. The other worktrees also sit outside its workspace.

**Warning: never start Codex in a worktree.** A session there cannot commit, and `4ag:implement` stops mid-build.

```
cd /Users/brian.kwon/repos/4thandgoal && codex
```

Check: run `pwd` before you start Codex. It prints `/Users/brian.kwon/repos/4thandgoal`.

## 3. Copy the config before the merge of this spec

Why: the main checkout on `main` does not have `.codex/config.toml` or `.agents/skills/` until a spec that adds them merges. Codex reads the config of the folder where it starts.

Do this only before that merge. Run it at the main checkout root. Replace `<branch>` with the spec branch, such as `codex-flow`.

```
mkdir -p .codex .agents/skills
git show <branch>:.codex/config.toml > .codex/config.toml
for s in plan to-spec to-acceptance to-tickets implement review; do ln -s ../../.claude/plugin/skills/$s .agents/skills/4ag-$s; done
```

Check: `codex debug prompt-input "hi" | grep -c '^- 4ag:'` prints 6.

Remove the copies when the spec merges. Step 6 does this.

## 4. Add the skill `research`

Why: `4ag:plan` loads `research` by its Codex name. Its Claude name is `mattpocock-skills:research`. The skill must sit in `~/.agents/skills/`.

The source is in the cache of the `mattpocock-skills` plugin. The path holds a version number. Change `1.3.1` if the plugin updates.

```
mkdir -p ~/.agents/skills && ln -s ~/.claude/plugins/cache/claude-plugins-official/mattpocock-skills/1.3.1/skills/engineering/research ~/.agents/skills/research
```

Check: `codex debug prompt-input "hi" | grep -c '^- research:'` prints 1.

## 5. Add the GitHub ruleset on `main`

Why: the ruleset is the wall on `main` for every agent, in Claude and in Codex. It needs the check `verdict`. The Repository admin role on the bypass list lets the weekly `publish` still push.

In the repo `bkwon94/4thandgoal`, open Settings, Rules, Rulesets, New branch ruleset. Set these values:

- Ruleset name: `main`
- Enforcement status: Active
- Target branches: Add target, Include default branch
- Rule: Require status checks to pass, with the check `verdict`
- Bypass list: Repository admin, with the mode Always

Click Create.

Check 1: this command lists the ruleset with the enforcement `active`.

```
gh api repos/bkwon94/4thandgoal/rulesets --jq '.[] | [.name,.enforcement] | @tsv'
```

Expected output: `main	active`

Check 2: replace `<id>` with the id of the ruleset. Get the id from `gh api repos/bkwon94/4thandgoal/rulesets --jq '.[].id'`.

```
gh api repos/bkwon94/4thandgoal/rulesets/<id> --jq '.rules, .bypass_actors, .conditions'
```

The output names `verdict` in the rule `required_status_checks`. It shows the admin role, `actor_id` 5, with `bypass_mode` `always`. It shows `~DEFAULT_BRANCH` in `conditions.ref_name.include`.

## 6. Remove the stale files after the merge

Why: the merge brings tracked files at `AGENTS.md`, `apps/site/AGENTS.md`, and `.codex/config.toml`. The untracked files at those paths make `git pull` fail. The untracked `.agents/skills/` symlinks from step 3 also go.

Do this at the main checkout root, after the spec merges and before `git pull`.

**Warning: run this only after the merge, and only in the main checkout.** The commands delete untracked files. Before the merge, they remove the files that step 3 makes.

```
rm AGENTS.md apps/site/AGENTS.md .codex/config.toml
find .agents/skills -type l -exec rm {} + 2>/dev/null
```

Check: `git status --short` shows none of these files. Then run `git pull`. It succeeds.
