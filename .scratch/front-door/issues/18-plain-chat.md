# 18: The Thread as a plain chat

Spec: `.scratch/front-door/PRD.md`. Acceptance tests AT-30, AT-31. Source: H7 of `.scratch/front-door/HANDS-ON.md`.

**App:** site

**What to build:** The Thread works like a plain chat. Each question and its Answer stay in the scroll exactly as they rendered: the question bubble, the card or the text, the data block, the check mark, and the links. Nothing folds. The manager scrolls up to reread. A new question scrolls to its top under the Thread header, and the sticky head and the sticky dock stay. An older Answer plays no entrance and no stream again. Under reduced motion, only the fades stay.

**Blocked by:** 03, 11

**Status:** done

- [x] After 3 questions, each of the 3 Answers is in the DOM in full, with its card or text, and none is folded (AT-30).
- [x] A new question scrolls to its top under the Thread header, and the older Answers stay in place (AT-31).
- [x] A kept Thread loads whole after a closed tab, and each older Answer shows at rest.
- [x] The code of the fold is gone: the fold line, the one open fold, and the flat body of an opened fold.
- [ ] PRD line 24, stories 38 and 39, line 223, AT-30, and AT-31 change to the plain chat with the commissioner.

## Comments
- Closes with the squash merge of the spec PR.
