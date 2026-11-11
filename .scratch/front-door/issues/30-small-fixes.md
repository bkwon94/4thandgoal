# 30: Two small fixes of the preview round

Spec: `.scratch/front-door/PRD.md`. Source: the small fixes of `.handoff/front-door-preview-testing.md` and the H17 preview check.

**App:** API

**What to build:**

1. Weak spots shows the depth word "fine" next to "hole" for a starter who cannot play now, for example "QB fine · hole: Lamar Jackson". A position row with a hole never reads "fine". The depth word comes from the grade; a hole now wins.
2. A trade turn of the chat context (`apps/site/src/app/front-door/chat-turns.ts`, `tradeFact`, and the API `chat_turns.py`) carries only its lean or offer count. It now carries the two sides: who gives whom.

**Blocked by:** 29

**Status:** done

- [x] The QB row of Bo Girds reads a depth word other than "fine" while Lamar Jackson is a hole.
- [x] A trade turn in the chat context names the players of each side.

## Comments
- Closes with the squash merge of the spec PR.
