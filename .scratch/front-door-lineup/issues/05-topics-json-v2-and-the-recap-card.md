# 05: `topics.json` v2 and the recap card

Spec: `.scratch/front-door-lineup/PRD.md`. Acceptance tests AT-22, AT-23, AT-40.

**App:** both

**What to build:** The weekly build writes `topics.json` at `schema_version` 2, with an optional `block` field on each league Topic. Week recap gets the recap card: the score, the place, a strip with a mark for each team, the top scorer against his projection, and the first sentence of the recap. The strip has a median tick only in a league that plays the median. The site renders the recap card in the Ledger look.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] The week 9 build of cpc writes a recap `block` with 114.07, 3rd of 12, and a median of 103.51 (AT-22).
- [ ] The week 9 build of norcal writes a recap `block` with 155.38 against kaiedmonds and no median (AT-23).
- [ ] `schema_version` is 2 in both files (AT-40).
- [ ] Site screenshots show the recap card in both leagues, light and dark, at 375, 768, and 1280 px.
