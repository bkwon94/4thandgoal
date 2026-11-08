# 05: How large are the Sleeper avatars?

Map: `.scratch/card-polish/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

The Index list shows one large picture of the chosen team, about 400px wide. The site has Sleeper avatars and headshots in `published/<season>/week-NN/avatars/`. Find the pixel size of the files we publish and of the largest size Sleeper serves. If no avatar is sharp at that size, the spec needs a different large picture, such as the grid panel of the hero look.

## Decision

The large picture of the Index list is not the team avatar. The facts decide it, from the notes at `decisions/05-research-avatar-size.notes.md`, measured on 2026-11-07.

- Sleeper serves 400px at most, and only for a custom upload. 8 of 24 teams have one. Those 8 are soft at 2x.
- The other 16 teams top out at 168px or 192px, and the pipeline stores 80px for most of them. One team has no avatar.
- The headshots are 350x254, so they are not a team picture.

Ticket 07 chooses what fills the large picture, in the prototype. The ticket names the panel of the hero look as the first try. The avatar can still sit small inside that panel.
