# 02: Notes on the Codex skill loader

Summary: Codex takes the name from the `name:` line, and it adds the plugin name from `.claude-plugin/plugin.json` above the symlink target. So `.agents/skills/<any>` -> `.claude/plugin/skills/plan` shows as `4ag:plan`, and `$4ag-plan` cannot exist through a plain symlink.
Codex follows a symlink to a folder in `.agents/skills/`, and the model reads the sibling files at the target path. A repo skill and a user skill with the same name are both listed, repo first, and a plain `$name` call then loads neither.

Source: the tag `rust-v0.167.1` of github.com/openai/codex, commit `0a94398fa60c4fac0e7659e4213a0a36e613dd46`. This tag is the same version as the installed `codex-cli 0.167.1`. In the links, `SRC` is `https://github.com/openai/codex/blob/rust-v0.167.1/codex-rs`.

Docs: `https://developers.openai.com/codex/skills` redirects (308) to `https://learn.chatgpt.com/docs/build-skills`.

## The test setup

The test repo is `/private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/6d42e2b2-0a8b-4a83-8539-41d47147e51d/scratchpad/codex-loader/repo`, a git repo. A temporary `HOME` and `CODEX_HOME` keep Brian's `~/.agents/skills/` and `~/.codex/` out of the test. No file in either folder changed.

```
repo/.agents/skills/qclash/SKILL.md                 name: qclash, "QCLASH REPO COPY."
repo/.agents/skills/zzq-alpha -> ../../plug/skills/alpha
repo/.agents/skills/zzq-beta  -> ../../other/skills/beta
repo/.agents/skills/zzq-gamma -> ../../other/skills/gamma
repo/.agents/skills/zzh-delta -> ../../.claude/plugin/skills/delta
repo/plug/.claude-plugin/plugin.json                {"name":"zzq"}
repo/plug/skills/alpha/SKILL.md + formats.md        name: alpha
repo/other/skills/beta/SKILL.md                     name: beta, no manifest above it
repo/other/skills/gamma/SKILL.md                    no name: line
repo/.claude/plugin/.claude-plugin/plugin.json      {"name":"zzh"}   (same shape as the 4ag plugin)
repo/.claude/plugin/skills/delta/SKILL.md           name: delta, "Read formats.md in this folder and print the token in it."
repo/.claude/plugin/skills/delta/formats.md         TOKEN-DELTA-4419
home/.agents/skills/qclash/SKILL.md                 name: qclash, "QCLASH USER COPY."
```

Run 1 lists the skills with no model call. `codex debug prompt-input` prints the prompt that the model sees:

```
cd .../codex-loader/repo
HOME=$T/home CODEX_HOME=$T/codexhome ~/.local/bin/codex debug prompt-input "hi"
```

Output, the system skills cut:

```
### Skill roots
- `r0` = `.../codex-loader/home/.agents/skills`
- `r1` = `.../codex-loader/codexhome/skills/.system`
- `r2` = `.../codex-loader/repo/.agents/skills`
### Available skills
- beta: Beta test skill with no plugin manifest above it. (file: r2/zzq-beta/SKILL.md)
- gamma: Gamma test skill with no name line. (file: r2/zzq-gamma/SKILL.md)
- qclash: QCLASH REPO COPY. (file: r2/qclash/SKILL.md)
- zzh:delta: Delta test skill under a hidden .claude/plugin folder. (file: r2/zzh-delta/SKILL.md)
- zzq:alpha: Alpha test skill. Read formats.md beside this file. (file: r2/zzq-alpha/SKILL.md)
- qclash: QCLASH USER COPY. (file: r0/qclash/SKILL.md)
```

Run 2 is one real `codex exec` turn. A copy of `auth.json` sat in the temporary `CODEX_HOME` for the run, and the copy is now deleted.

```
HOME=$T/home CODEX_HOME=$T/codexhome ~/.local/bin/codex exec --json -s read-only \
  'Use $zzh:delta, then use $qclash. Give two lines only: line 1 is the token that delta asks for; line 2 is the one word that the qclash skill body tells you to say. Then stop.' </dev/null
```

Output, the completed items of `--json`:

```
{"type":"agent_message","text":"I’m using zzh:delta, then qclash.\n"}
{"type":"command_execution","text":"/bin/zsh -lc 'cat .claude/plugin/skills/delta/formats.md .agents/skills/qclash/SKILL.md'","out":"TOKEN-DELTA-4419\n---\nname: qclash\ndescription: QCLASH REPO COPY.\n---\n\nSay REPO.\n"}
{"type":"agent_message","text":"TOKEN-DELTA-4419\nREPO"}
```

