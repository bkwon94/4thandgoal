# Folder move

This runbook moves the repo folder from `~/repos/cpcfantasyfootball` to `~/repos/4thandgoal`.
Brian runs it by hand, once, after the rebrand spec merges.

**Warning: move on a day other than Tuesday.** The weekly build runs Tuesday at 08:00. A move on that day breaks the build.

**Warning: close every Claude session in the repo first.** An open session keeps the old path. It then writes to a folder that no longer exists.

The GitHub repo is already `bkwon94/4thandgoal`, so the remote needs no change. Step 3 checks it.
The plugin is `4ag`, and its marketplace is `4ag-local`.

Do the steps in this order. Run each check before the next step. If a check fails, stop.

## 1. Stop the LaunchAgent

```
launchctl bootout gui/$(id -u)/com.briankwon.cornerstone-weekly
```

Check: `launchctl list | grep cornerstone` prints nothing.

## 2. Remove the worktrees of merged specs

A worktree of an open spec stays. The move step repairs it.

First, list each worktree whose branch is merged into `origin/main`. The command fetches first, so the test sees the latest `main`. It removes nothing.

```
cd ~/repos/cpcfantasyfootball && git fetch origin && for wt in .claude/worktrees/*(N); do b=$(git -C "$wt" branch --show-current); [ -n "$b" ] || continue; if git merge-base --is-ancestor "$b" origin/main || [ -n "$(gh pr list --state merged --head "$b" --json number --jq '.[0].number')" ]; then echo "$wt $b"; fi; done
```

The `(N)` makes an empty glob match nothing. Without it, zsh stops with "no matches found" when `.claude/worktrees/` is empty.

A squash merge leaves the branch out of `main`. The `gh pr list` test finds those branches.

Read the list. Then remove each listed worktree. The command refuses to remove a worktree with changes.

```
git worktree remove .claude/worktrees/<name>
```

Check: `git worktree list` shows no listed worktree.

## 3. Move the folder

If `~/repos/4thandgoal` exists, `mv` puts the repo inside it. The guard makes the command do nothing in that case.

```
test ! -e ~/repos/4thandgoal && mv ~/repos/cpcfantasyfootball ~/repos/4thandgoal
```

If the command prints nothing and the target exists, stop. Look at the target. Rename or remove it only if it is empty or stale. Then run the command again.

Check: `git -C ~/repos/4thandgoal remote -v` shows `bkwon94/4thandgoal` for fetch and push.

## 4. Repair the worktrees

Pass the path of each remaining worktree. Include a worktree outside the repo, such as one in `/private/tmp`.

First, set `other` to the path of each outside worktree. Set it to nothing if there is none. Find them in the output of `git worktree list` before the move.

```
other=/private/tmp/example-worktree
cd ~/repos/4thandgoal && git worktree repair .claude/worktrees/*(N) $other
```

The `(N)` makes an empty glob match nothing. Without it, zsh stops with "no matches found" when `.claude/worktrees/` is empty. The value `/private/tmp/example-worktree` is an example. Replace it.

Check: `git worktree list` shows `/Users/brian.kwon/repos/4thandgoal` and no line with `prunable`.

## 5. Move the Claude project folder

This folder holds the memory and the sessions of the repo.

If the new folder exists, `mv` puts the old folder inside it. The guard makes the command do nothing in that case.

```
test ! -e ~/.claude/projects/-Users-brian-kwon-repos-4thandgoal && mv ~/.claude/projects/-Users-brian-kwon-repos-cpcfantasyfootball ~/.claude/projects/-Users-brian-kwon-repos-4thandgoal
```

If the command prints nothing and the new folder exists, stop. Look at the new folder. A session may have made it. Ask before you merge or remove it.

Check: `ls ~/.claude/projects | grep -E 'cpcfantasyfootball|4thandgoal'` prints only the `4thandgoal` folder.

## 6. Set the marketplace and the plugin

In `~/.claude/settings.json`, make these three changes:

1. Rename the marketplace key to `4ag-local`.
2. Set its path to `/Users/brian.kwon/repos/4thandgoal`.
3. Set the plugin to `4ag@4ag-local`.

Also change the old path in the two `autoMode` lines.

Check: `grep -n cpcfantasyfootball ~/.claude/settings.json` prints nothing.

## 7. Rebuild the venv and the node modules

The old venv holds the old path.

```
cd ~/repos/4thandgoal && rm -rf .venv && uv sync --all-packages && pnpm install
```

Check: `.venv/bin/python -c "import sys; print(sys.prefix)"` prints a path under `/Users/brian.kwon/repos/4thandgoal`.

## 8. Copy and load the LaunchAgent

```
cp ~/repos/4thandgoal/apps/pipeline/launchagents/com.briankwon.cornerstone-weekly.plist ~/Library/LaunchAgents/ && launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.briankwon.cornerstone-weekly.plist
```

Check: `launchctl list | grep cornerstone` shows the job.

## 9. Prove the plugin loads

Open a new Claude session in `~/repos/4thandgoal`. Call one `4ag:` skill.

Check: `/plugin` lists `4ag@4ag-local` as enabled.

## Record the move

Paste these three outputs into the close comment of ticket 03:

1. `git worktree list`
2. `launchctl list | grep cornerstone`
3. The `/plugin` view with `4ag@4ag-local` enabled
