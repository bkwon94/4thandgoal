# 15: The prompts folder comes from the config

**What to build:** Every prompt read goes through the league config. Today `load_prompt` in the writer reads the packaged prompts with `importlib.resources`, and the verifier, the analysis, the finder reasons, and the research call it. The config holds `prompts_dir`, and nothing reads it. Thread the path from the config into `load_prompt` through the parameters the callers already hold. Ticket 02 left this out because the change touches about eighteen files.

**Blocked by:** 02

**Status:** done

- [ ] `grep -rn "resources.files" src/` finds nothing. Every prompt read takes its folder from the config.
- [ ] A test builds a config with a different prompts folder and sees the writer read a prompt from it.
- [ ] The four golden tests pass with no golden change.
- [ ] `make typecheck` passes.

## Comments

- 2026-11-01: merged into `modular` from branch `modular-15-prompts`, commits 24b1b10, ca79dc0, and 24e4c84. 1,510 tests collected. `load_prompt` takes the folder; the writer and the verifier take `prompts_dir` keyword-only; the analysis and the finder read it through the snapshot's config. Fourteen files, not eighteen. Two reviewers passed it after one fix pass.
