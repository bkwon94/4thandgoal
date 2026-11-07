# 09: How Brian places six spots each week

Map: `.scratch/easter-eggs/MAP.md`.

**Kind:** grill

**Blocked by:** 01

**Status:** done

## Question

Brian places six spots for each Tuesday egg drop. Decide the shape of `eggs.toml`, the make target that sends it to the API, and how the egg drop joins the Tuesday publish, so the eggs go live with the week page. Decide what happens when a spot sits on a page that the publish of that week makes.

Brian set a rule on 2026-11-06: no agent finalizes an egg without his confirmation. An agent may propose spots, but Brian confirms each one before it goes into `eggs.toml` or the API.

## Decision

Brian decided in the grill of 2026-11-06.

The order of each Tuesday:

1. `make build CLIENT=cpc WEEK=N` builds the week, as now.
2. `make egg-draft CLIENT=cpc WEEK=N` runs an agent. It reads the catalog of ticket 01, the survey notes, the new week page in the build folder, and the eggs that dropped before. It proposes six spots, each with a reason, and spreads them across the catalog so no spot repeats.
3. Brian keeps, changes, or rejects each spot. Only a confirmed spot can drop.
4. `make publish CLIENT=cpc WEEK=N` publishes and pushes the week, then sends the confirmed eggs to the API as its last step. If the API is down, the publish warns, and `make egg-drop CLIENT=cpc WEEK=N` retries. With no confirmed eggs, the publish drops none and says so.

The file is `~/cpc-eggs/2026.toml` on the laptop of Brian, outside the public repo. The API keeps every egg that dropped, and Fly snapshots its volume each day, so a lost laptop loses only the draft of one week.

The new week page of a drop may hold more than one of its eggs, so managers read and use the whole page. No cap is fixed: Brian sets the mix of each week when he confirms the draft. For a few minutes after the drop, an egg can point to a page that the site deploy has not put online yet. That does no harm.
