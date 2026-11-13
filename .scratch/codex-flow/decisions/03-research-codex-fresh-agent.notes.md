# 03: How Codex starts a fresh agent — notes

Research for `decisions/03-research-codex-fresh-agent.md`. Codex CLI 0.167.1, run on 2026-11-11.

## Summary

1. Yes. A Codex session has a `spawn_agent` tool. With `fork_turns: "none"` the child gets only its brief; the default `all` forks the full parent history. A skill asks for it in plain words.
2. Yes, `codex exec` also works. The prompt goes in as an argument or on stdin. stdout holds only the last message, `-o <file>` writes the same text, and `--json` gives JSONL events.
3. Yes. `spawn_agent` takes `model` and `reasoning_effort`; `codex exec` takes `-m` and `-c model_reasoning_effort=...`. `gpt-6-astra` fills the place of `opus`.
4. Yes, with one catch. `workspace-write` makes `.git` read-only and turns the network off, so `git commit` and `gh` fail. A permission profile that grants write on the gitdir and turns on the network fixes both, with approval `never`.

The runs used a throwaway repo at `/private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/6d42e2b2-0a8b-4a83-8539-41d47147e51d/scratchpad/codex-agent/repo`. It has a branch `spec` and a ticket worktree `.claude/worktrees/spec-01` on branch `spec-01`, in the same layout as `build.md`. Below, `$D` is `.../scratchpad/codex-agent` and `$WT` is `$D/repo/.claude/worktrees/spec-01`. The source is a clone of `github.com/openai/codex` at tag `rust-v0.167.1` (commit `0a94398f`).

## 1. Can a Codex session start a subagent?

### Answer

Yes. The feature `multi_agent` is `stable` and `true` for this account. The session gets a `spawn_agent` tool, plus `wait`, `send_input`, and `close_agent` tools.

The child starts with no parent history only if the call says so. Two versions of the tool exist:

- **V2** has the parameter `fork_turns`. It "Defaults to `all`; use `none` to start without parent history." Each model in this account's catalog sets the version. `gpt-6.1-sol`, `gpt-6-astra`, and most other models use `v2`.
- **V1** has the parameter `fork_context`. False or omitted "starts with only the initial prompt." Only `gpt-reserve`, `gpt-5.6-luna`, and `codex-auto-review` use `v1`.

So a skill must ask for `fork_turns: "none"` in plain words. If the skill does not, the Judge gets the full context of the build. That breaks ADR 0026.

A skill tells Codex to start one in plain words. The docs say Codex delegates "when applicable `AGENTS.md` or skill instructions request it". No special syntax exists. The run below used the words "Use your spawn_agent tool" and named the parameters, and Codex passed them exactly.

Limits that matter for `4ag:implement`:

- `agent_max_depth` defaults to 1. The main session can spawn, but a child cannot spawn a grandchild. The call returns "Agent depth limit reached. Solve the task yourself."
- `agents.max_threads` defaults to 6 open children at a time. A completed child counts until `close_agent` closes it.
- The child inherits the sandbox, the approval policy, and the cwd of the parent turn. A custom agent file cannot change the sandbox.
- A child with `fork_turns: "all"` failed under `codex exec --ephemeral`, because the fork reads the parent rollout from disk. A child with `none` works under `--ephemeral`.

### Sources

- Docs: https://developers.openai.com/codex/subagents (redirects to https://learn.chatgpt.com/docs/agent-configuration/subagents). Codex handles "spawning new subagents, routing follow-up instructions, waiting for results, and closing agent threads." Subagents inherit the parent sandbox policy. Codex delegates when skill instructions ask.
- `codex-rs/core/src/tools/handlers/multi_agents_spec.rs:664-668`: the V2 `fork_turns` text, "Defaults to `all`".
- `codex-rs/core/src/tools/handlers/multi_agents_spec.rs:626-631`: the V1 `fork_context` text, "false or omitted starts with only the initial prompt".
- `codex-rs/core/src/tools/handlers/multi_agents_v2/spawn.rs:221-233`: an empty `fork_turns` becomes `"all"`, which becomes `SpawnAgentForkMode::FullHistory`.
- `codex-rs/core/src/tools/handlers/multi_agents/spawn.rs:112,227`: V1 `fork_context` defaults to `false`.
- `codex-rs/core/src/config/mod.rs:1687-1712`: the feature `multi_agent_v2` forces V2; else the model's `multi_agent_version` decides.
- `codex-rs/core/src/config/mod.rs:260,270`: `DEFAULT_AGENT_MAX_THREADS = Some(6)`, `DEFAULT_AGENT_MAX_DEPTH = 1`.
- `codex-rs/core/src/tools/handlers/multi_agents/spawn.rs:74-79`: the depth check.
- `codex-rs/core/src/agent/child_config.rs:104-110,175-200`: the child config copies the approval policy, the sandbox, and the cwd of the parent turn.

