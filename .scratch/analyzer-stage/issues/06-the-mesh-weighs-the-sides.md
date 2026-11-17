# 06: The mesh weighs the sides

Spec: `.scratch/analyzer-stage/PRD.md`. Acceptance tests AT-3, AT-5, AT-15, AT-20 in the wait, and AT-23.

**App:** site

**What to build:** The pending grade button starts the wait of the mesh at once. A weight under each side pulls the mesh down in turn, 1.25 s per side, and a trade of three or more sides cycles through each side. Accent pulses, with a bright head and a soft tail, run along the mesh lines, bend with the mesh, and run faster near a weight that pulls. The stage lines of ticket 05 sit over the mesh. `Sweep` leaves the grade wait and stays in the Finder wait. The wait has no minimum time. With motion off, the mesh stays still.

**Blocked by:** 04, 05

**Status:** ready-for-agent

- [ ] Within 100 ms of the tap on "Grade the Trade", the mesh moves and "Weighing the sides" shows.
- [ ] A recording of 5 s of the wait shows a dip under the side of Bo Girds, then under the side of Teehee, about 1.25 s each.
- [ ] At 375 px with a 4x CPU slowdown, no frame of the wait takes longer than 50 ms after the first second.
- [ ] Each analyzer hero text reaches 4.5:1 or more over 10 samples in 3 s of the wait, in `cpc` and `norcal`, at 390 and 1280 px.
- [ ] The Finder wait of `norcal` shows the `Sweep` bar and no mesh.
- [ ] The design bar skills ran on the wait, and Brian checked it on his iPhone.
