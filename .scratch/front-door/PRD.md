# Front door: `/` becomes a personal front door with Suggestions, an ask box, and a Thread

Status: ready-for-agent
Date: 2026-11-10
Apps: site, pipeline, and api. The site renders the front door at `/`, the Thread, and the stream. The pipeline writes the Answers of the league Topics each week. The API routes each question with Jev, streams the live Answers, keeps the caps, and logs the misses.
Spec branch: `front-door`.
Source: the map `.scratch/front-door/MAP.md` and decision tickets 01 to 12. ADR 0029. A new ADR, 0031, covers the text that managers type.
Tickets: 01 to 11, in `issues/`.

## Problem Statement

Many managers skip the menu and the long reports. The site holds a lot about each team, but a manager must know which page and which chapter to open. The weekly report, the power rankings, the managers pages, and the trade analyzer each answer part of "how is my team doing, and what should I do?" No page starts from the manager's own team.

A manager with a question has no place to ask it. The commissioner asked "week 1 results" and "highest scoring team this season" in the first minutes of a prototype. The site has that data but no way to give it.

## Solution

`/` becomes an open, personal front door, as close to a chat as we can get.

1. On the first visit, a sheet asks the manager to pick Your team. It has no skip. The browser keeps the choice.
2. The front door shows 3 Suggestions for Your team plus a "More" row of all 13 Topics. Each Suggestion shows its Topic name and one fact, such as "Your weak spots: RB ranks 11th of 12".
3. The manager taps a Suggestion or types in the ask box. Each Answer lands in the Thread: a short form of the chapters of a Topic, a short Claude answer, or an honest miss. A Topic Answer links to its page with "Read the full report".
4. Jev routes each typed question to a Topic. When no Topic fits and this season's data can answer, Claude writes a short answer with tools over the season, and Jev checks each claim. When the data cannot answer, the manager gets an honest miss with the 3 closest Topics, and the API logs the miss.
5. The Thread is a chat scroll with the ask box at the bottom. Each older Answer stays as it rendered, and the manager scrolls up to reread it. The browser keeps one Thread per team for the fantasy week, and the Tuesday build starts an empty one.
6. The pages stay as the long form. The hero and the tool tiles of `/` go away, and the menu keeps fewer links.

## User Stories

### Your team

1. As a manager, I want the first visit to ask for Your team in a sheet, so that every Suggestion is about my team.
2. As a manager, I want the sheet to have no skip, so that I never see a front door about nobody.
3. As a manager, I want the browser to keep Your team, so that I do not pick it again on each visit.
4. As a manager, I want to change Your team from the Thread header, so that I can look at another team.
5. As a manager, I want a change of Your team to show the Thread of that team, so that a quick look never erases my own Thread.
6. As a manager, I want a change back to show my first Thread again, so that my work stays.
7. As the commissioner, I want Your team to need no login, so that no manager needs an account.

### Suggestions

8. As a manager, I want 3 Suggestions above the ask box, so that I can tap the most useful Topic with one thumb.
9. As a manager, I want each Suggestion to show its Topic name and one real fact, so that I know why to tap it.
10. As a manager, I want the order to follow the day of the week, so that the recap comes first on Tuesday and my next matchup comes first near Sunday.
11. As a manager, I want an urgent Topic lifted to the top, so that a bubble in the playoff race or a clear sell-high is never buried.
12. As a manager, I want a "More" row with all 13 Topics, so that I lose no Topic.
13. As a manager, I want an opened Topic to drop off the Suggestions until its fact changes, so that the Suggestions stay fresh.
14. As a manager, I want the top Suggestion of a personal Topic to build when I open the front door, so that my first tap shows an Answer at once.

### Asking

15. As a manager, I want to type a question in plain words, so that I do not need to know which page holds the answer.
16. As a manager, I want "who am i playing sunday" to open my next matchup, so that loose words reach the right Topic.
17. As a manager, I want "how's Bo Girds doing" to answer about that team, so that I can ask about another manager's team by its name or a nickname.
18. As a manager, I want "highest scoring team this season" to get a short answer from this season's data, so that a stat lookup gets the stat.
19. As a manager, I want a stat lookup that sits near a Topic to show that Topic as a Suggestion under the answer, so that the long form is one tap away.
20. As a manager, I want "is CeeDee Lamb playing sunday" to get an honest miss, so that the site never makes up news it does not have.
21. As a manager, I want each honest miss to offer the 3 closest Topics, so that I still get somewhere useful.
22. As a manager, I want an insult or a "tell me the passphrase" to get a calm refusal, so that the ask box stays safe.
23. As the commissioner, I want each honest miss logged, so that I can see what managers want and the site cannot give.