### Runs

```
$ codex features list | grep -E 'multi_agent'
multi_agent                              stable             true
multi_agent_mode                         removed            false
multi_agent_v2                           stable             false
multi_agent_v2_dynamic_tools             under development  false
```

```
$ codex debug models   # parsed: slug, priority, multi_agent_version
gpt-6.1-sol 1 v2
gpt-6-astra 2 v2
gpt-6.1-terra 3 v2
gpt-6-sol 4 v2
gpt-reserve 5 v1
gpt-6-luna 6 v2
gpt-5.6-sol 7 v2
gpt-5.6-terra 8 v2
gpt-5.6-luna 9 v1
codex-auto-review 10 v1
```

Run 4 put a secret word in the parent prompt only. It then asked for two children with the same brief. Agent A used `fork_turns: "none"`. Agent B left `fork_turns` out.

```
$ cd $D; codex exec -C "$WT" -s read-only -m gpt-6.1-sol -c model_reasoning_effort='"low"' \
    --ephemeral --json -o $D/run4.last.txt "The secret word for this session is PELICAN-42. Do not write \
    the secret word in any message to a subagent. Use your spawn_agent tool twice, then wait for both \
    agents and report their answers verbatim. Agent A: set fork_turns to \"none\", model to \"gpt-6-luna\", \
    reasoning_effort to \"low\". Agent B: omit fork_turns, model to \"gpt-6-luna\", reasoning_effort to \
    \"low\". Give each agent only this message: 'Answer in one line: do you see any secret word in your \
    conversation history? If yes, write it.' Finally, print the exact JSON arguments you passed to each \
    spawn_agent call." > $D/run4.jsonl 2> $D/run4.err
exit=0

$ cat $D/run4.last.txt
Agent A’s verbatim answer:
> Yes: “secret word.”

Agent B failed to start, so it has no answer to await.

Exact arguments for Agent A:
{"task_name":"agent_a","fork_turns":"none","model":"gpt-6-luna","reasoning_effort":"low","message":"Answer in one line: do you see any secret word in your conversation history? If yes, write it."}

Exact arguments for Agent B:
{"task_name":"agent_b","model":"gpt-6-luna","reasoning_effort":"low","message":"Answer in one line: do you see any secret word in your conversation history? If yes, write it."}

$ grep -i spawn $D/run4.err
... ERROR codex_core::tools::router: error=collab spawn failed: Fatal error: failed to load model context
for thread 01a1cdb6-...: invalid thread-store request: no rollout found for thread id 01a1cdb6-...
```

What the run shows:

- The tool has `task_name` and `fork_turns`, so it is V2.
- Agent A did not see `PELICAN-42`. It quoted only the words "secret word" of its own brief. The fresh child has none of the parent context.
- Agent B tried a full-history fork and failed only because of `--ephemeral`. In an interactive session, which keeps its rollout, Agent B forks the full history. This run did not test that case, to keep `~/.codex/` unchanged.
- `codex exec --json` gives no event for a `spawn_agent` call. The run shows only `agent_message` items. The model and the effort of the child come from the parent report and from the source, not from an event.

## 2. Does a new `codex exec` process work as the fresh agent?

### Answer

Yes. Each `codex exec` is a new session with no history, so it is fresh by build. It also loads the `AGENTS.md` of its cwd and the user config, like any session.

- **The prompt.** Pass it as the last argument. Or omit it, or pass `-`, and pipe it on stdin. If you give both, the argument is the task and stdin becomes a `<stdin>` block.
- **Stdin.** `codex exec` prints "Reading additional input from stdin..." if stdin is open. Give it `< /dev/null` when the prompt is an argument, or it waits on stdin.
- **The output.** stdout holds only the last agent message. Progress goes to stderr. `-o <file>` writes the same last message to a file. In run 2 the file and stdout differ only in the trailing newline. `--json` turns stdout into JSONL events. `--output-schema <file>` asks for a last message in a JSON Schema shape.
- **The exit code.** The exit code is 0 when the turn completes, even when a command inside it fails. The parent must read the message or the files, not the exit code.
- **Approval.** `codex exec` defaults to approval `never`, so it never waits on the user.

