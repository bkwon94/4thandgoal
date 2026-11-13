# 01: The type scale, the measure, and the cards

**What to build:** A league member on a tablet or a laptop reads the weekly report with type one size larger per tier and body text no wider than about 68 characters. Each chapter sits as a card on the grey body with an even gap, white or dark as the chapter is, with a square edge and no shadow. On a phone the report is as it is today: the print type scale and the unbroken white page with the chapter rules. The type scale, the measure, and the card gap are tokens.

**Blocked by:** None (can start immediately)

**Status:** done

- [ ] The type scale tokens, label through headline and the hero number, carry one value per tier. The body is 14px on a phone, 15px on a tablet, 16px on a desktop. The other sizes step with the print ratio kept.
- [ ] A measure token of about 68 characters caps every chapter blurb, the hero blurb, and the matchup recap. Tables, grids, and score rows take no cap.
- [ ] From 640px each chapter is a card with a token gap between chapters, and the chapter rule is gone. Dark chapters stay dark cards. The card edge is square, with no shadow and no radius.
- [ ] Under 640px the chapters, the rules, and the type are as they were.
- [ ] The existing tests pass. The typecheck, the build, and the export check pass.
- [ ] Checked with agent-browser on the week 7 report at 390 by 844, 768 by 1024, and 1280 by 800 with reduced motion on. No sideways scroll. Screenshots as `01-week7-<width>.png` in the feature folder.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in a6cd647d.
Proof: The commit "Step the type scale per tier, cap the blurbs, and set chapters as cards" merged in 95d57c8d on `main`.
Read 1 file: .scratch/todoist-queue/audit.md.
