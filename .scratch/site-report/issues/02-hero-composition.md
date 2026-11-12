# 02: The hero composition

**What to build:** A league member on a tablet or a laptop sees the game changer as one picture: the label, the name, the position line, the points, and the projected line on the left, and the cutout on the red glow on the right, bottom-aligned and clipped to a hero of a token height. The blurb runs under both halves at the measure. The glow, the cutout, and the points keep their reveal delays. On a phone the hero is as it is today.

**Blocked by:** 01 The type scale, the measure, and the cards

**Status:** done

- [ ] From 640px the hero is two parts at a token height: text left, cutout right on the glow, bottom-aligned, clipped to the hero.
- [ ] The blurb runs under both parts at the measure.
- [ ] A long name and a short name give the same hero height.
- [ ] The three reveal parts keep their delays, and with motion off the hero shows at rest.
- [ ] Under 640px the hero is as it was.
- [ ] The game changer tests pass. The typecheck, the build, and the export check pass.
- [ ] Checked with agent-browser on the week 7 report at 390 by 844, 768 by 1024, and 1280 by 800 with reduced motion on. Screenshots as `02-hero-<width>.png` in the feature folder.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in 322dfbac.
Proof: The commit "Set the game changer hero in two parts from the tablet tier up" merged in 7d82a17e and 95d57c8d.
Read 1 file: .scratch/todoist-queue/audit.md.
