# Next week byes: who sits out, and the hit the team takes

Status: ready-for-agent
Date: 2026-10-28
Repos: the pipeline `cornerstone-fantasy-sleeper-weekly-report` and the site `cpcfantasyfootball`. The same PRD sits in both.
Glossary: **Key starter**, **Bye line**, **Bye cover**, **Position rank**, **Must Watch**, **Storyline**, **Reaction sentence** in the pipeline `GLOSSARY.md`.
ADRs: pipeline ADR 0006, a key starter reads real starts, not the best lineup. ADR 0004 still rules the trade analyzer's view of a bye.
Extends: `.scratch/next-week-storylines/PRD.md`. Follows: `.scratch/tone/PRD.md`.

## Problem Statement

The Next Week preview pairs the games and marks two Must Watch. It never says who sits out. A bye week
takes a quarterback or a top receiver off a roster for one game, and the manager finds out on Sunday
morning. Brian wants the preview to say, per team, who is on bye next week and what hit the team takes.
He wants it casual, with the roast on the roster build when the bench has no cover.

The report also reads too tame. The tone prompt counts jokes, and the writer meets the count and stops.
Brian wants the roast to run through the whole report, not to sit at one per blurb.

## Solution

Each game card in the Next Week preview gets a **bye line** under each team: every rostered player of
that team on bye next week, key starters first and in bold, with his position. A team with nobody on bye
gets no line. The Next Week blurb grows from 1 to 3 sentences to 2 to 6 and gains the bye facts, so the
writer can roast the team that loses two starters and has no cover at the slot. No new chapter.

A **key starter** is a player the team started in at least 3 of its last 4 completed weeks at QB, RB, WR,
or TE. The rule reads what the manager did, not the best lineup. A **bye cover** is the bench player with
the highest lineup value who can fill the slot a key starter on bye leaves open.

The tone prompt drops the count rules. Roast becomes the default register, wherever a fact invites it,
early or late in a blurb. The banned patterns stay. The verifier's accuracy rules do not change.

## User Stories

1. As a reader, I want each game card to name my players on bye next week, so that I set my lineup before Sunday.
2. As a reader, I want every rostered player on bye in the line, so that a bench player I forgot is there too.
3. As a reader, I want the key starters first and in bold, so that the real hit stands out from the bench names.
4. As a reader, I want each name with his position, so that I know which slot opens.
5. As a reader, I want full names as the Position Leaders show them, so that two players with one last name never blur.
6. As a reader, I want no line under a team with nobody on bye, so that the slate stays short.
7. As a reader, I want the line to wrap and never truncate, so that the fifth name is still there on a phone.
8. As a reader, I want the Next Week blurb to roast the team that loses the most, so that the preview is fun to read.
9. As a reader, I want the blurb to name the bench cover and his rank when a starter sits, so that I see what the team falls to.
10. As a reader, I want the blurb to say when a slot has no cover, so that the roast of the roster build has a fact behind it.
11. As a reader, I want the Must Watch tags and reasons kept, so that the preview loses nothing it has today.
12. As a reader, I want the preview blurb at 2 to 6 sentences, so that the byes fit beside the storylines without a wall of text.
13. As a league member, I want the roast throughout the report, so that every chapter reads like the group chat.
14. As a league member, I want no joke count, so that the writer stops at natural and not at one.
15. As a league member, I want the team name as the punchline where it fits, so that the roast lands on the manager and not the player.
16. As a league member, I want no joke about an injury itself, so that the humor never costs a person.
17. As a manager, I want a start in the FLEX slot to count as a start, so that my flexed back is a key starter too.
18. As a manager, I want a player I added this week to be in the line but not a key starter, so that the roast is about my habits and not my new add.
19. As a manager, I want a kicker or a defense in the line but never a key starter, so that a streamer on bye is not called a hit.
20. As a manager, I want the bar to drop to 2 of 3 and then 2 of 2 early in the season, so that week 3 has key starters too.
21. As the commissioner, I want every claim in the blurb backed by a fact, so that the verifier can reject a made-up rank.
22. As the commissioner, I want one fact per player on bye with his position rank and his starts of 4, so that the writer can cite the hit.
23. As the commissioner, I want one fact per key starter's slot with the bye cover and his rank or "no cover", so that the roast of the bench has a number.
24. As the commissioner, I want one fact for a team with nobody on bye, so that the writer can roast the team that read the schedule.
25. As the commissioner, I want the bye facts in scope of the Next Week chapter only, so that a recap chapter never cites next week's bye.
26. As the commissioner, I want the bye line on the page to come from data and not from the writer, so that the names are always right.
27. As the commissioner, I want the key starter rule in the tunables, so that 3 of 4 is one edit.
28. As the commissioner, I want no bye lines and one log line when the schedule or the history is thin, so that the Tuesday build never fails on a bye.
29. As the commissioner, I want the page JSON shape to grow and never change what exists, so that an older week still renders.
30. As the commissioner, I want week 7 untouched on the live site, so that nobody reads a blurb that changed under him.
31. As Brian, I want to read the week 7 build on the local dev server, so that I judge the lines and the voice on real facts before the merge.
32. As Brian, I want the feature in the week 8 build with no manual step, so that the launchd job carries it.
33. As a reader on a phone at 390px, I want the bye line indented past the avatar like the "vs", so that the card reads as one block per team.
34. As a reader with reduced motion on, I want the card to reveal as today, so that nothing new moves.
35. As a reader in dark mode, I want the bold names readable on the grey card, so that the key starters stand out in both themes.

