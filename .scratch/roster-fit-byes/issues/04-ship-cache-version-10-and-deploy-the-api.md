# 04: Ship: cache version 10 and deploy the API

**What to build:** Cached grades change, so the grade cache document version moves from 9 to 10. The
glossary, ADR 0004, the ADR 0003 marks, and the rubric prompt commit with the code on the feature
branch. Code review runs before merge. After merge, run the build check, then deploy the API. Brian
approved build and deploy with no confirm. One live grade of a week 8 trade with a player on bye in
week 10 shows no hole. This change reaches the API only. No weekly report rebuild.

**Blocked by:** 03, A middle team's player on bye this week is a hole.

**Status:** done

- [x] The cache document version is 10.
- [x] The glossary, both ADRs, and the rubric prompt are in the same commit set as the code.
- [x] Code review passed and the branch merged to main without `--no-verify`.
- [x] The build check passed before the deploy.
- [x] The API deployed and serves the new document version.
- [x] A live grade shows a later-week bye as no hole.

## Comments

2026-10-27 evening. Merged as 03cc522 and pushed. `fly deploy` ran from that commit and the machine
reached a good state. `/health` is ok. The live grade ran on the local API at the same commit against
live Sleeper data, since the production passphrase is not in the session: roster 6 gets Luther Burden
for Parker Washington in week 8, and roster fit reads "It gets the highest-value player in the trade,
and the best lineup does not lose." No hole for his week 10 bye. The site repo's copy of the find
fixture is one trade behind; follow-up.
