# 07: The staged reveal

Spec: `.scratch/analyzer-stage/PRD.md`. Acceptance tests AT-10, AT-11, AT-12, AT-13, AT-18, AT-20 at the reveal, and AT-24.

**App:** site

**What to build:** When the grade arrives, the mesh lines of the favored side flash once and fade in about 0.6 s. The mesh then dips toward the favored side and goes flat. A Gut call has no favored side, so the mesh settles flat with no dip. In about 1 s, the Lean word lands, the Lean scale fills, and the Case and the side tabs rise in. The Case uses the texts reveal recipe and the result cards use the skeleton reveal recipe of transitions.dev. Nothing adds a delay. With motion off, the reveal is a plain fade. The front door chat wait does not change.

**Blocked by:** 06

**Status:** ready-for-agent

- [x] On a cached repeat of trade T, the Lean word shows within 1.3 s of the response.
- [x] The time stamps show the Lean word, then the Lean scale, then the Case and the side tabs, within about 1 s.
- [x] A recording of the reveal shows the flash and the dip toward the favored side of trade T.
- [x] With reduced motion on, the mesh stays still in the wait and the result appears in a plain fade.
- [x] Each analyzer hero text reaches 4.5:1 or more at the end of the reveal, in `cpc` and `norcal`.
- [x] The full floor passes in `cpc` and `norcal`.
- [x] The front door chat wait shows no mesh and no stage line.