### Sources

- Docs: https://developers.openai.com/codex/noninteractive (redirects to https://learn.chatgpt.com/docs/non-interactive-mode). Codex "streams progress to `stderr` and prints only the final agent message to `stdout`." "By default, `codex exec` runs in a read-only sandbox."
- `codex exec --help` (below): the `[PROMPT]` text, `--json`, `-o`, `--output-schema`, `--ephemeral`, `-C`.
- `codex-rs/exec/src/lib.rs:595-597`: "Default to never ask for approvals in headless mode", `approval_policy: Some(AskForApproval::Never)`.

### Runs

```
$ codex --version
codex-cli 0.167.1

$ codex exec --help   # excerpt
Usage: codex exec [OPTIONS] [PROMPT]
  [PROMPT]  Initial instructions for the agent. If not provided as an argument (or if `-` is used),
            instructions are read from stdin. If stdin is piped and a prompt is also provided, stdin
            is appended as a `<stdin>` block
  -m, --model <MODEL>                 Model the agent should use
  -s, --sandbox <SANDBOX_MODE>        [possible values: read-only, workspace-write, danger-full-access]
  -C, --cd <DIR>                      Tell the agent to use the specified directory as its working root
      --add-dir <DIR>                 Additional directories that should be writable alongside the primary workspace
      --ephemeral                     Run without persisting session files to disk
      --output-schema <FILE>          Path to a JSON Schema file describing the model's final response shape
      --json                          Print events to stdout as JSONL
  -o, --output-last-message <FILE>    Specifies file where the last message from the agent should be written
```

Run 1 used `--json` and `-o`:

```
$ codex exec -C "$WT" -s workspace-write -m gpt-6.1-sol -c model_reasoning_effort='"low"' --ephemeral \
    --json -o $D/run1.last.txt "Run these shell commands one at a time ... 1) pwd 2) echo built > built.txt \
    3) git add built.txt 4) git commit -m 'run1 commit' 5) gh auth status 6) curl ... https://api.github.com" \
    > $D/run1.jsonl 2> $D/run1.err
exit=0   (about 68 s)

event types in run1.jsonl: {'thread.started': 1, 'item.completed': 8, 'turn.started': 1, 'item.started': 4, 'turn.completed': 1}
first line:  {"type":"thread.started","thread_id":"01a1cdb3-008c-76e0-8039-ec7541a928fd"}
last line:   {"type":"turn.completed","usage":{"input_tokens":229415,"cached_input_tokens":208896,...,"output_tokens":608,...}}
```

Run 2 used plain stdout and `-o`:

```
$ diff $D/run2.stdout $D/run2.last.txt
5c5
< 5. `gh api repos/openai/codex --jq .full_name` — Exit code: `0`. First line: `openai/codex`
---
> 5. `gh api repos/openai/codex --jq .full_name` — Exit code: `0`. First line: `openai/codex`
\ No newline at end of file
```

The stderr header of run 3 shows the session settings and the stdin line:

```
Reading additional input from stdin...
OpenAI Codex v0.167.1
workdir: .../codex-agent/repo/.claude/worktrees/spec-01
model: gpt-6.1-sol
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR] (network access enabled)
reasoning effort: low
```

The user config of this account loads many plugins and MCP servers. Each run printed hook errors and MCP 404 errors on stderr, and run 1 used 229k input tokens, mostly cached. `--ignore-user-config` skips that config. This research did not test it.

## 3. Can the parent set the model and the reasoning effort?

### Answer

Yes, in both ways.

- **`spawn_agent`** takes `model` and `reasoning_effort`. Each one defaults to the value of the parent. The config `multi_agent_v2.expose_spawn_agent_model_overrides` defaults to `true`, so the parameters show. The tool text tells the model to set `model` only "if the user explicitly asks", so the skill must name the model.
- **Config defaults.** `agents.default_subagent_model` and `agents.default_subagent_reasoning_effort` set the default for each child.
- **Custom agent files.** A file `.codex/agents/<name>.toml` sets `model` and `model_reasoning_effort` for one role, called by `agent_type`. Its values take precedence. The spec does not need one.
- **`codex exec`** takes `-m <model>` and `-c model_reasoning_effort="<level>"`.

