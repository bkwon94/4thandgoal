# 26: The check reads what the personal facts mean, and a miss keeps the data block

Spec: `.scratch/front-door/PRD.md`. Source: H17 of `.scratch/front-door/HANDS-ON.md`.

**App:** API and site

**What to build:** "how can i improve my roster" routes to weak spots. Claude wrote true sentences, but the Jev check failed them twice, and the site dropped the whole Answer.

1. The meanings of `can_play_now`, `hole`, and `weak_starting_slots` live only in the Claude instructions (`personal_wording.py:19-22`). The check state holds only the raw slice (`personal_topics.py:224`). One `FACT_MEANINGS` dict now feeds both the instructions and the check state, so they cannot drift.
2. Each weak slot is a string such as "QB: Fernando Mendoza (QB50)". The slice now gives each weak slot a row: `slot`, `player`, `position`, `projected_rank_at_position`, `can_play_now`. The waiver `team_need` keeps its string.
3. The API logs each sentence that fails the check, with its noul.
4. On an honest miss of a personal Topic, the site keeps the data block. Only the text place shows the miss line.
5. A typed question that routes to a personal Topic reaches Claude and the check. Only a tap reads or keeps a stored Answer, so a typed question never gets the Answer of a tap or of another typed question.

**Blocked by:** 25

**Status:** in-review

- [x] The check state of a personal Topic holds the fact meanings, from the same dict as the instructions.
- [x] `weak_starting_slots` in the weak spots slice is a list of rows.
- [x] A failed check logs each failed sentence and its noul.
- [x] A personal Topic that ends as a miss still shows its data block.
- [x] Live: weak spots for Bo Girds passes the check on the first text in at least 4 of 5 runs.
- [x] A typed question reaches the prompt and the check question of its personal Topic, and reads no stored Answer.
