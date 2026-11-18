# 01: Which Jev wording routes site questions right

Map: `.scratch/site-answer/MAP.md`.

**Kind:** prototype

**Blocked by:** none

**Status:** done

## Question

The route needs a new Jev Noul, "the question asks about the site itself", and a Jev Choice over the Menu items of the client. Which wording of the two routes about 30 real questions right, in the style of front-door decision 09?

The set holds the three shapes: "where is the trade analyzer", "what tools are there", and "how do I use the sim". It also holds the traps, which must keep their old route: "where is my team in the standings", "what's the trade market like", "take me through week 10", and "who has the best roster". The spec needs the wording, the cutoffs, and the place of the new row in the route table of `decide()` in `apps/api/src/cornerstone_api/ask.py`.

Run the prototype on the live Jev. Record the score of each wording, then delete the prototype code.

## Decision

Brian, 2026-11-18, after the prototype ran the live Jev route on 40 questions with `jev-1.14.0`, in 3 runs. 3 questions are real, from Brian. 37 are written by Claude. 22 are site questions, and 18 are traps that must keep their old route. Questions 35 to 40 were held out while the wordings were tuned.

1. **The Noul is `n5`.** Instructions: "Does `manager_question` ask for a page or tool of the site, by its name or by what it does?" Yes: "The manager names a page or tool in `site_pages` as the thing they want, or asks where one is, which ones the site has, or how to use one." No: "The manager asks for a fact, a judgment, or advice about the league or its teams, or asks for something unrelated to the site." It routed 21 of 22 site questions to `site` and kept 18 of 18 traps. It quotes no test question, so its score is not fit to the set. Four other wordings scored 16 to 21 of 22.
2. **The Choice is `c1`.** "Which page in `site_pages` does the manager ask about in `manager_question`?" The options are the `site_pages` lines plus `none`: "No one page: the manager asks about the whole site, or about a page that is not in `site_pages`." It picked the right page 66 of 66 times.
3. **The state gets a `site_pages` field.** It maps each page key of the client to one line about the page. The keys for cpc are `home`, `week`, `rankings`, `managers`, `analyzer`, and `midseason`.
4. **The row order is A.** After `ABUSE`, a clear yes on the site Noul routes to `site`. Then the old table runs. Order B, where a Topic wins first, sent "take me to the weekly reports" to the week recap.
5. **Only a yes above 0.7 routes to `site`.** An unsure score falls through to the old table. So "how do i set my lineup", a question about Sleeper at 0.51 to 0.56, never routes to `site`.
6. **A Topic wins over a bare page name that is also a Topic.** "power rankings?" and "show me the power rankings" stay with the power rankings Topic, whose Answer links to its page.
7. **A page the client lacks routes to `site` with `none`.** The answer shows the full list. "is there a waiver page" does this for cpc, which has no waiver page.
8. **A sim question points to the midseason report.** The sim has no page and no Menu link of its own.

What the prototype also showed, for the spec:
- Today, "where is the trade analyzer" and "what tools are there" are an honest miss. "take me to the weekly reports" goes to the week recap, and "what can this site do" goes to a free answer.
- The `site_pages` field moves the old route of 5 of 40 questions. Order A catches 4 of them first. The fifth, "who won the midseason awards", moves from a miss to a free answer, which is a better route.
- "where are the playoff odds" overlaps a Topic and the sim. `n5` scored it 0.39, so it keeps its Topic.
- One request grows from 2894 to 3448 input tokens, so +554.
- The page list comes from `[menu].front_door_items` in `clients/<slug>/client.toml`, plus `midseason`. cpc has no `waiver` package, and the sim and the egg board have no Menu link.

The prototype code was never in the repo. A copy for the spec sits in the session scratchpad, outside the repo, with the question set, the runner, and the raw scores of each run.