The model for the place of `opus` is `gpt-6-astra`. The catalog describes it as "Frontier intelligence for the most demanding work." `gpt-6.1-sol` is the default and the "Latest workhorse model for coding and everyday work". It fits a ticket builder, as `sonnet` or `opus` does in Claude. Both support efforts up to `ultra`. The catalog sets `multi_agent_reasoning_effort: xhigh` for `gpt-6.1-sol`, `gpt-6-astra`, and `gpt-6.1-terra`.

### Sources

- Docs: https://learn.chatgpt.com/docs/agent-configuration/subagents. "Without a configured value, a subagent inherits the parent's model and reasoning effort." "If a custom agent file sets `model` or `model_reasoning_effort`, the value in the file takes precedence."
- `codex-rs/core/src/tools/handlers/multi_agents_spec.rs:17-18,670-682`: the V2 `model` and `reasoning_effort` parameters and the "inherit" text.
- `codex-rs/core/src/config/mod.rs:1403,1427`: `expose_spawn_agent_model_overrides` defaults to `true`.
- `codex-rs/core/src/config/mod.rs:978,981`: `agent_default_subagent_model` and `agent_default_subagent_reasoning_effort`.
- `codex-rs/core/src/tools/handlers/multi_agents/spawn.rs:162-167`: the effective model and effort of the child come from its snapshot, else from the arguments.

### Runs

```
$ codex debug models   # parsed: slug | visibility | default effort | efforts | description
gpt-6.1-sol | list | low | ['low','medium','high','xhigh','max','ultra'] | Latest workhorse model for coding and everyday work.
gpt-6-astra | list | medium | ['low','medium','high','xhigh','max','ultra'] | Frontier intelligence for the most demanding work.
gpt-6.1-terra | list | low | ['low','medium','high','xhigh','max','ultra'] | GPT-6.1 Terra Codex model.
gpt-6-sol | list | medium | ['low','medium','high','xhigh','max','ultra'] | Previous generation workhorse model.
gpt-reserve | hide | medium | ['low','medium','high','xhigh','max'] | Fast and affordable agentic coding model.
gpt-6-luna | list | medium | ['low','medium','high','xhigh','max'] | Fast and affordable model for easier tasks.
gpt-5.6-sol | list | low | ['low','medium','high','xhigh','max','ultra'] | Older generation workhorse model.
gpt-5.6-terra | list | medium | ['low','medium','high','xhigh','max','ultra'] | Older balanced model for straightforward work.
gpt-5.6-luna | list | medium | ['low','medium','high','xhigh','max'] | Older fast and efficient model.
codex-auto-review | hide | medium | ['low','medium','high','xhigh','max'] | Automatic approval review model for Codex.
```

- Runs 1 to 3 passed `-m gpt-6.1-sol -c model_reasoning_effort='"low"'`. The stderr header shows `model: gpt-6.1-sol` and `reasoning effort: low`.
- Run 4 passed `"model":"gpt-6-luna","reasoning_effort":"low"` to `spawn_agent`, and Agent A started. No `--json` event shows the model of the child. The source above shows that the arguments set it.
- No run used `gpt-6-astra`, to keep the cost low. It is in the catalog with `visibility: list`.

## 4. Can the fresh agent work in a given worktree and run `git` and `gh`?

### Answer

Yes, but not with the plain `workspace-write` sandbox.

- **The worktree.** `-C <dir>` sets the working root for `codex exec`. A `spawn_agent` child has no cwd parameter. It inherits the cwd of the parent, so its brief must name the worktree path, and each command must use that path.
- **Files.** `workspace-write` lets the agent write in the working root, `/tmp`, and `$TMPDIR`.
- **`git`.** `workspace-write` protects `<root>/.git` as read-only. For a worktree it also protects the gitdir that the `.git` file points to. So `git add` and `git commit` fail with `index.lock: Operation not permitted`. `--add-dir <repo>/.git` does not help, because the default rule still covers it.
- **`gh` and the network.** `workspace-write` turns the network off. `gh api` fails. `-c sandbox_workspace_write.network_access=true` turns it on.
- **The fix.** A permission profile that extends `:workspace` can grant write on the gitdir and turn on the network. Run 3 passed it with `-c` and did not touch `~/.codex/`. `git commit` and `gh api` then passed, with approval `never` and no prompt.
- **Full access.** `-s danger-full-access` and `--dangerously-bypass-approvals-and-sandbox` also remove the limits. This research did not run them, because the Claude Code auto mode refused the run as unsafe. The docs mark them "not recommended".

