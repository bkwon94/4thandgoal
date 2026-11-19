# 02 notes: Does Codex find a repo skill

Research for decision ticket 02. Checked on 2026-11-18 against `codex-cli 0.169.0` and `openai/codex` `main` at `60fcb1649f0c3213d9d44c7c0caaca6459fb7c6c`.

## Answer

1. Codex finds a repo skill at `.agents/skills/<name>/SKILL.md`. It does not read `.claude/skills/`.
2. Put the real file at `.claude/skills/verify/SKILL.md`, so Claude Code finds it.
3. Add one tracked symlink `.agents/skills/verify -> ../../.claude/skills/verify`, so Codex finds the same file.
4. Git, Claude Code, and Codex all accept this symlink. The repo uses this exact pattern now for its seven 4ag skills.

## Where Codex looks for a skill

The official docs list these locations. Source: https://developers.openai.com/codex/skills, which redirects (308) to https://learn.chatgpt.com/docs/build-skills.

- Repo: `.agents/skills` "in every directory from your current working directory" up to the repository root.
- User: `$HOME/.agents/skills`.
- Admin: `/etc/codex/skills`.
- System: skills that ship with Codex, such as `skill-creator`.

The docs do not name `.claude/skills` or `.codex/skills` as a skill location. The docs also say: "Codex supports symlinked skill folders and follows the symlink target when scanning these locations." They say `SKILL.md` "must include `name` and `description`."

The source agrees. In https://github.com/openai/codex/blob/60fcb1649f0c3213d9d44c7c0caaca6459fb7c6c/codex-rs/ext/skills/src/host_roots.rs:

- `AGENTS_DIR_NAME` is `".agents"` and `SKILLS_DIR_NAME` is `"skills"`.
- `repo_agents_skill_roots` probes `<dir>/.agents/skills` for each directory from the project root to the CWD, with the scope `SkillScope::Repo`.
- `roots_from_layer_stack` adds `$CODEX_HOME/skills` (a comment marks it "Deprecated"), `~/.agents/skills`, and the system cache.
- For a project config layer, it also adds `<config folder>/skills`. That folder is `.codex/` of the project (https://github.com/openai/codex/blob/60fcb1649f0c3213d9d44c7c0caaca6459fb7c6c/codex-rs/config/src/state.rs, `config_folder`). So `.codex/skills/` also works in the source. The docs do not list it, and the project layer loads only for a trusted project. Do not use it.

No skill root names `.claude`. The one `.claude` string in the source is `ClaSource::CONFIG_DIR` in `codex-rs/external-agent-migration/src/source/cla.rs`. That code is a one-time import of Claude config, not a live skill root. The `source-command-commands-*` entries in `~/.agents/skills/` look like the output of that import.

## Symlinks

- Codex: https://github.com/openai/codex/blob/60fcb1649f0c3213d9d44c7c0caaca6459fb7c6c/codex-rs/ext/skills/src/loader/host.rs line 162 sets `DirectorySymlinkPolicy::Follow` for `SkillScope::User | SkillScope::Repo | SkillScope::Admin`. Only `System` ignores a symlink. The scan skips hidden folders inside a root (`HiddenDirectoryPolicy::Skip`, line 176), but the root `.agents/skills` itself is a direct probe.
- Claude Code: https://code.claude.com/docs/en/skills names the project location `.claude/skills/<skill-name>/SKILL.md`. It also says a `<skill-name>` entry "can be a symlink to a directory elsewhere on disk." With the plan, Claude reads the real folder, so it needs no symlink.
- Git: git stores a symlink as mode `120000` with the target path as its content. This repo already tracks seven such links (`git ls-files -s .agents` shows mode `120000`). `core.symlinks` is unset here, so it takes the default `true` (https://git-scm.com/docs/git-config#Documentation/git-config.txt-coresymlinks). On a checkout with `core.symlinks=false`, such as some Windows setups, git writes a plain text file. Codex then does not find the skill there. No such checkout exists in this flow.

## Skill name in Codex

Codex takes the name from the `name` frontmatter. It adds a plugin prefix when a plugin manifest sits above the real path of the skill (https://github.com/openai/codex/blob/60fcb1649f0c3213d9d44c7c0caaca6459fb7c6c/codex-rs/ext/skills/src/loader/namespace.rs, `SkillNamespaceResolver`). That is why `.agents/skills/4ag-plan`, which resolves into `.claude/plugin/` with `.claude/plugin/.claude-plugin/plugin.json` named `4ag`, shows as `4ag:plan`. A `verify` skill at `.claude/skills/verify/` has no manifest above it. The inference is that it shows as plain `verify` in both harnesses.

## How the repo installs its 4ag skills for Codex now

- The real skills live at `.claude/plugin/skills/<name>/`, in the Claude plugin `4ag`.
- `.agents/skills/` holds seven tracked relative symlinks: `4ag-implement`, `4ag-plan`, `4ag-quick`, `4ag-review`, `4ag-to-acceptance`, `4ag-to-spec`, `4ag-to-tickets`. Each points to `../../.claude/plugin/skills/<name>`. The last commit that changed them is `7c4c956a` (#42).
- `docs/agents/codex.md` step 3 makes the same links by hand before a spec merges. Step 7 turns off the cached plugins `4ag@4ag-local` and `cpc@cpc-local` in `~/.codex/config.toml`, so each skill lists once.
- `~/.agents/skills/` holds user skills. `research` is a symlink into the Claude plugin cache of `mattpocock-skills` 1.3.1 (step 4).

## Local check

In this worktree, `codex debug prompt-input "hi"` lists each of `4ag:implement`, `4ag:plan`, `4ag:quick`, `4ag:review`, `4ag:to-acceptance`, `4ag:to-spec`, and `4ag:to-tickets` once. The entry for `4ag:plan` shows `(file: r38/4ag-plan/SKILL.md)`, so Codex reads it through the `.agents/skills` symlink. I did not add a test skill under `.claude/skills/`, because this task changes no file but this one.

## Suggested decision

Keep the source at `.claude/skills/verify/SKILL.md`. Add a tracked relative symlink at `.agents/skills/verify` that points to `../../.claude/skills/verify`. Check it with `codex debug prompt-input "hi" | grep -o '\\n- verify:'`. A running Codex keeps the skill list from its start, so restart Codex after you add the link.
