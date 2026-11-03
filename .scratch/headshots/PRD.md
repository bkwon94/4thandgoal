# Headshots on the awards, the leader boards, and the Game Changer

Status: ready-for-agent
Date: 2026-10-20
Glossary: `GLOSSARY.md`, see **Headshot**.
Branch: stacks on `page-feedback-week-7`.

## Problem Statement

The page names players as text only. A reader scans the Awards tiles, the Position Leaders
boards, and the Game Changer hero and sees no faces. Team avatars already give the matchup
cards an identity; the player sections lack it.

## Solution

Every player on an award tile, a leader row, or the Game Changer hero gets a headshot. The
build fetches each headshot from the Sleeper image CDN, saves it next to the team avatars, and
falls back to a default silhouette when the CDN has none. A DEF shows its NFL team logo.

## User Stories

1. As a reader, I want a headshot on each award tile, so that the winner has a face.
2. As a reader, I want a headshot on each leader row, so that I can scan the boards by face.
3. As a reader, I want a large headshot on the Game Changer hero, so that the section reads as a feature.
4. As a reader, I want a DEF row or tile to show the NFL team logo, so that a defense reads like the other rows.
5. As a reader, I want a silhouette when a headshot is missing, so that the layout holds and no broken image shows.
6. As the commissioner, I want the build to fetch headshots once per page and save them with the site, so that the page does not hotlink to Sleeper.
7. As the commissioner, I want a failed fetch to log a warning and go on, so that one missing image never stops the Tuesday build.
8. As the commissioner, I want the default test suite to run with no network, so that the fake fetch hook covers headshots the same as avatars.
9. As a reader on a phone at 390px, I want every leader row to hold on one line with the headshot in place, so that nothing wraps.
10. As a reader, I want the headshot sizes to follow the page scale, so that the three sizes look like one system.
11. As the commissioner, I want trade cards and matchup top scorers unchanged, so that this change stays in the three sections.

## Implementation Decisions

- A headshot URL comes from the player ID: `https://sleepercdn.com/content/nfl/players/{player_id}.jpg`. For a DEF line the player ID is the team abbreviation, and the URL is `https://sleepercdn.com/images/team_logos/nfl/{abbreviation lowercase}.png`. The CDN serves a 350 by 254 PNG on a white background under the `.jpg` name.
- The render step fetches each needed headshot through the same `fetch_bytes` hook the team avatars use, saves it under `headshots/` in the week directory as `{player_id}.png`, and records the page-relative path. A failed fetch or a non-200 gives the default path `static/headshot-default.svg`, a new static file. The fetch set is the players on the award tiles, the leader rows, and the Game Changer, with no duplicates.
- The render context carries a `headshots` map from player ID to path. The template reads it in the three sections through one macro, the same as the `av` macro for teams.
- Markup: an `img.headshot` with `alt=""`, `loading="lazy"` on the leader rows, inside the tile, the hero, and the row. The hero size is large, the tile medium, the row small, on the existing size scale with no new tokens. Rows stay one line at 390px.
- No change to the writer, the facts, the verifier, or the trade and matchup sections.

## Testing Decisions

- The render seam only. Prior art: `tests/test_render.py`, which calls `render_week` with a fake `fetch_bytes` and asserts on the HTML and the files on disk.
- Tests: the context has a headshot path for every player on a tile, a row, and the hero; a DEF uses the team logo URL; a fetch that returns `None` gives the default path; the three sections carry `img.headshot`; the fetch set has no duplicate URLs; the file lands under `headshots/`.
- The suite runs with no network.

## Out of Scope

- Headshots on trade cards, matchup cards, the MOTW section, or the bench regret lines.
- A resize or a crop of the CDN image.
- Any change to the writer or the facts.

## Further Notes

- About 20 images at 26 KB each, so about 500 KB per page. Acceptable for a weekly page.
- The design pass renders the real week 6 from the saved `facts.json` and `blurbs.json` on disk, with no writer call.
