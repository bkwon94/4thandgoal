# 07: Sweep the comments for the glossary words

**What to build:** The glossary renamed "Black card" to "Dark chapter". It says "card" names only the look of a chapter from the tablet tier. About 20 comments still say "black card". Most are in `src/app/globals.css`, `src/components/rankings/power-rankings.tsx`, `src/components/waiver/player-sheet.tsx`, and `src/components/waiver/war-chest.tsx`. The terms "swap card", "finder cards", and "grey card" in the analyzer also clash with the rule. ADR 0007 keeps its text, because an ADR is a record.

**Blocked by:** None

**Status:** wontfix

- [ ] Decide the new words for the analyzer terms with Brian.
- [ ] Change each "black card" comment to "dark chapter".
- [ ] Change the analyzer terms to the agreed words.
- [ ] Leave ADR 0007 as it is.
- [ ] `pnpm typecheck` and `pnpm test` pass.

## Comments

Closes as wontfix in the audit of `todoist-queue` on 2026-11-12.
Proof: `GLOSSARY.md` now lists "dark chapter" under _Avoid_ and defines "Swap card" as a term, so the rename this ticket asks for goes against the glossary; the three named component files are gone.
Read 1 file: .scratch/todoist-queue/audit.md.
