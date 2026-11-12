# 04: The bye line in the game card

Spec: `.scratch/next-week-byes/site/PRD.md`, "The site", "The page JSON". Glossary: **Bye line**, **Key starter**.

**What to build:** Each side of a next-week game card with players on bye shows a bye line: a small "Bye"
tag, then every name with his position, key starters first and in bold, in the small mute text of the
Must Watch reason, indented past the avatar like the "vs". The line wraps and never truncates. A side with
an empty or missing list renders as today.

**Blocked by:** 01 in the pipeline tracker (the `byes` shape in the page JSON). The shape is `{ player_id, name, position, key }` per side.

**Status:** done

- [x] The week types gain an optional `byes` list on each side of a next-week game. A missing list reads as empty.
- [x] The card renders the bye line under a side with players on bye, in list order, with the "Bye" tag before the names. Title case for the tag.
- [x] A key starter's name is bold. The bold reads in both themes on the grey card.
- [x] The line is indented past the avatar, wraps at 390px, and never truncates.
- [x] A side with an empty list has no tag and no line. The Must Watch tag and reason render as today.
- [x] The fixture week JSON gains byes for at least two sides, one with a key starter and one with none. The tests read the tag count, the names, the bold key starter, and the absence on an empty side. No test reads a class name.
- [x] `pnpm test`, `pnpm typecheck`, `pnpm build`, and `pnpm check:export` pass.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in 15f11610.
Proof: "Merge next-week-byes: the bye subtitle in the next-week card" is on `main`, and every box is checked.
Read 1 file: .scratch/todoist-queue/audit.md.