## Implementation Decisions

### Key starters and byes, in the pipeline

- **Bye source**: the nflverse games file gives each NFL team's bye week, as the schedule reader already
  does. A player's bye is his NFL team's bye. Next week is the page week plus one. A player with no NFL
  team, or an NFL team with no schedule row, has no bye.
- **Who is on bye**: every player on the roster at build time whose NFL team has its bye next week, at
  any position. The list orders key starters first, then the rest by position rank, then by name.
- **Key starter**: a player started in at least 3 of the team's last 4 completed weeks at QB, RB, WR, or
  TE. A start is a place in the starters list of the saved matchups of that week on that roster, FLEX
  included. The empty slot "0" is not a start. With fewer than 4 completed weeks the bar is 2 of 3, then
  2 of 2. With fewer than 2 completed weeks no player is a key starter. The counts are tunables.
- **The saved week grows**: the past week model keeps each roster's starters per week, read from the
  saved matchups file that already holds them. No new fetch and no change to the saved files.
- **Position rank**: the glossary's position rank, from the analyzer's snapshot of the saved week. The
  weekly build loads the snapshot from the files of the week, with no chart and no slow sources, since
  the rank table needs neither. One rank means one thing on the page.
- **Bye cover**: for each key starter on bye, the bench player with the highest lineup value who can
  fill his slot, by the lineup slots the best-lineup code already builds. A bench player can cover one
  slot only. A slot with no such bench player has no cover.
- **Where it lives**: the next-week facts of the league facts module, next to the storylines. The
  computed byes ride on the next-week game model as a per-side list, so the renderer reads them, as the
  storylines ride there for the facts.

### Facts, for the writer

- `NX.bye.<roster>.<pid>`: "Brock Purdy, QB4, is on bye in week 9 and started 4 of the last 4 for Lil
  Fridge." The rank through the number holder. A player with no position rank, such as a K or a DEF,
  reads without one.
- `NX.bye.<roster>.<pid>.cover`: "His slot falls to Spencer Rattler, QB27, with 9.8 a game." Or: "No
  bench player can fill his slot." One fact per key starter on bye, never for a bench player on bye.
- `NX.bye.<roster>.none`: "Nobody on Return of T Mac is on bye in week 9."
- The Next Week chapter's fact ids gain the `NX.bye.` facts. Its range becomes 2 to 6 sentences. The
  chapter brief gains one line: the byes next week are part of the preview. No required fact and no
  count rule on how many teams the prose names.
- Scope: the bye facts name the team and the players, so the scope teams and scope players of the
  chapter include them, as the storyline facts do.

### The page JSON

