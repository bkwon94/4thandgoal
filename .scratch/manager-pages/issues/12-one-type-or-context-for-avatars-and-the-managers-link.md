# 12: One type or a context for the avatars and the managers link

**What to build:** `avatars` and `managersHref` travel together through `AllMatchups`, `Trades`, `PowerRankings`, `Standings`, and each inner `Row`, `Side`, or `TradeCard`. One link change touched eight files. Cut the number of files a link change touches.

**Blocked by:** none

**Status:** done

- [ ] Compare two options: one type that holds both values, or a React context that holds both.
- [ ] Pick the option with the smaller diff and fewer props. Say why in the commit message.
- [ ] `Moves` on the manager page also takes `managers` and `managersHref`. Include it in the check.
- [ ] No change in the rendered HTML. `pnpm check:export` still passes.
- [ ] The tests pass with no change to what they read.

## Comments

- 2026-10-31: closed by modular site ticket 05. The link format lives in one place, `managerHrefFrom` in the routes module, and the hand-built join in the week parts is gone. `managersHref` stays a string prop: a function cannot cross into a client component, and a shared type or a context would change seven files for no fewer props. `Moves` calls the same helper.