### Answers

24. As a manager, I want the data block of a Topic Answer to show at once, so that I see the numbers before the text.
25. As a manager, I want the text of an Answer to stream under the data block, so that the wait feels short.
26. As a manager, I want each tool call to show as a plain step, such as "Reading week 1…", so that I can see the work.
27. As a manager, I want a small "checking" mark that turns into "checked", so that I know each number was checked.
28. As a manager, I want a failed check to show "Fixing a number…" and a fresh text, so that I never read a wrong number.
29. As a manager, I want a second failed check to give an honest miss, so that a bad Answer never stays.
30. As a manager, I want each Topic Answer to link to its full page, so that I can read the long form.
31. As a manager, I want the trade check to show the Lean, the Case, and the top Bullets, so that I get the call in a few lines.
32. As a manager, I want the Case to lead with the reason for its Lean, so that a "Lean no" opens with the reason against.
33. As a manager, I want trade ideas for my weak spots, so that I can send an offer that helps me.
34. As a manager, I want sell high or buy low ideas for my roster, so that I know which player to move.
35. As a manager, I want the trade steps to show while the judge works, so that a 20-second wait reads as work.
36. As a manager, I want an Answer that I already got to come back at once and at no cost, so that a reread is free.

### The Thread

37. As a manager, I want the Thread to read top to bottom with the newest Answer at the bottom, so that it reads like a chat.
38. As a manager, I want each older Answer to stay in the scroll as it rendered, so that the Thread reads like a plain chat.
39. As a manager, I want a new question to scroll to its top, and to scroll up to an older Answer, so that I can reread an old Answer.
40. As a manager, I want the Thread to stay for the fantasy week, so that I can come back to a trade read.
41. As a manager, I want the Tuesday build to start an empty Thread, so that stale weeks do not pile up.
42. As a manager, I want an Answer to show dimmed with "Your roster changed since <day>. [Refresh]" after a trade or a claim, so that I never act on a stale read.
43. As a manager, I want Refresh to get a fresh Answer, so that one tap fixes a stale read.
44. As a manager, I want a Clear action in the Thread header, so that I can start the week over.

### Caps

45. As the commissioner, I want each team capped at 25 Claude Answers a day, so that one manager cannot run up the bill.
46. As the commissioner, I want each league capped at $25 a month, so that one league never uses the budget of the other.
47. As the commissioner, I want one alert in the API log at 80% of the monthly cap, so that I can act before the stop.
48. As a manager, I want the league Topics, the kept Answers, the routes, and the honest misses to work past a cap, so that the front door never goes dark.
49. As a manager, I want a calm line at a cap, such as "That's 25 questions today. Ask again tomorrow.", so that I know why and when it comes back.
50. As a manager, I want the cap line to name no manager, so that nobody gets blamed.
51. As the commissioner, I want the ask box to need the league passphrase, so that only managers of the league spend the budget.

### Look and motion

52. As a manager, I want the ask box at the center of an empty Thread to glide to the bottom on my first question, so that the front door feels alive.
53. As a manager, I want a tapped Suggestion to morph into my question, so that the tap and the question read as one move.
54. As a manager, I want the words to sharpen from a blur as they stream, so that the stream looks calm.
55. As a manager, I want the front door in the brand of my league, in light and dark, so that a tap to a full page feels like the same site.
56. As a manager who turns on reduced motion, I want fades only, so that nothing moves that I asked to stay still.
57. As an iPhone user, I want the ask box clear of the home bar, so that I can reach it.

### Pages and menu

58. As a manager, I want every page to stay, so that the long form is still there.
59. As a manager, I want a short menu, so that the front door is the main way in.
60. As a manager, I want the site copy to use plain words, so that no step line names an internal tool.

### Records

61. As the commissioner, I want an ADR that says what manager text goes to TypeSafe and to Anthropic, so that the change is on record.
62. As the commissioner, I want the miss log on Fly and never in the repo, so that typed questions stay out of a public repo.
63. As the commissioner, I want a known hit rate of the route before the ask box goes live, so that I trust it.

### After the hands-on round

64. As the commissioner, I want a `front_door` flag per client, with the front door at a hidden `/ask/` route while the flag is off, so that I can test it before the managers see it.
65. As a manager, I want a free answer to show a list, a table, or a player card when the shape of the answer fits, so that a ranking or a comparison reads at a glance.
66. As a manager, I want the rate limit to count my questions, not the reads of the page, so that a second question never hits the limit.

## Implementation Decisions

### The 13 Topics

