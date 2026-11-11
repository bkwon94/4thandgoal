# 41: Claude picks a block by the shape of the answer, not the words of the ask

Spec: `.scratch/front-door/PRD.md`. Source: H28 of `.scratch/front-door/HANDS-ON.md`.

**App:** API

**What to build:** a block shows only for exact asks.

1. The router sends "can you compare my roster to Teehee" to How you stack up, which reads one team and has no blocks. A comparison of the asker's team with a named team now routes to the free answer. How you stack up keeps "how do I stack up" and "how good is my team".
2. The free answer rules name 3 narrow cases. They now name the shape: an answer that ranks 3 or more players or teams uses a list; an answer that sets 2 teams or 2 players side by side uses a table; an answer about one player uses a player card; anything else is text.
3. "my top players" with no time reads as this season, and the lead says "this season".

A block eval holds at least 15 phrasings, 5 per kind, plus 5 that stay text. The bar is 17 of 20.

**Blocked by:** 40

**Status:** in-progress