The session log in `codexhome/sessions/2026/11/11/rollout-...jsonl` holds one injected skill only:

```
<skill>\n<name>zzh:delta</name>\n<path>.../codex-loader/repo/.claude/plugin/skills/delta/SKILL.md</path>\n---\nname: delta ...
```

It holds no `<skill>` item for `qclash`.

## 1. The skill name: folder or `name:` line

**Answer.** Codex takes the name from the `name:` line. It uses the folder name only when `name:` is absent or empty, and then it uses the folder of the symlink target, not the symlink. Codex then adds a namespace. It walks up from the symlink target, and the nearest `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, or `.cursor-plugin/plugin.json` gives the prefix `<plugin name>:`. The 4ag skills sit under `.claude/plugin/.claude-plugin/plugin.json`, which has `"name": "4ag"`. So each symlink shows as `4ag:plan`, `4ag:to-spec`, and so on, whatever the symlink is named.

**`$4ag-plan` with no change to the Claude name.** No option gives this through a symlink:

- Codex has no name override. The frontmatter parser reads only `name`, `description`, and `metadata.short-description`.
- `agents/openai.yaml` has `interface.display_name`, but that is a label for the app UI, not the name for a `$` call.
- The only routes to `$4ag-plan` are a change of `name:` to `4ag-plan`, or a real wrapper folder with its own `SKILL.md` that points at the source. A change of `name:` changes the Claude name too.

The better fact: `:` is a legal character in a `$` mention. So Codex calls `$4ag:plan`, the same name as Claude. Run 2 shows that `$zzh:delta` loads the skill.

**Sources.**

- The `name:` line wins, with a fallback to the folder name: `SRC/skills/src/parser.rs` lines 64-69, and `SRC/ext/skills/src/loader/host.rs` lines 374 and 396-406.
- The fallback uses the target folder. The skill path is the canonical path, at `SRC/ext/skills/src/loader/host.rs` lines 194-207, and that path goes to `default_skill_name`.
- The namespace comes from the nearest manifest above the canonical target: `SRC/ext/skills/src/loader/namespace.rs` lines 11-24 and 150-163, and `SRC/ext/skills/src/loader/host.rs` lines 263-267 and 317-320.
- The manifest paths include `.claude-plugin/plugin.json`: `SRC/exec-server-protocol/src/protocol.rs` lines 55-59. The prefix is the manifest `name`: `SRC/utils/plugins/src/plugin_namespace.rs` lines 89-119.
- The prefix format is `{namespace}:{base_name}`: `SRC/ext/skills/src/loader/namespace.rs` line 179.
- The frontmatter fields: `SRC/skills/src/parser.rs` lines 7-20. The `openai.yaml` interface fields: `SRC/skills/src/model.rs` lines 70-76.
- `:` is a mention character: `SRC/skills/src/mentions.rs` lines 226-227.
- The docs say `SKILL.md` "must include `name` and `description`". They do not say how the folder name and `name:` relate. See `https://learn.chatgpt.com/docs/build-skills`.

**Run evidence.** Run 1 shows that `zzq-beta` lists as `beta`, so the `name:` line wins. `zzq-gamma` has no `name:` line and lists as `gamma`, the target folder. `zzq-alpha` lists as `zzq:alpha`, and `zzh-delta` lists as `zzh:delta`, so the manifest above the target adds the prefix. The `zzh-delta` case has the same shape as the real repo: a hidden `.claude/plugin/` folder with `.claude-plugin/plugin.json`.

## 2. Symlinks and sibling files

**Answer.** Yes. Codex follows a symlink to a folder in the repo, user, and admin roots. It does not follow one in the system root. The model reads the sibling files, such as `formats.md`. The injected `<skill>` block gives the canonical target path, `.claude/plugin/skills/<name>/SKILL.md`. So the model reads the sibling files at the source path, not through the symlink. A relative path such as `formats.md` in the skill text resolves beside the real `SKILL.md`. The listing shows the symlink path, such as `r2/zzh-delta/SKILL.md`.

A hidden folder in the target, such as `.claude`, causes no problem. The loader skips hidden folders only below the scan root on the walk path, and the walk path is `.agents/skills/<link>/`.

**Sources.**

