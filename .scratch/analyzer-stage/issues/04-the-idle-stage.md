# 04: The idle stage

Spec: `.scratch/analyzer-stage/PRD.md`. Acceptance tests AT-1, AT-2, AT-16, and AT-20 in idle.

**App:** site

**What to build:** The analyzer hero ground becomes a live mesh on a Canvas 2D, with no WebGL. Idle draws a calm, flat mesh at the 24 px pitch of the hero grid, with no pulses. The canvas draws its own glow low in the bottom-right corner, and cuts a soft hole in the mesh and the glow under each text block and each chip, deeper under a small muted label. Each player that the reader adds shows on the stage. The canvas pauses when the hero leaves the viewport or the tab hides. With motion off, the mesh is still. The build may start from the scrolltide items `mesh-flow` and `light-cove`, and rewrites them. Add the glossary term "Mesh" from the spec.

**Blocked by:** 02

**Status:** done

- [x] With an empty Stack, two screenshots 2 s apart show the same flat mesh.
- [x] After the add of Kenneth Walker III to the side of Bo Girds, the hero shows his name.
- [x] The canvas draws no frame while the hero is out of view, and none while the tab is hidden.
- [x] Each analyzer hero text reaches 4.5:1 or more in idle, in `cpc` and `norcal`, at 390 and 1280 px.
- [x] `GLOSSARY.md` defines "Mesh".
- [x] The design bar skills ran on the idle hero, and Brian checked it on his iPhone.

## Comments

- 2026-11-16: Brian checked the idle stage on his iPhone over the LAN dev server and said "its good".

The merge: `6638fcd1` merged into `analyzer-stage` on 2026-11-16; review fixes `a8f2b48d` and `4eb5bef2`; Judge fix round `7b1d09c7`.
The proof: `make check-fast` passed at each merge, the full check passed on 2026-11-17, and the Judge gave PASS to AT-1 to AT-34 after one fix round.
Read at least 5 files: AGENTS.md, apps/site/AGENTS.md, .scratch/analyzer-stage/PRD.md, .scratch/analyzer-stage/ACCEPTANCE.md, .scratch/analyzer-stage/issues/04-the-idle-stage.md.
Closes with the squash merge of the spec PR.
