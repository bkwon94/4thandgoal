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

The command fetches first, so the test sees the latest `main`. Then it removes each worktree whose branch is merged into `origin/main`, and prints the path and the branch of each one. It keeps the branch. It never uses `--force`, so it refuses to remove a worktree with changes and prints why.

```
cd ~/repos/cpcfantasyfootball && git fetch origin && for wt in .claude/worktrees/*(N); do b=$(git -C "$wt" branch --show-current); [ -n "$b" ] || continue; if git merge-base --is-ancestor "$b" origin/main || [ -n "$(gh pr list --state merged --head "$b" --json number --jq '.[0].number')" ]; then echo "remove $wt $b"; git worktree remove "$wt"; fi; done
```

The `(N)` makes an empty glob match nothing. Without it, zsh stops with "no matches found" when `.claude/worktrees/` is empty.

A squash merge leaves the branch out of `main`. The `gh pr list` test finds those branches. A detached worktree has no branch, so the command skips it.

Check: `git worktree list` shows no worktree that the command printed as `remove`, except one that it refused because of changes. Look at each refused worktree before step 3.

## 3. Move the folder

If `~/repos/4thandgoal` exists, `mv` puts the repo inside it. The guard makes the command do nothing in that case.

```
test ! -e ~/repos/4thandgoal && mv ~/repos/cpcfantasyfootball ~/repos/4thandgoal
```

If the command prints nothing and the target exists, stop. Look at the target. Rename or remove it only if it is empty or stale. Then run the command again.

Check: `git -C ~/repos/4thandgoal remote -v` shows `bkwon94/4thandgoal` for fetch and push.

## 4. Repair the worktrees

Pass the path of each remaining worktree. Include a worktree outside the repo, such as one in `/private/tmp`.

The command finds each outside worktree from the git records, which still hold their paths. Then it repairs them with the worktrees under `.claude/worktrees/`.

```
cd ~/repos/4thandgoal && { other=(${(f)"$(git worktree list --porcelain | awk '/^worktree /{print $2}' | grep -v -e '/repos/4thandgoal' -e '/repos/cpcfantasyfootball')"}); git worktree repair .claude/worktrees/*(N) $other; }
```

The command is for zsh. The `(N)` makes an empty glob match nothing. Without it, zsh stops with "no matches found" when `.claude/worktrees/` is empty. The `${(f)...}` splits the outside paths into one word for each line. With no outside worktree, the list is empty and `grep` exits 1, so the `;` makes the repair run all the same.

Check: `git worktree list` shows `/Users/brian.kwon/repos/4thandgoal` and no line with `prunable`.

## 5. Move the Claude project folder

This folder holds the memory and the sessions of the repo.

If the new folder exists, `mv` puts the old folder inside it. The guard makes the command do nothing in that case.

```
test ! -e ~/.claude/projects/-Users-brian-kwon-repos-4thandgoal && mv ~/.claude/projects/-Users-brian-kwon-repos-cpcfantasyfootball ~/.claude/projects/-Users-brian-kwon-repos-4thandgoal
```

If the command prints nothing and the new folder exists, stop. Look at the new folder. A session may have made it. Ask before you merge or remove it.

Check: `test ! -e ~/.claude/projects/-Users-brian-kwon-repos-cpcfantasyfootball && test -d ~/.claude/projects/-Users-brian-kwon-repos-4thandgoal && echo ok` prints `ok`.

Claude keeps one more project folder for each worktree, named `-Users-brian-kwon-repos-cpcfantasyfootball--claude-worktrees-<name>`. Those folders stay where they are. The sessions of a worktree do not carry over.

## 6. Set the marketplace and the plugin

The command copies `~/.claude/settings.json` to `~/.claude/settings.json.bak`. Then it changes three names in the file:

1. The old folder and repo name `cpcfantasyfootball` becomes `4thandgoal`. This changes the marketplace path and the old names in the `autoMode` lines.
2. The plugin `cpc@cpc-local` becomes `4ag@4ag-local`.
3. The marketplace key `cpc-local` becomes `4ag-local`.

```
cp ~/.claude/settings.json ~/.claude/settings.json.bak && sed -i '' -e 's#cpcfantasyfootball#4thandgoal#g' -e 's#"cpc@cpc-local"#"4ag@4ag-local"#g' -e 's#"cpc-local"#"4ag-local"#g' ~/.claude/settings.json
```

Check: `grep -nE 'cpcfantasyfootball|cpc-local' ~/.claude/settings.json` prints nothing, and `python3 -m json.tool ~/.claude/settings.json >/dev/null && echo ok` prints `ok`.

## 7. Rebuild the venv and the node modules

The old venv holds the old path.

```
cd ~/repos/4thandgoal && rm -rf .venv && uv sync --all-packages && pnpm install
```

Check: `.venv/bin/python -c "import sys; print(sys.prefix)"` prints a path under `/Users/brian.kwon/repos/4thandgoal`. Then `pnpm --dir apps/site exec node -e 1` prints nothing and exits with 0.

## 8. Copy and load the LaunchAgent

```
cp ~/repos/4thandgoal/apps/pipeline/launchagents/com.briankwon.cornerstone-weekly.plist ~/Library/LaunchAgents/ && launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.briankwon.cornerstone-weekly.plist
```

Check: `launchctl list | grep cornerstone` shows the job.

## 9. Prove the plugin loads

```
cd ~/repos/4thandgoal && claude
```

In the new session, call one `4ag:` skill.

Check: `/plugin` lists `4ag@4ag-local` as enabled.

## Record the move

Paste these three outputs into the close comment of ticket 03:

1. `git worktree list`
2. `launchctl list | grep cornerstone`
3. The `/plugin` view with `4ag@4ag-local` enabled
