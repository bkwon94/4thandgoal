# 11: The bench sentence and the odds change words

**What to build:** Two lines on the manager page use wording that does not match the rest of the site. Decide the wording with Brian, then change both lines.

**Blocked by:** none

**Status:** ready-for-human

- [ ] `BenchPoints` in `season-so-far.tsx` writes two sentences and speaks as "Your". The rest of the site writes about a team. Brian picks the new sentence.
- [ ] `changeWords` in `manager-hero.tsx` reads "up 5" for the odds and for the power rank alike, with no unit. Brian picks words that name the unit for each.
- [ ] The tests that read these lines change with them.
- [ ] Ask Brian before any edit. The wording is his decision.

## Comments

Stays open in the audit of `todoist-queue` on 2026-11-12, as ready-for-human. Brian kept it, because it fixes a real bug or changes what a manager sees.
Proof: `season-so-far.tsx` still writes two "Your" sentences and `changeWords` still writes "up 5"; the ticket says Brian picks the words.
Read 1 file: .scratch/todoist-queue/audit.md.