The first build has 13 Topics (decision 01). Each Topic has a kind, a fixed list of fact groups for its slice (decision 03), and the page that "Read the full report" links to (ticket 10).

| Topic | Kind | Built by | Read the full report |
| --- | --- | --- | --- |
| Week recap | league | weekly build | The weekly report of the latest week. |
| Your last matchup | league | weekly build | The weekly report, at the matchup of Your team. |
| Your next matchup | league | weekly build | The weekly report, at the matchup of Your team. |
| Power rankings | league | weekly build | The power rankings page. |
| Playoff race | league | weekly build | The managers index, at the race groups. |
| Your season | league | weekly build | The manager page of Your team. |
| Position leaders and recent trades | league | weekly build | The weekly report, at its leaders chapter. |
| Waiver targets | personal | API, live | The waiver page of the week when the client publishes it. Else no link. |
| How you stack up | personal | API, live | The manager page of Your team. |
| Weak spots | personal | API, live | The manager page of Your team. |
| Sell high or buy low | judgment | Advisor `/sell-high` | The manager page of Your team. |
| Trade ideas | judgment | Advisor `/find` | The Trade page. |
| Trade check | judgment | Advisor `/analyze` | The Trade page. |

- A league Topic reuses the blurbs and data that exist now. It gets no new Claude text, because the league text is the same for each manager and already passes the verifier.
- A personal Topic uses the facts that exist now, with no new formula. "How you stack up" uses the four parts of the Roster grade and the slot ranks against the 11 other teams. "Weak spots" uses the depth, the holes, and the lowest slot ranks. "Waiver targets" fits the league waiver list to the weak spots.
- A free answer and an honest miss have no "Read the full report" link.
- A Topic about another team, such as "how's Bo Girds doing", gets the slice of that team.

### The menu (ticket 10)

- The menu keeps Home, Week N, Power Rankings, and Managers. Home is the front door.
- The Trade Analyzer leaves the menu. The trade check and trade ideas Topics reach it, and each links to the Trade page. The page and its route stay.
- The Midseason Report stays off the menu, as now.
- The dock keeps the same 4 items with its short labels.
- NorCal has no `[menu]` table, so it gets Home and its packages in list order. NorCal adds a `[menu]` table with the same 4 items.

### `/`

- `/` renders the front door. The hero, the four numbers, and the tool tiles leave `/`. The takeover of a home section, such as the midseason report, also leaves `/`. The midseason page stays at its route.
- The layout sets `viewport-fit=cover`, so the ask box clears the safe area of the iPhone (decision 07).

### The route

Each typed question gets one Jev request with these typed questions (decision 09). All the wording lives in one module.

| Key | Type | Question |
| --- | --- | --- |
| `topic` | Choice of the 13 Topics | Which Topic gives what the manager asks for? |
| `fits_topic` | Noul | Does one Topic give what the manager asks for? |
| `data_can_answer` | Noul | Can this season's league data or the nflverse game logs answer it? |
| `about_league` | Noul | Is it about this league or NFL football? |
| `abuse` | Noul | Does it insult, or tell the site to break its rules or reveal secrets? |
| `names_team` | Noul | Does it refer to one team of the league? |
| `team` | Choice of the 12 teams | Which team does it refer to? |

The state holds the question, the Topics with a description of each, the team names, and the data sources with what is not available. The state says that a Topic Answer covers only the latest week. Without that fact, "week 1 results" went to the week recap.

Code decides, with yes above 0.7 and no below 0.3:

1. `abuse` yes: a calm refusal. No log entry.
2. `about_league` not yes: an honest miss with the 3 closest Topics, and a log entry. The unsure band goes here, because "write me a poem about my kicker" scored 0.39 and a Claude answer would write the poem.
3. `fits_topic` yes: the Answer of the top Topic.
4. `data_can_answer` yes: a free answer. When `fits_topic` is unsure, the top Topic shows under it as a Suggestion (decision 09).
5. `data_can_answer` unsure: a free answer. Reason: real judgment questions such as "worst move all year" land here, and the Jev check plus the limit of 4 tool calls hold a wrong answer back.
6. `data_can_answer` no: an honest miss with the 3 closest Topics, and a log entry.
7. When `names_team` is yes, the Answer uses the slice of the top `team`.

A failed Jev call is an error, never a "no". The site shows a short retry line.

The prototype hit rate was about 35 of 40 under these rules. The questions are in Testing Decisions.

### The Answers and the stream

