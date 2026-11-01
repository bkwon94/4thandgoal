# 10: Type clash renames

**What to build:** Every type name means one thing. The trade form `Pick` becomes `PlayerPick`. The trade side `Destination` becomes `SideChoice`. The analyzer `TradeSide` type comes from the API schema, and the week `TradeSide` stays its own type from the week schema. The `Team` in the API client comes from the teams schema. No shapes merge across files.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] No exported type name is defined in two modules. A grep per name proves it.
- [ ] The `TradeSide` component keeps its name, and its props type is named for the component.
- [ ] `pnpm typecheck` and `pnpm test` pass. `out/` has no diff against `main`.
