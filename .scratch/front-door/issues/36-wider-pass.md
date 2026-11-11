# 36: A search with no offers runs a wider pass, so every trade ask gives an idea

Spec: `.scratch/front-door/PRD.md`. Source: H15, H18, H21 of `.scratch/front-door/HANDS-ON.md`.

**App:** analyzer and API

**What to build:** "what can i get for kenneth walker" and "id rather not trade a WR" built 0 offers, because the target question found no player on any partner. Ticket 35 shows ideas only when the search builds offers. When a search builds 0 offers, it now runs one wider pass: each partner offers its best player at the asker's need (or near the anchor's value for an anchored search), with the limit of ticket 31 kept. The pick ranks those as ideas with reasons, through the near ideas of ticket 35.

**Blocked by:** 35

**Status:** in-progress
