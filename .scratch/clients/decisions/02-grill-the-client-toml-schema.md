# 02: The sections and values of `client.toml`

Map: `.scratch/clients/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

What does `client.toml` hold? It replaces the League config (ADR 0022). The spec needs its sections: the league, the provider per season, the package list, the values of each package, the menu, the brand, and the copy. It also needs the rule for each value that the check reads, and the error when a value is missing. Decide which values sit in `client.toml` and which get their own file, as in One ADR-0009.

Decision 01 note: Decision 01 sets the package list: `league`, `facts`, and `design` are in every client, and `week`, `rankings`, `managers`, `waiver`, and `analyzer` are the choice. Each package owns a `tunables` module, and a client sets only the values that its README names. A client may also choose its AI service, as one value behind the Writer port. `config.py` moves into `league`, so decide what is left of it.

## Decision

Brian decided each item in the grill of 2026-11-03.

### The file for CPC

```toml
# clients/cpc/client.toml
# league, facts, and design are in every client, so the list omits them.
packages = ["week", "rankings", "managers", "analyzer"]
timezone = "America/New_York"
usage_code = "cpcfantasy"

# One table per season. The provider gives the sizes of each season.
[seasons.2026]
provider = "sleeper"
league_id = "1386167364424318976"

# Only the values that differ from the defaults in the package README.
[values.analyzer]
finder = false

# Each item names the home page or one package of the list. The order is the order of the menu.
[menu]
layout = "hamburger"
items = [
  { page = "home", label = "Home" },
  { package = "week" },                       # the label "Week N" comes from the week package
  { package = "rankings", label = "Power Rankings" },
  { package = "managers", label = "Managers" },
  { package = "analyzer", label = "Trade Analyzer" },
]
```

The deploy of CPC today sets neither `NEXT_PUBLIC_WAIVER` nor `NEXT_PUBLIC_FINDER`. So the list omits `waiver`, and `finder` is false, and the golden diff stays empty.

### The choices and the reasons

1. **The sizes come from the provider.** The adapter maps the provider settings of each season into a kernel model in `league`. The code derives the lines, the strength rank, and the star ranks from the roster slots and the team count. A typed size can disagree with the league and give no error. Each derived value must equal the CPC value of the League config today.
2. **The owner goes away.** `owner_username`, `is_owner`, and the published key `is_brian` have no reader. The CPC golden diff allows that one removed key in each team of each `page.json`.
3. **`display_name` goes away.** It has no reader. The site name goes into `copy.toml` (ADR 0022).
4. **The site values follow one rule.** A value that changes with the league goes into `client.toml`. A value that changes with the deploy stays an env value of the app.
   - `NEXT_PUBLIC_WAIVER` becomes `waiver` in the package list.
   - `NEXT_PUBLIC_FINDER` becomes the `finder` value of `analyzer`.
   - `NEXT_PUBLIC_SEASON` is derived: the latest season in `client.toml`.
   - `NEXT_PUBLIC_USAGE_CODE` becomes `usage_code`. It is optional, and with none the site loads no count script.
   - `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_BASE_PATH` stay env values of the site app.
5. **One schema per package.** Each package defines its values as one pydantic model. A step exports it as a JSON Schema file into the package, and the site build checks `client.toml` against that file with a validator such as `ajv`. The check fails if an exported file is stale. Two schemas per package give two sources of truth. A checked `client.json` makes the site build run Python.
6. **Required and default values.** The seasons, with the provider and the league id of each, the timezone, and the package list are required. Each package value has a default that its README names. An unknown key fails the check.
7. **The menu is a closed set.** Each item names the home page or one package of the list. An item sets only its label and its place. An item for a package that the client omits fails the check.

### Gone from the League config

- The sizes: they come from the provider.
- `owner_username` and `display_name`: no reader.
- `prompts_dir`: it is the fixed folder `prompts/` of the client.
- `seller_gap` and `shootout_top`: they move into the `tunables` of `analyzer` and `week`.