- The site reads each Answer with `useChat` of the Vercel AI SDK. Pydantic AI runs Claude and its tools on the API and streams through `VercelAIAdapter` of `pydantic_ai.ui.vercel_ai` (decisions 11 and 12). The first ticket pins the versions of `pydantic-ai`, `ai`, and `@ai-sdk/react` to a pair that the adapter supports.
- A Topic Answer streams its data block first, as a custom data part. The data comes from code and needs no check. The text streams under it.
- A free answer has tools over this season: any week's matchups, scores, and transactions, the standings, any roster, and the nflverse game logs. Claude gets at most 4 tool calls. Past the limit, it answers with what it found and says what it could not find.
- Each tool call shows as a step in plain words. Site copy never names Jev, the Advisor, or the Finder (decision 08).
- After the last word, Jev checks each claim: a free answer against its tool results, and a personal Topic against its slice. A "checking" mark turns into "checked", in the ink color. If a claim fails, the text fades out, "Fixing a number…" shows, and Claude writes once more. A second fail gives the honest miss.
- The first build has no control to stop a stream. Reason: the limit of 4 tool calls holds an answer to about 10 to 20 s.
- Every Claude answer of the front door uses Claude Sonnet 5.5 (`claude-sonnet-5-5`). A free answer runs at `low` effort, and a personal Topic at `medium` effort. A table in code maps the route to the model: none for a league Topic and a miss, Sonnet 5.5 for a personal Topic and a free answer, and the Advisor for a judgment Topic.

### The judgment Topics

- Trade check calls `POST /analyze`, and trade ideas calls `POST /find`, both as they are (decision 06).
- A typed trade check, such as "is Chase Brown for Breece Hall fair", needs its players. Jev picks each player from the real rosters, with a Choice per side and a Noul for "names a player". If a pick is unsure, the Answer opens the Trade page with the form, and fills each player that Jev is sure of. Brian, 2026-11-10.
- This spec adds `POST /sell-high` to the Advisor in the `analyzer` package. It uses Sonnet 5.5 and reuses the Playbook, the fact helpers, the verifier, and the Jev checks of the Advisor. Code puts each player's trade value, lineup value, trend of the last 4 weeks, and schedule ahead side by side. The Advisor picks the players and writes why.
- The Advisor gets one optional stage callback. The route sends each stage as a data part, such as "Checked the players on each side", then the whole Answer. The Advisor does not stream its text, because a Lean must never show before the verifier passes it.
- The Case leads with the reason for its Lean. The fairness line agrees with the Lean.
- The trade ideas Topic calls `/find` for each client. The `finder` flag of `client.toml` keeps its meaning for the analyzer page only.

### Suggestions

- The API serves the Suggestions of Your team. The day of the week sets the base order. Jev lifts a Topic when its fact makes it urgent for Your team, with one Noul per Topic over the same fact that the Suggestion shows (decision 02).
- Each Suggestion shows its Topic name and one fact from code. The fact costs nothing and needs no check.
- The front door shows 3 Suggestions plus "More". A Topic that the manager opened drops off until its fact changes or the week turns. The browser keeps that record next to Your team. Clear keeps it.
- On open, the API builds the Answer of the top Suggestion when it is a personal Topic. The other Suggestions build on the tap.

### The cache and stale Answers

- The API keeps each Answer under a key built from the facts it read, such as the roster and the week. The same key streams the kept Answer back at once, at no cost. A free answer keys on the question text plus the data it read (decision 11).
- The site asks the API whether the key of each Answer in the Thread is still current. The check costs nothing. A stale Answer shows dimmed with "Your roster changed since <day>. [Refresh]" and hides its "checked" mark.

### The Thread

- The Thread reads top to bottom, newest at the bottom. The ask box stays at the bottom, with one row of Suggestion chips above it. "More" leads the chip row (decision 08).
- When a new question lands, it scrolls to its top, under the header. Each older Answer stays in the scroll as it rendered, with no fold, and plays no entrance and no stream again. The manager scrolls up to reread it (ticket 18).
- The browser keeps one Thread per team for the fantasy week. The week of the latest build keys it, so the Tuesday build starts an empty Thread (decision 05).
- Clear in the Thread header empties the Thread of this week for Your team, with no confirm.
- A miss and a cap line hide the Suggestion chips, so the 3 closest Topics show only once.

### Caps

- Each team gets 25 Claude Answers a day. A kept Answer, a route, an honest miss, and the head start of the top Suggestion do not count toward it (decision 04).
- Each league gets $25 a month, as a separate cap. The head start counts toward it.
- At 80% of the monthly cap, the API logs one alert. It sends no email, because the API has no mail sender. Brian, 2026-11-10.
- Past a cap, everything that costs nothing still works. A new Claude Answer shows a calm line with the 3 closest Topics. The team line reads "That's 25 questions today. Ask again tomorrow." The league line reads "The league's question budget is used up for this month. It resets on <date>." Neither line names a manager.
- The ask box needs the league passphrase, through the `X-League-Passphrase` header that the API uses now.
- The API keeps the counts and the miss log in a store on its Fly volume, like the egg store.

