# 05: What does the Announcement look like?

Map: `.scratch/season-sim/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** done

## Question

The Announcement introduces a new feature once per browser. It has art, a title, a line of text, a link to the feature, and a dismiss. It builds on the shared Sheet or on the Dialog of `packages/design`.

Build 2 or 3 different versions for Brian to choose from, with the sim as the first feature. Use ui-sdk and transitions-dev, and meet the design bar. Check each one on a phone. Record the choice and the base part, then delete the prototype code.

## Decision

Brian, 2026-11-18, after one round of 3 variants.

**Variant A, "Sheet", with 3 changes.** The Announcement is a bottom sheet on the shared `Sheet` of `packages/design`, with `initialFocus="content"`. A drag down, "Not now", Escape, or a tap on the dim closes it. From top to bottom it holds:

1. The art slot. For the sim, the art is a live preview: Your team's name and playoff odds, and the standings rows near Your team with the playoff line.
2. An eyebrow, "New: Season sim".
3. A title, "See your path to the playoffs".
4. One line, "Pick this week's results and watch your playoff odds move."
5. The link "Open the sim", the one solid red control.
6. "Not now".

The 3 changes from the prototype:

1. The preview shows 3 rows: the team above Your team, Your team, and the team below, with the playoff line.
2. The What-if chip ("What-if: <team> win both") is a real button. A tap turns it on or off, and the odds count to the new number.
3. The chip still turns on once by itself, but only after the sheet settles, so the manager sees the odds move.

The art slot belongs to the use. The next Announcement puts its own art there. The rest of the sheet is the general component.

**Why A.** A shows the feature itself: tap a result and the odds move. B, "Card", a ticket with a stub to tear, hid the value behind a gesture, and the tear does not carry over to a later Announcement. C, "Takeover", a full-screen extra edition, was too strong for a one-time note on page load. Its chart showed past odds, not the What-if.

**The first visit.** A new visitor sees the team picker first, so the Announcement skips that load. Brian keeps the rule of the map: it opens only on page load, and never while another sheet is open. It must show on the next load. So a skipped open is not "seen". Only a dismiss or a press of its link hides it for good.

**For the spec.**

- The art reads Your team. Brian did not decide what the Announcement does on a later load with no team set. The spec decides it.
- Pass the site name in as a prop. The prototype read `clientValues.copy.siteName` inside the component, which breaks ADR 0012.
- The prototype opened about 0.7 s after load, and skipped the open if another modal was open or the page was the link target.
- Use real sim numbers. The sample rows of the prototype put a lower place above a higher place in odds.
- Under reduced motion, the rows and the odds show at once, with no count and no automatic chip.

**The record.** The prototype files, 57 screenshots, the check script, and its output are in `~/plans/season-sim-prototype/announcement/`. The check passed in WebKit at 390x660, 810x980, 1080x740, and 1280x800, with motion and with reduced motion. The prototype code is deleted from the worktree.
