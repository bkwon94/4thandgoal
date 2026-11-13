# 10: The headshot strip stops short of the chip edge

**Repo:** `cpcfantasyfootball`

**What to fix:** In the swap card, the headshot image of each player chip is narrower than the chip, so a blank strip shows on the right. The two-side arrow card and the row-per-side card both show it, and the arrow card showed it before the multi-team feature. See `.scratch/analyzer-multi-team/screenshots/result-three-fix-1280.png`.

**Blocked by:** None (can start immediately)

**Status:** done

- [ ] The headshot fills the chip edge to edge in both cards
- [ ] A missing headshot keeps the fallback with no gap

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in 0a8b8868.
Proof: The site redesign (#11) rebuilt `PlayerChip` in `packages/analyzer/site/form/analyze-result.tsx` with `-mx-sp-2 -mt-sp-2 self-stretch` so the headshot fills the chip. No screenshot confirms the gap is gone.
Read 1 file: .scratch/todoist-queue/audit.md.