- The symlink policy for each scope: `SRC/ext/skills/src/loader/host.rs` lines 164-167. The walk option: `SRC/ext/skills/src/loader/discovery.rs` lines 75-78.
- The skill path becomes canonical: `SRC/ext/skills/src/loader/host.rs` lines 194-207 and 389.
- The hidden-folder rule is checked below the scan root only: `SRC/ext/skills/src/loader/discovery.rs` lines 121-123 and 179-191.
- The docs say: "Codex supports symlinked skill folders and follows the symlink target when scanning these locations." See `https://learn.chatgpt.com/docs/build-skills`.

**Run evidence.** Run 1 lists all four symlinked skills. In run 2, the injected path is `.../repo/.claude/plugin/skills/delta/SKILL.md`. The model ran `cat .claude/plugin/skills/delta/formats.md` and printed `TOKEN-DELTA-4419`.

## 3. A repo skill and a user skill with the same name

**Answer.** Neither wins. Codex removes a duplicate by path, not by name, so both skills stay in the list. The list sorts by scope, with repo before user, then by name. A plain `$name` call loads a skill only when exactly one skill has that name. With a clash, `$qclash` injects no skill at all. The model then sees two `qclash` entries in the list and picks one by itself. In run 2 it picked the repo copy, which is first in the list, but no rule makes it do so. A path mention, such as a pick from the `$` popup in the TUI, still selects one exact skill.

So a bare `implement`, `to-spec`, or `to-tickets` in `.agents/skills/` would clash with Brian's user skills, and `$implement` would load nothing. The `4ag:` prefix removes the clash.

**Sources.**

- The duplicate removal is by path: `SRC/ext/skills/src/loader/host_merge.rs` lines 228-229. The sort is by scope rank, then name: lines 241-247 and 260-266.
- The user root `$HOME/.agents/skills` and the repo roots `.agents/skills` from the cwd up to the project root: `SRC/ext/skills/src/host_roots.rs` lines 142-147 and 216-244.
- A plain name loads only when its count is 1: `SRC/skills/src/selection.rs` line 39 and line 191. The core turn uses this function: `SRC/core/src/session/turn.rs` line 1154.
- The docs say: "If two skills share the same `name`, Codex doesn’t merge them; both can appear in skill selectors." See `https://learn.chatgpt.com/docs/build-skills`.

**Run evidence.** In run 1, both `qclash` entries are in the list, the repo copy first. In run 2, the session log has no `<skill>` item for `qclash`. The model read `.agents/skills/qclash/SKILL.md` with `cat` by its own choice.

## What this means for the spec

The layout that works:

```
.agents/skills/4ag-plan          -> ../../.claude/plugin/skills/plan
.agents/skills/4ag-to-spec       -> ../../.claude/plugin/skills/to-spec
.agents/skills/4ag-to-acceptance -> ../../.claude/plugin/skills/to-acceptance
.agents/skills/4ag-to-tickets    -> ../../.claude/plugin/skills/to-tickets
.agents/skills/4ag-implement     -> ../../.claude/plugin/skills/implement
.agents/skills/4ag-review        -> ../../.claude/plugin/skills/review
```

Changes that the facts force on decision 01:

1. **Item 3, the names.** Codex calls `$4ag:plan`, not `$4ag-plan`. The name is the same in both harnesses, so the skill text can use `4ag:plan` with no adapter for the name. The symlink name does not set the Codex name. Keep `4ag-<name>` for the symlinks anyway, because a symlink named `implement` is confusing beside Brian's user skill of the same name.
2. **A hard dependency.** The `4ag:` prefix exists only because `.claude/plugin/.claude-plugin/plugin.json` has `"name": "4ag"` above the target. The spec must keep that file and that name. If the manifest moves or its name changes, Codex lists bare `implement`, `to-spec`, and `to-tickets`, and these clash with Brian's user skills. A clash makes a plain `$implement` load nothing.
3. **Sibling files.** The model reads them at `.claude/plugin/skills/<name>/`. Relative paths in the skill text work. Text that names the path `.agents/skills/...` for a sibling file would also work through the symlink, but the source path is the one Codex gives the model.
4. **A smoke check for the proof, item 7.** `codex debug prompt-input "hi"` lists each skill with no model call and no cost. A check can grep its output for the six `4ag:` names.

If Brian still wants `$4ag-plan` with a hyphen, the only route is six real wrapper folders, each with a `SKILL.md` that has `name: 4ag-<name>` and points at the source. That route adds six files that can drift, so these notes do not recommend it.
