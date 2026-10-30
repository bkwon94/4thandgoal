# 03: The routes, the index, the hero, and the menu

**What to build:** a reader opens `/<season>/managers/` and sees the twelve teams in standings order, each a link. A team's page opens with the hero: the avatar, the team name, the owner, the record, and the standing. Under the hero, the three numbers: the grade reads "—" until ticket 04, the playoff odds with the change since last week, the power rank with its move. The menu shows "Managers" when the file exists. A desktop shows the chapter rail with the five chapters, each an empty chapter with its heading. Site repo.

**Blocked by:** 02 The managers file and publish

**Status:** done

- [x] The loader reads the managers file for the latest season, checks the schema version loud, and joins each entry with the last rankings week for the odds, the rank, and their changes.
- [x] With no managers file the routes do not build, the menu has no "Managers" entry, and nothing fails.
- [x] The odds change is none when the week before has no odds. The odds read "—" when no week has odds.
- [x] The index shows twelve cards in standings order with the avatar, the name, the owner, and the record. A card is one link.
- [x] The hero reads the report's look at every tier. One quiet line of context under each number. No third line.
- [x] The loader tests, the page tests, and the masthead test pass. Fixtures are built in the test.
- [x] `pnpm test`, `pnpm typecheck`, `pnpm build`, and `pnpm check:export` pass.
