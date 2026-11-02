# 02: `LeagueConfig` as a parameter

**What to build:** One frozen pydantic `LeagueConfig`, built from literals in a config module. It holds the slug, the display name, the provider name, the provider league id per season, the owner's username, the timezone, and the prompts folder. The CLI and the API entry build it once and pass it down. No module reads a global config. The league id leaves the orchestrator. `is_brian` becomes `is_owner`, and the username comes from the config.

**Blocked by:** 01

**Status:** done

- [ ] The literal league id, the owner's username, and the timezone exist in one module only. A grep for each finds the config, the tests, and the fixtures, and nothing else.
- [ ] Every function that needs a league value takes `config` or one field of it. No module-level config instance outside the entry points.
- [ ] The parser takes the owner's username from the config. `is_owner` replaces `is_brian` in the models and the tests.
- [ ] The API settings still read the passphrase from the environment.
- [ ] The four golden tests pass with no golden change.
- [ ] The module this ticket makes is in the `pyright` include list, and `make typecheck` passes.

## Comments

- 2026-10-31: merged into `modular` from branch `modular-02-config`, commits 69f5687, 0aa88d2, and a8f0014. 1,471 tests collected. Decisions: the wire name `is_brian` stays through a pydantic alias, so no published file changes; the nflverse kickoff zone stays a literal Eastern constant, because the feed gives kickoffs in Eastern time for every league; `prompts_dir` has no reader until ticket 15; `league_ids` is a tuple of pairs so the frozen model is really frozen. Two reviewers passed it after one fix pass.