- Each side of a next-week game gains `byes`: a list of `{ player_id, name, position, key }` in the
  order above. An empty list for a team with nobody on bye. The schema version does not change: a new
  optional list breaks no reader, and the site treats a missing list as empty.

### The tone prompt

- The Humor section loses "Every blurb has at least one joke" and "Roast bad teams harder" as rules.
  It becomes voice guidance: roast is the default register of the group chat. Roast wherever a fact
  invites it, early in the blurb or late, as often as the facts allow. A record below .500, a bench
  with no cover, a benched star, and a team name that writes its own joke are all invitations.
- The banned patterns stay. The reaction sentence rules stay. The number rules stay. The verifier
  does not change for this.
- The week 7 build is the test. Brian reads every blurb on the local site before the merge.

### The site

- The game card renders a bye line under a side with a non-empty list: a small "Bye" tag, then the
  names with positions, key starters in bold, in the small mute text of the Must Watch reason, indented
  past the avatar like the "vs". The line wraps. A side with an empty or missing list renders as today.
- The week types gain the optional `byes` list on the next-week team. The fixture week JSON gains byes
  for the test.

### Thin data

- No schedule, no history, or fewer than 2 completed weeks: every side has an empty list, no bye
  facts are made, and the build logs one line that names the missing source. Nothing raises.

## Testing Decisions

A good test reads what a reader or the writer sees: the facts, the chapter, the page JSON, the
rendered card. No test reads a private helper, a class name, or the shape of a prompt string beyond
the one line the brief gains.

### Pipeline

- **Seam 1, the bundle** (the highest seam): `build_bundle` on the week 6 fixture with its history
  root. Tests assert the `NX.bye.` facts exist with the right text and numbers, that the Next Week
  chapter lists them, and that its range is 2 to 6. Prior art: the next-week storyline tests on the
  `hbundle` fixture in the sheet tests.
- **Seam 2, the key starter rule**: a pure function from a roster's starters per week to its key
  starters, tested with 4, 3, 2, and 1 completed weeks, a FLEX start, a new add, a K and a DEF.
  Prior art: the storyline unit tests in the league facts tests.
- **Seam 3, the page JSON**: the renderer writes `byes` on each side, key starters first, and an
  empty list for a team with nobody on bye. Prior art: the next-week render test.
- **Seam 4, thin data**: the bundle with no schedule and with one saved week gives empty lists, no
  bye facts, and no raise.
- The fixture history needs starters in its saved matchups. It has them already, since the saved
  files are copies of the raw matchups.

### Site

- **One seam, the rendered chapter**: the Next Week component with the fixture JSON. Tests read the
  "Bye" tag count, the names in the line, that a key starter is bold through its role or its text, and
  that a side with an empty list has no tag. Prior art: the Next Week component tests.

### The humor

- No automated test. The week 7 build on the local dev server is the test. Brian reads it.

## Out of Scope

- A full tone pass with approved example sentences and a rewrite of a past week. That is the next
  feature, like `.scratch/tone/`.
- A republish of week 7. The feature ships with the week 8 build.
- A change to the trade analyzer's view of a bye. ADR 0004 stands.
- Headshots in the bye line.
- A new chapter for the byes.
- A change to the verifier for humor.
- Byes in the Rankings chapter or the recaps.

## Further Notes

- The numbers from the real rosters, weeks 8 to 11: 25, 9, 24, and 27 rostered players on bye, of
  which 8, 3, 9, and 10 are key starters. In week 8 and week 11, 11 and 12 of the 12 teams have a
  player on bye. That is why the names are a data line and the prose is one blurb.
- Real roast material is in the data already: one team benched Marvin Harrison Jr. in all of the last 4
  weeks and he is on bye in week 8; one team has five players off in week 10, three of them key
  starters.
- The site's dev server writes an untracked `AGENTS.md`. Do not commit it. The publish command stages
  every file in the site repo, so nothing uncommitted may sit on its `main`.
- Other sessions work on both repos. Work in the worktrees under the scratchpad and merge to `main`
  from the main checkout with `--no-ff`.