### The weekly build

- The pipeline writes the Answers of the 7 league Topics for each team into the published week, from the blurbs and data that exist now. The site reads them with no API call.
- It writes the fact of each Suggestion that comes from the weekly data.

### Look and motion

- The front door takes the structure and the motion of variant C in the brand of variant A (decision 07). The look of C becomes the dark theme, with the light theme beside it.
- The ask box sits at the center of an empty Thread and glides to the bottom on the first question, on one shared layout spring. A Suggestion morphs into the question. The words sharpen from a blur of about 6 px as they stream. The data block settles from a blur at a scale of 0.98. "More" springs open from one pill. The send button sits in a halo that grows as the field fills.
- The motion follows the `transitions-dev` tokens. Under `prefers-reduced-motion`, it keeps the fades and drops each move, blur, and loop. The check mark has no bounce.
- Each UI ticket meets the DESIGN BAR of the map.

### Records

- ADR 0031 covers the text that managers type. It says what goes to TypeSafe and to Anthropic. It says that the miss log lives on Fly, never in the repo, and that each entry stays 90 days. Brian, 2026-11-10. Number 0030 is the ADR of `manager-brain`.
- `GLOSSARY.md` gets the terms "honest miss" and "route" in the front-door group.

## Testing Decisions

A good test drives the front door from outside: a request to the API, a page render, or a browser run. It checks what a manager sees or what the API returns. It never checks a private function or the order of internal calls.

### The seams

1. **The API endpoints.** The ask endpoint, the Suggestions endpoint, and the key check run through `TestClient` with recorded Sleeper data, `FakeJev`, and a test model of Pydantic AI. They test the route table, the stream parts, the cache, the stale check, the caps, the passphrase, and the miss log. Prior art: `apps/api/tests/test_eggs.py` and `test_api.py`, with the fakes in `apps/pipeline/tests/fakes.py`.
2. **The front door page.** A vitest page test renders `/` with the real published data of `cpc` and a recorded stream. It tests the sheet, the Suggestions, "More", the Thread, the stale line, the cap lines, and Clear. Prior art: `apps/site/src/app/page.test.tsx`.
3. **The browser run.** A Playwright run drives the front door against the local API, on a phone viewport, in light and dark, with axe and with reduced motion. Prior art: `apps/site/e2e/eggs.spec.ts`.
4. **The weekly build.** A pipeline test builds a week from recorded data and checks the Answers of the league Topics in the published week. Prior art: the build tests of the pipeline.
5. **The route eval.** A test with the `live` marker sends the question set of decision 09 to the real Jev and reports the hit rate. It fails below 52 of the 59 questions with an expected route. It asserts no single probability. The questions name teams of the league and no manager, so they sit in the repo.

### What the evidence shows

- The trade ideas Answer runs with real `/find` output before the commissioner sees it. The prototype templates read as real and looked bad (decision 08).
- Each state of prototype 08 runs on a phone in light and dark: the sheet, the empty Thread, More, a league Answer, a personal Answer, "Fixing a number…", the trade check with its steps, trade ideas, a free answer with tool steps, an honest miss, a stale Answer with Refresh, the two cap lines, and Clear.

## Out of Scope

- Past seasons of the league in a free answer. It needs a new fetch and store.
- A split that sends simple lookups to Haiku 5.5. The commissioner chose Sonnet 5.5 for all answers.
- A port of the Advisor to Pydantic AI with a stream of the Case.
- A live news source. It adds a vendor and a cost, and its facts have no ground truth for the Jev check.
- A login for each manager. Your team lives in the browser.
- A chat of only free text with no Topics.
- A change to the content of a weekly report.
- A control to stop a stream.
- A Thread kept on the server or shared across devices.

## Further Notes

- `manager-brain` merged to `main` as `c133eb89` on 2026-11-10. The `front-door` branch merges `main` before the first ticket.
- For the API work, load the skill `building-pydantic-ai-agents` from `pydantic/skills`, plugin `ai@pydantic-skills`. Load `typesafe:typesafe-ai` before any Jev question or state.
- A copy of the code of prototypes 08 and 09 sits in a session scratchpad, outside the repo. The decisions are the source of truth.
- Cost: about $1 to $66 a month for 2 leagues, by use. Claude is over 95% of it. The caps hold the worst month near $50.
