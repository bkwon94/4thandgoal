# 06: The `parts/`, `shell/`, `analyzer/`, and `fixtures/` folders

**What to build:** The shared parts leave the week folder into a parts folder, one file per part: chapter, label, tag, blurb, avatar, team name, who, headshot. The avatar lookup by roster id moves beside the avatar helper under lib. The masthead, the menu, the theme button, and the compact bar move into a shell folder. The analyzer, the trade form, the trade side, the trade finder, the analyze result, the team picker, the passphrase dialog, and the teams skeleton move into an analyzer folder. Every fixture moves into one fixtures folder, typed by the schemas. A folder names a layer or a page, never a mix.

**Blocked by:** 05

**Status:** ready-for-agent

- [ ] No file under the week folder is imported from outside the week folder.
- [ ] The components folder has no loose file at its top level except `current-page.ts`, or that file has a folder too.
- [ ] Every fixture import points at the fixtures folder, and each fixture has a schema type.
- [ ] The diff is moves and import paths only. `out/` has no diff against `main`.
