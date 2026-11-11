# 22: The chat context of each typed question

Spec: `.scratch/front-door/PRD.md`. Source: H11 of `.scratch/front-door/HANDS-ON.md`.

**App:** site, API

**What to build:** Each typed question carries the turns of its Thread: the question and the final shown answer text of each earlier turn, oldest first and newest last, with no data block, tool result, or step line. A hard limit of about 8,000 tokens, 32,000 characters, drops the oldest turns first. The router reads the turns in the Jev state, so a follow-up such as "cant choose mine" routes like the whole question. Claude reads them as earlier messages in the free answer and in a typed personal Topic, with the Anthropic cache mark on the last turn. The Jev check judges each claim against the tool results only. A tapped Topic carries no turns and keeps its kept Answer (AT-8).

**Blocked by:** 03, 05, 06

**Status:** done

- [x] The site sends the turns of the Thread, newest last, and cuts the oldest past the limit.
- [x] The API cuts a longer list from the oldest end, and each turn is plain text under its cap.
- [x] The route puts the turns in the Jev state.
- [x] Claude reads the turns as earlier messages, with a cache mark on the last turn.
- [x] The Jev check never reads the turns.
- [x] A tapped personal Topic sends no turns and keeps its key and its kept Answer.
- [x] On a local API, as CPC roster 6, "cant choose mine" after "who has the best roster" names the best other team.

## Comments
- Closes with the squash merge of the spec PR.
