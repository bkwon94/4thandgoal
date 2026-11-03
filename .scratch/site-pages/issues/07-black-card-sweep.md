# 07: Sweep the comments for the glossary words

**What to build:** The glossary renamed "Black card" to "Dark chapter". It says "card" names only the look of a chapter from the tablet tier. About 20 comments still say "black card". Most are in `src/app/globals.css`, `src/components/rankings/power-rankings.tsx`, `src/components/waiver/player-sheet.tsx`, and `src/components/waiver/war-chest.tsx`. The terms "swap card", "finder cards", and "grey card" in the analyzer also clash with the rule. ADR 0007 keeps its text, because an ADR is a record.

**Blocked by:** None

**Status:** triage

- [ ] Decide the new words for the analyzer terms with Brian.
- [ ] Change each "black card" comment to "dark chapter".
- [ ] Change the analyzer terms to the agreed words.
- [ ] Leave ADR 0007 as it is.
- [ ] `pnpm typecheck` and `pnpm test` pass.
