# Notes for 05: How large are the Sleeper avatars?

Ticket: `.scratch/card-polish/decisions/05-research-avatar-size.md`. Measured 2026-11-07. No manager names or usernames appear here. Teams are roster ids.

## Verdict (facts only)

No team has a 800px source, and Sleeper serves none. The largest source is 400x400, for custom uploads only.

- A 400px picture is sharp at 1x for 8 of 24 teams (5 in cpc, 3 in norcal). It is soft at 2x for those 8.
- The other 16 teams top out at 168px (full size) or 192px (default image). The pipeline stores 80px.
- A sharp 400px picture is not possible for every team of both clients. A sharp 800px picture is possible for none.
- The headshot files are 350x254, so they are not square and not a team picture.

## 1. Published file sizes

Command: `sips -g pixelWidth -g pixelHeight <file>` on every file under `clients/<slug>/published/2026/week-08/avatars/`. Headshots: a sample of 4 per client.

| Client | Roster ids at 400px | Roster ids at 168 or 192px | Roster ids at 80px |
| --- | --- | --- | --- |
| cpc | 1, 5, 6, 7, 12 | 2 (192, default), 8 (168, default), 11 (168, default) | 3, 4, 9, 10 |
| norcal | 7, 11, 12 | none | 1, 3, 4, 5, 6, 8, 9, 10 |

- cpc has 12 avatar files. norcal has 11 files, because roster 2 has no avatar.
- Headshots: all 8 sampled files are `350 x 254` PNG. Counts: cpc 21 files, norcal 17 files.

## 2. Where the pipeline gets avatars

- `packages/league/python/src/league/parse.py` lines 25 to 36. The constant `AVATAR_THUMB_URL = "https://sleepercdn.com/avatars/thumbs/{avatar}"`.
- `_avatar_url` returns `user.metadata.avatar` first. Sleeper puts the full custom URL there, for example `https://sleepercdn.com/uploads/<file>.jpg`.
- Otherwise `_avatar_url` returns the thumb URL for `user.avatar`. Otherwise it returns `None`.
- The pipeline never builds the full-size URL `https://sleepercdn.com/avatars/<id>`.
- `packages/week/python/src/week/page.py` lines 190 to 203 (`_download_avatars`) saves the URL bytes as `avatars/<roster_id>.<ext>`. A `None` URL or a failed download uses the default image `images/avatar-default.svg`.
- Headshots: `packages/league/python/src/league/player_ids.py` lines 17 and 18. Forms: `https://sleepercdn.com/content/nfl/players/<id>.jpg` and `https://sleepercdn.com/images/team_logos/nfl/<id>.png`.

URL forms in `clients/<slug>/published/2026/managers.json` (`team.avatar_url`):

| Form | cpc | norcal |
| --- | --- | --- |
| `/uploads/<file>.jpg` (custom) | 5 | 3 |
| `/avatars/thumbs/<id>` | 4 | 8 |
| `/images/v3` or `/images/v4/avatars/avatar_default_*.webp` (Sleeper default) | 3 | 0 |
| no avatar (`avatar_url` is null) | 0 | 1 |

## 3. Largest size Sleeper serves

Command: `curl -s -o <file> <url>`, then `sips`. Files in `/private/tmp/claude-503/avatar-probe/`. All HTTP 200.

| URL form | Result |
| --- | --- |
| `/avatars/thumbs/<id>` (3 ids) | 80 x 80 |
| `/avatars/<id>` (same 3 ids) | 168 x 168 |
| `/uploads/<file>.jpg` (3 files) | 400 x 400 |

- Sleeper API docs, https://docs.sleeper.com/#avatars: "There are thumbnail and full-size images for each avatar." The docs give the two URL forms and no pixel sizes. The sizes above are measured, not documented.
- The sizes match the published files: thumb 80, default image 168 or 192, upload 400.
- Not checked: whether `/uploads/` serves an original larger than 400. The 3 files fetched are all 400, and so are all 8 published uploads.

## Consequence for the spec

If the Index list must show one sharp 400px picture for any team, the avatar cannot do it. The ticket names the fallback: a different large picture, such as the grid panel of the hero look.
