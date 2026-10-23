# 07: The research step

Spec: `.scratch/waiver/PRD.md`.

**What to build:** Every ranked player in best adds, trending, sneaky, and stashes, up to
`RESEARCH_PLAYERS` (32), carries up to `CLAIMS_PER_PLAYER` (2) research claims: one sentence each with
a source URL, a source name, a date, and whether the claim backs or disputes the engine's facts. The
claims live in the saved facts as a fact family with the URL in the fact, and the verifier treats a
sentence with a URL as cited. A rewrite reads the saved claims. When the search fails for every
player, the file carries a missing-experts flag and the build completes.

Start with a research task into `.scratch/waiver/research.md`: which Yahoo Fantasy waiver columns,
feeds, and podcasts carry the three writers Brian follows there, with real URLs, and what the
Claude web search tool costs per call today. The prompt then names those sources first, then the
wider web, and asks only for takes and news from the last 7 days.

The research module takes the search call as a parameter. The search call is one Claude call per
player with the web search tool. A claim with no URL is dropped.

**Blocked by:** 02 Usage and environment.

**Status:** ready-for-agent

- [ ] `research.md` names the real Yahoo sources and the search cost per call with the price page URL and the date.
- [ ] A fake search call that returns a claim with no URL leaves that claim out.
- [ ] The per-player cap and the player cap hold.
- [ ] A failure for one player leaves the other players' claims in place.
- [ ] A failure for every player sets the missing-experts flag and the build completes.
- [ ] A claim sentence with a URL passes the verifier; the same sentence with no URL fails it.
- [ ] A claim with a banned word fails the code check as any blurb does.
- [ ] One prompt text test pins the source order and the 7-day rule.
- [ ] The research runs once per build after the engine, and a rewrite never calls the search.
- [ ] Glossary gains **Research claim**.
