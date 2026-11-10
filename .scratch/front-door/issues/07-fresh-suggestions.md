# 07: Urgent Suggestions, the head start, and stale Answers

Spec: `.scratch/front-door/PRD.md`. Acceptance tests AT-6, AT-8, AT-34, AT-35.

**App:** both

**What to build:** The API serves the Suggestions of Your team. Jev lifts a Topic above the order of the day when its fact makes it urgent. On open, the API builds the Answer of the top Suggestion when it is a personal Topic. The site asks the API whether the key of each Answer in the Thread is still current. A stale Answer shows dimmed with "Your roster changed since <day>. [Refresh]", and Refresh gets a fresh Answer.

**Blocked by:** 03, 06

**Status:** ready-for-agent

- [ ] A lift Noul above 0.7 puts its Topic first (AT-6).
- [ ] The top personal Suggestion opens at once after 30 s, and the log shows the build on open (AT-8).
- [ ] A roster change dims the weak spots Answer with the stale line and no "checked" mark (AT-34).
- [ ] Refresh streams a fresh Answer with "checked" (AT-35).