A `spawn_agent` child inherits the sandbox of the parent session. So for a ticket builder to commit, the parent session must run with the same profile. In an interactive session that is a config value or a launch flag. The skill cannot change it.

### Sources

- Docs: https://learn.chatgpt.com/docs/agent-approvals-security. "`<writable_root>/.git` is protected as read-only whether it appears as a directory or file." `workspace-write` "keeps network access turned off unless you enable it in your configuration."
- Docs: https://learn.chatgpt.com/docs/permissions. Extending `:workspace` "keeps the workspace root's `.git`, `.agents`, `.codex`, and `.aws` paths read-only unless you explicitly override those rules." It shows the syntax `[permissions.<name>]`, `extends`, the `filesystem` rules, and `network.enabled`.
- `codex-rs/protocol/src/permissions.rs:860-871`: `append_default_read_only_project_root_subpath_if_no_explicit_rule(&mut entries, ".git")`, also `.agents`, `.codex`, `.aws`.
- `codex-rs/protocol/src/permissions.rs:2365-2377`: a `.git` pointer file of a worktree makes its resolved gitdir read-only too.
- `codex-rs/protocol/src/permissions.rs:2502-2511`: an explicit rule on the same path skips the default read-only rule. This is why the profile in run 3 works.
- `codex-rs/core/src/agent/child_config.rs:175-200`: a child copies the sandbox and the cwd of the parent turn.

### Runs

Local `gh` is logged in. `gh auth status` showed `✓ Logged in to github.com account bkwon94 (keyring)`.

Run 1 used plain `workspace-write`. The command is in section 2.

```
1. `pwd` — Exit code: `0`. First line: `.../codex-agent/repo/.claude/worktrees/spec-01`
2. `echo built > built.txt` — Exit code: `0`. No output.
3. `git add built.txt` — Exit code: `128`. First line: `fatal: Unable to create '.../repo/.git/worktrees/spec-01/index.lock': Operation not permitted`
4. `git commit -m 'run1 commit'` — Exit code: `128`. (same error)
5. `gh auth status` — Exit code: `1`. First line: `github.com`
6. `curl -sS -o /dev/null -w '%{http_code}' https://api.github.com` — Exit code: `6`. First line: `curl: (6) Could not resolve host: api.github.com`
```

Run 2 used `workspace-write`, `--add-dir` on `.git`, and the network on:

```
$ codex exec -C "$WT" -s workspace-write --add-dir "$D/repo/.git" -c sandbox_workspace_write.network_access=true \
    -m gpt-6.1-sol -c model_reasoning_effort='"low"' --ephemeral -o $D/run2.last.txt "... 1) echo built > built.txt \
    2) git add built.txt 3) git commit -m 'run2 commit' 4) gh auth status 5) gh api repos/openai/codex --jq .full_name"
exit=0
sandbox: workspace-write [workdir, /tmp, $TMPDIR, .../codex-agent/repo/.git] (network access enabled)
1. `echo built > built.txt` — Exit code: `0`. First line: no output.
2. `git add built.txt` — Exit code: `128`. First line: `fatal: Unable to create '.../repo/.git/worktrees/spec-01/index.lock': Operation not permitted`
3. `git commit -m 'run2 commit'` — Exit code: `128`. (same error)
4. `gh auth status` — Exit code: `0`. First line: `github.com`
5. `gh api repos/openai/codex --jq .full_name` — Exit code: `0`. First line: `openai/codex`
```

Run 3 used a permission profile passed with `-c`. Here `$G` is `$D/repo/.git`.

```
$ codex exec -C "$WT" -c 'default_permissions="builder"' \
    -c "permissions={builder={extends=\":workspace\", filesystem={\"$G\"=\"write\", \"$G/worktrees/spec-01\"=\"write\", \
        \":workspace_roots\"={\".\"=\"write\", \".git\"=\"write\"}}, network={enabled=true}}}" \
    -m gpt-6.1-sol -c model_reasoning_effort='"low"' --ephemeral -o $D/run3.last.txt "... 1) echo built > built.txt \
    2) git add built.txt 3) git commit -m 'run3 commit' 4) gh api repos/openai/codex --jq .full_name 5) touch $D/outside.txt"
