# 10: Type clash renames

**What to build:** Every type name means one thing. The trade form `Pick` becomes `PlayerPick`. The trade side `Destination` becomes `SideChoice`. The analyzer `TradeSide` type comes from the API schema, and the week `TradeSide` stays its own type from the week schema. The `Team` in the API client comes from the teams schema. No shapes merge across files.

**Blocked by:** 02

**Status:** done

- [x] No exported type name is defined in two modules, except where two schemas each own a type of that name, such as `Team` and `TradeSide`. A grep per name proves it.
- [ ] The `TradeSide` component keeps its name, and its props type is named for the component.
- [ ] `pnpm typecheck` and `pnpm test` pass. `out/` has no diff against `main`.

## Comments

- 2026-10-31: merged into `main` from branch `modular-10-type-renames`, commit 50775b7. The first criterion read too strictly: the PRD keeps one `Team` and one `TradeSide` per schema, so the criterion now says so. Two reviewers passed it.
