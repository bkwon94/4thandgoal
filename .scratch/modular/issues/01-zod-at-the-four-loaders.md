# 01: Zod at the four loaders

**What to build:** Each of the four loaders parses its published file with a Zod schema. The version check stays first, with its message. The type files re-export the inferred types under the names components use today, so no component changes. One test parses every file under the public folder with its schema. A shape change from the pipeline then fails the site test, not just the version check.

**Blocked by:** None (can start immediately)

**Status:** done

- [ ] Four schemas, one per published file, in a schemas folder under lib.
- [ ] Every exported type in the type files is an inferred type, and its name is unchanged.
- [ ] A test parses every `page.json`, `waiver.json`, `rankings.json`, and `managers.json` under the public folder. It fails with the file name and the path of the bad field.
- [ ] `pnpm typecheck`, `pnpm test`, and `pnpm check:export` pass. `out/` has no diff against `main`.

## Comments

- 2026-10-31: merged into `main` from branch `modular-01-zod`, commits 9b8f94e and 1de9723. 493 tests. The export matches `main` apart from the build id. Two reviewers passed it after one fix pass for lost comments.