exit=0
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR] (network access enabled)
1. Exit code: `0`. No output.
2. Exit code: `0`. No output.
3. Exit code: `0`. First line: `[spec-01 81fbb35] run3 commit`
4. Exit code: `0`. First line: `openai/codex`
5. Exit code: `0`. No output.

$ git -C "$WT" log --oneline
81fbb35 run3 commit
a76ad8b init
```

Step 5 proves nothing about the limits of the sandbox. The path is under `/private/tmp`, and the sandbox always lets the agent write in `/tmp`. The 4thandgoal worktrees are under the repo, not `/tmp`.

Run 3 did not test a write to the gitdir of a different worktree. In 4thandgoal each worktree has its own gitdir under `.git/worktrees/<name>`, and the objects and refs go in `.git`. The grant on all of `<repo>/.git` covers each worktree. Note that this grant also lets the agent write to the refs of `main`. The rule of ADR 0019 then depends on the prompt and the prek hook, not on the sandbox.

## What this means for the spec

### The Judge and the ticket builders use `spawn_agent`

The main Codex session runs `$4ag-implement`. It starts each ticket builder and the Judge with its `spawn_agent` tool. This matches decision 01: a fresh agent in the same harness. The facts force no change to decision 01. They add the four rules below.

1. **Say `fork_turns: "none"` in words.** The default forks the full history. The neutral text in `judge.md` and `build.md` must say: "Start the agent with no history of this session. In Codex, call `spawn_agent` with `fork_turns` set to `none`." This is the Codex form of "never use `fork`".
2. **Name the model and the effort.** The Judge brief says: in Codex, `model` is `gpt-6-astra` and `reasoning_effort` is `high`. In Claude it stays `model: opus`. A ticket builder can inherit the model of the parent, as in Claude today. Decision 04, the neutral tool words, must carry this pair per harness.
3. **Name the worktree in the brief.** A child inherits the cwd of the parent. Each builder brief must give the absolute path of its ticket worktree and say "Run each command with that path, as `git -C <path>` or `cd <path> && ...`." The briefs in `build.md` already name the worktree. Check that the text does not lean on a cwd.
4. **Close each child.** Six children is the cap on open threads, and a completed child counts until `close_agent`. A frontier with more than six tickets must start them in batches, or close each child after its merge. Note this in `build.md`.

### The session must run with a profile that allows `.git` and the network

A child inherits the sandbox of the parent, and the skill cannot change it. The plain `workspace-write` sandbox blocks `git commit` and `gh`. So the spec needs a Codex permission profile for this repo. The flow is:

- The repo ships a project config `.codex/config.toml` with a profile, for example `4ag`. The profile extends `:workspace`, grants `write` on the repo `.git`, and sets `network.enabled = true`. It also sets `approval_policy = "never"`. Decision 02 or a new decision must confirm that Codex loads a project `.codex/config.toml`, and how it treats a trusted project.
- Brian starts Codex at the repo root with that profile. `$4ag-implement` checks it in "Before you start". It runs `git -C <spec worktree> commit --allow-empty --dry-run` or a similar read, and stops with the name of the profile if the sandbox blocks `.git`.
- The profile must grant write on the full `.git`, which includes the refs of `main`. ADR 0019 then rests on the prompt and the prek hook. The spec should state this, or add a `deny` rule on `.git/refs/heads/main` if Codex allows it. A test is open.

### `codex exec` stays a fallback

A new `codex exec` process also gives a fresh agent. Use it only if a spec needs a Judge outside the session. The form is:

```
codex exec -C <spec worktree> -m gpt-6-astra -c model_reasoning_effort='"high"' \
  -c 'default_permissions="4ag"' --ephemeral -o <scratchpad>/judge.last.txt - < <brief file>
```

The parent reads `VERDICTS.md` from the worktree and the last message from the `-o` file. The parent must not trust the exit code, because it is 0 even when a command inside fails. The Judge writes only `VERDICTS.md`, so a profile without `.git` write is enough for it. The commit of `VERDICTS.md` stays with the parent, as in `judge.md` today.

### Open items for the spec

- No run used `gpt-6-astra` or a full-history fork in an interactive session. Both are cheap to test in the proof run of decision 01, item 7.
- `codex exec --json` gives no event for `spawn_agent`. The Judge evidence of the child model comes from the brief and the source only.
- Each run printed hook and MCP errors from the user config. They did not stop a run. `--ignore-user-config` may cut them and the token cost for a `codex exec` fallback. This research did not test it.
