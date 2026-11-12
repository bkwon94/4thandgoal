# 05: The Codex permission profile

Map: `.scratch/codex-flow/MAP.md`.

**Kind:** grill

**Blocked by:** 03

**Status:** done

## Question

Decision 03 found that the default Codex sandbox blocks `git commit` and the network. `4ag:implement` needs both. A permission profile with write on `.git` and the network fixed it, passed with `-c`. Brian decides two things:

1. Where the profile lives: the project `.codex/config.toml`, the user `~/.codex/config.toml`, or a flag that each run passes.
2. What keeps agents off `main`. The profile can also write the refs of `main`. ADR 0019 then rests on the skill text, the prek hook, and the GitHub rules, not on the sandbox.

## Decision

Brian decided both items in the grill of 2026-11-11.

1. **The place.** The profile `4ag` lives in the project `.codex/config.toml`, tracked in the repo. It extends `:workspace`, gives write on the repo `.git`, turns on the network, and sets approval to `never`. The repo then carries what its own skill needs, as `.claude/settings.json` does for Claude. `$4ag:implement` checks the profile in "Before you start" and stops with its name if the sandbox blocks a commit. The profile holds no secret.
2. **The wall on `main`.** The GitHub ruleset on `main` keeps agents off it: `verdict` is a required check, and the Repository admin role is on the bypass list so `publish` can still push. It stops a push to `main` from either harness. The ruleset is the hold in `docs/agents/state.md`. The spec gives it to Brian as a manual step, with the exact Settings values and a check, before the Codex proof run.

Not yet checked: Codex may load a project `.codex/config.toml` only for a trusted project. The spec checks it with a real run. If trust is needed, the trust step is one more manual step for Brian.

Facts found in the grill: the prek hook runs only `make check-fast`. No local hook blocks a commit on `main`.
