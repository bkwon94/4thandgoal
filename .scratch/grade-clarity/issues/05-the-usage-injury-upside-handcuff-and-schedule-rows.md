# 05: The usage, injury, upside, handcuff, and schedule rows

Spec: `.scratch/grade-clarity/PRD.md`. Acceptance tests AT-24, AT-25, AT-26, and AT-36.

**App:** pipeline

**What to build:** The other rows read as decision 03 says. Usage gives one clause for each player with the shares of the position. The injury row gives the return week and the weeks on the injury report. The upside row and the handcuff row use plain words. The schedule row names each playoff opponent with its rank at the position.

**Blocked by:** 04.

**Status:** ready-for-agent

- [ ] Usage gives the snap share, the target share, and the air yards per target for WR and TE, and the snap share, the carry share, and the target share for RB. QB gets no usage row. No week and no route share show.
- [ ] The injury row reads in the form "Cooper is out until week 11. He was on the injury report in 5 of 8 weeks."
- [ ] The handcuff row reads in the form "Spears backs up your RB, Pollard, on the Titans depth chart." The upside row reads in the form "Spears gets more work while Pollard is out."
- [ ] The schedule row names each playoff opponent with its rank in points allowed at the position, such as "TEN (3rd most points to WRs)". The sentence "The schedule leans for this side" is gone.
- [ ] `make check-fast` passes at the root.
