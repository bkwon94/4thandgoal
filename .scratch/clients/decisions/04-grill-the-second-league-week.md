# 04: What the second league needs to build a week

Map: `.scratch/clients/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

What does the second league need to build a week? The CPC build reads the history of past seasons, the prompts and the voice of the writer, and league-sized limits in `tunables.py`. The second league has none of these yet. The spec needs the list of what a new client must supply, and what a build does when a part is missing.

## Decision

Brian decided each item in the grill of 2026-11-03.

### The second league

NorCal Redraft Apex #6, Sleeper league `1402948824305049600`, in its first season. It differs from CPC in four ways that the code meets:

| Setting | CPC | NorCal |
| --- | --- | --- |
| Reception points | 0.5 | 1.0 |
| Passing TD points | 4 | 6 |
| Median game | on | off |
| Roster slots | 2 FLEX, DEF, no K | 3 FLEX, no DEF, no K |

### The files for NorCal

```toml
# clients/norcal/client.toml
packages = ["week", "rankings", "managers", "analyzer"]
timezone = "America/New_York"

[seasons.2026]
provider = "sleeper"
league_id = "1402948824305049600"

[values.league]
chart = "1QB1.0PPR4pt"               # the closest chart; no 6-point passing TD chart exists

[values.analyzer]
finder = true

[menu]
layout = "bar"
```

```toml
# clients/norcal/brand.toml
radius_card = "4px"
radius_small = "2px"

[fonts]
body = 'system-ui, -apple-system, "Segoe UI", sans-serif'
heading = 'system-ui, -apple-system, "Segoe UI", sans-serif'

# No [light] table: one dark set, no theme button.
[dark]
accent = "#c2410c"             # burnt red-orange: the fills with white text
band = "#0a0a0a"
page = "#141414"
card = "#232323"
text = "#f5f0e6"
muted = "#a8a29a"

[dark.derived]
accent_text = "#e0a526"        # gold: the accent as text on the dark page
```

The site name in `copy.toml` is "NorCal Apex 6". NorCal has no logo, so the logo of a brand is optional, and the masthead then shows the site name as text. Each text pair of the brand passes WCAG AA: text on page 16.2, muted on card 6.2, gold on page 8.4, white on accent 5.2. Brian gave the palette as red, gold, orange, and mustard with dark greys and blacks. The spec may tune the values with the same contrast check.

### The choices and the reasons

1. **The chart is a package value of `league`.** `chart = "1QB1.0PPR4pt"` names the chart. The default is no chart, and then each chart value is 0, as the code does today for a week with no chart. A name derived from the scoring fails for NorCal, because no chart for 6-point passing touchdowns exists.
2. **The reception points choose the points key.** 0 gives `pts_std`, 0.5 gives `pts_half_ppr`, and 1 gives `pts_ppr`. Any other value fails the build with a plain message. Each key uses the Sleeper default of 4-point passing touchdowns, so each NorCal QB projection is 2 points low for each passing touchdown. The matchup scores stay exact.
3. **The League settings carry the median game.** It comes from `league_average_match`. Each package honors it when it moves: the standings and the odds count one game a week, the power form drops the median weight, the week has no Median Game chapter, and the managers points line has no median line. Each package ticket adds a test with the median off. Today 16 pipeline modules and 8 site files assume the median.
4. **The roster slots set the position lists.** A position with no slot, through a flex slot too, leaves the pool and the leaders. The ranked positions stay QB, RB, WR, and TE. `K` leaves the CPC pool, and the ticket proves with the golden diff that nothing changes.
5. **The returns file is one shared NFL file.** It sits outside each client folder, beside the other NFL data, and Brian keeps it. A return week is an NFL fact, the same in each league. The spec sets the path.
6. **The prompts split by kind.** Each rule prompt moves into the package that owns it: `writer` and `verifier` into `facts`, `analysis`, `finder`, and `rubric` into `analyzer`, and `research` into `waiver`. `tone.md` and `vocabulary.md` move into `facts` as the default voice. A client `prompts/` folder is optional and can override only those two files. The median text moves into the week package, and the build adds it only when the median game is on.
7. **NorCal takes four packages and differs at the second level.** NorCal takes the same list as CPC. It differs in its package values, with `finder = true`, and in its menu, with the layout `bar`. A test that builds a client with a short list, such as `week` only, proves the package level.

### What a build does when a part is missing

| Part | Source | When it is missing |
| --- | --- | --- |
| The history | Fetched from Sleeper | Never missing. The first season starts at week 1. |
| The sizes, the median game, and the positions | The League settings | Never missing. |
| The player points | The key from the reception points | An unknown value fails the build. |
| The chart | `chart` in `[values.league]` | Each chart value is 0. |
| The returns | The one shared NFL file | No player is due back. |
| The voice | `facts`, or `prompts/` of the client | The default voice. |
| The logo | `assets/` of the client | The masthead shows the site name as text. |
