# 04: The analyzer form per tier

**What to build:** A league member on a tablet or a laptop opens the trade analyzer, enters the passphrase, and sees the form in a white card with My team on the left and The other team on the right. Each team's player list sits under its own picker. The grade button spans both columns, and the grading status, the error line, and the retry button sit under it across both columns. The loading rows, the rate limit line, and the failed fetch line render inside the same card. The heading reads "Pick the Teams". On a phone the form is one column with both pickers before both lists, as today. The passphrase dialog is unchanged. The trade finder, when its flag is on, sits under the form across both columns. The result, when a grade is done, renders under the form.

**Blocked by:** 01 (The page shell and the card look on every page)

**Status:** done

- [x] The form and every state of the fetch render inside one chapter, so from the tablet tier they sit in one white card on the grey body.
- [x] From the tablet tier the two pickers and the two lists sit in a two-column grid: the pickers in row one, the lists in row two, each team in its own column. The document order stays picker, picker, list, list.
- [x] On a phone the form is one column in the same order as today.
- [x] The grade button, the grading status, the error line, and the retry button span both columns.
- [x] The finder, when its flag is on, sits under the form across both columns.
- [x] The heading reads "Pick the Teams". The finder heading is title case too.
- [x] The passphrase dialog, the team picker, and the player list are unchanged beyond their placement.
- [x] The analyzer test checks both pickers before both lists in document order and the grade button after the lists, and every state of the form as today.
- [x] A browser check at 768 and 1280, after a passphrase, shows the two columns with a team picked on each side and the lists under the pickers. At 390 the form is unchanged.
- [x] `pnpm test`, `pnpm typecheck`, and `pnpm build` pass.

## Comments

Closes as done in the audit of `todoist-queue` on 2026-11-12. The work merged in 230ba6e8.
Proof: The commit "Put the analyzer form in one chapter with two team columns" merged in 69c1c4af and 6486cff5.
Read 1 file: .scratch/todoist-queue/audit.md.
