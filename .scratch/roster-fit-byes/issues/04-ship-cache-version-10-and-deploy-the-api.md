# 04: Ship: cache version 10 and deploy the API

**What to build:** Cached grades change, so the grade cache document version moves from 9 to 10. The
glossary, ADR 0004, the ADR 0003 marks, and the rubric prompt commit with the code on the feature
branch. Code review runs before merge. After merge, run the build check, then deploy the API. Brian
approved build and deploy with no confirm. One live grade of a week 8 trade with a player on bye in
week 10 shows no hole. This change reaches the API only. No weekly report rebuild.

**Blocked by:** 03, A middle team's player on bye this week is a hole.

**Status:** ready-for-agent

- [ ] The cache document version is 10.
- [ ] The glossary, both ADRs, and the rubric prompt are in the same commit set as the code.
- [ ] Code review passed and the branch merged to main without `--no-verify`.
- [ ] The build check passed before the deploy.
- [ ] The API deployed and serves the new document version.
- [ ] A live grade shows a later-week bye as no hole.
