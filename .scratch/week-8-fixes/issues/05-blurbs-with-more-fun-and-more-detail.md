# 05: Blurbs with more fun and more detail

Spec: `.scratch/week-8-fixes/PRD.md`, part 5.

**What to build:** The chapter blurbs read flat. Loosen the voice inside the tone rules, and ask for one more
concrete detail per blurb: the number, the player, or the turn that made the chapter. Use the facts ticket 03
found where they fit.

**Blocked by:** 03.

**Status:** ready-for-agent

- [x] Read the tone rules in `.scratch/tone/PRD.md` and the writer prompt. Name what you change and what you keep.
  - Changed: rule 30, the tone Humor bullet, the rule 29 game-time line, the verifier gate, and the two-number code check.
  - Kept: rules 1 to 29, the opener, the banned words and phrases, the number rules, and the examples.
- [x] The prompt asks for one concrete detail per blurb and allows a light joke where the facts earn it.
- [x] The word bans and the number rules stay. A test shows that.
- [x] `make build WEEK=8` from the saved data. Paste three blurbs, before and after, in the close comment.
- [ ] Brian reads the page before the publish.
- [x] `make check` passes.
