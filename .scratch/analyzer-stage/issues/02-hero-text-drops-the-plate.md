# 02: Hero text drops the plate, and the glow moves low

Spec: `.scratch/analyzer-stage/PRD.md`. Acceptance tests AT-17, AT-18, AT-19, AT-21, and AT-25.

**App:** site

**What to build:** No hero text has a dark box behind it. The `plate` utility leaves the site with every use: the hero slots, the week hero, the manager hero, the grade dial, the grade popover, the midseason opener, the 404 page, the egg banner, and the analyzer result. Its padding and negative margin go with it. The glow of the static hero art becomes `radial-gradient(ellipse 38% 46% at 100% 112%, var(--color-accent-glow), transparent 70%)`, from the prototype of decision 05. The egg banner takes the same glow. Each comment that says a text sits on a plate changes to say why the text needs none (ADR 0036).

**Blocked by:** 01

**Status:** done

- [x] No file of the site uses the `plate` utility, and the utility is gone.
- [x] The pixel scan gives 4.5:1 or more for each hero text in `cpc` and `norcal`, at 390 and 1280 px, and the floor passes.
- [x] The score 106.71 of the week 9 hero of `cpc` reaches 4.5:1 or more.
- [ ] Each text of the egg banner reaches 4.5:1 or more with eggs on.
- [x] The hero scene of the week hero keeps its own row.
- [x] A polish pass checks the rhythm of each changed hero by eye, at 375, 768, and 1280 px.

## Comments

The merge: `1e49bdd9` merged into `analyzer-stage` on 2026-11-16; review fixes `a8f2b48d` and `4eb5bef2`; Judge fix round `7b1d09c7`.
The proof: `make check-fast` passed at each merge, the full check passed on 2026-11-17, and the Judge gave PASS to AT-1 to AT-34 after one fix round.
Read at least 5 files: AGENTS.md, apps/site/AGENTS.md, .scratch/analyzer-stage/PRD.md, .scratch/analyzer-stage/ACCEPTANCE.md, .scratch/analyzer-stage/issues/02-hero-text-drops-the-plate.md.
Closes with the squash merge of the spec PR.
