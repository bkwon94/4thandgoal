# 17: Lower five modules to their PRD layer

**What to build:** Five modules sit one or two layers above where the PRD places them, because of one import each. The layer test marks each with a `# PRD:` note. Lower them so the note goes away: `history` and `snapshot` read facts modules; `season_inputs` holds a snapshot; `chart` calls the writer for the Claude read of the chart image; `live` imports `chart`. Candidate moves: `TREND_WEEKS` from `facts_league` into `tunables`; the position rank and trend helpers that the snapshot needs out of `facts_league` and `ranks` into a load-layer module; the Claude call out of `chart` behind a parameter the caller passes, so `chart` stays a provider.

**Blocked by:** 07

**Status:** done

- [ ] No `# PRD:` note remains in the layer map, or each one that remains has an ADR line that accepts it.
- [ ] The layer test passes. The four golden tests pass with no golden change.
- [ ] `make typecheck` passes.

## Comments

- 2026-11-01: merged into `modular` from branch `modular-17-lower-modules`, six commits fcd16e0 to 9434239 and the fix f4cd5cc. 1,511 tests collected. `TREND_WEEKS` lives in the tunables. `standings_table.py` in the load layer holds the standings functions the snapshot needs. `claude_errors.py` in the provider layer holds the two Claude error classes. `chart` takes the Claude call as a parameter through `claude_reader`. No `# PRD:` note remains. An independent graph script finds no upward edge. Two reviewers passed it after one fix pass.
