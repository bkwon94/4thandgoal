# 05: The Codex permission profile

Map: `.scratch/codex-flow/MAP.md`.

**Kind:** grill

**Blocked by:** 03

**Status:** open

## Question

Decision 03 found that the default Codex sandbox blocks `git commit` and the network. `4ag:implement` needs both. A permission profile with write on `.git` and the network fixed it, passed with `-c`. Brian decides two things:

1. Where the profile lives: the project `.codex/config.toml`, the user `~/.codex/config.toml`, or a flag that each run passes.
2. What keeps agents off `main`. The profile can also write the refs of `main`. ADR 0019 then rests on the skill text, the prek hook, and the GitHub rules, not on the sandbox.

## Decision

None yet.
