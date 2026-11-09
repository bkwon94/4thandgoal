# Manager brain: the analyzer and the Finder judge a trade as a manager of the league does

Status: ready-for-agent
Date: 2026-11-09
Apps: both. The pipeline package `analyzer` builds the fact sheet, asks Jev, calls the Advisor, and checks its words. The API serves the new analyze document and finder document. The site shows the Lean, the Case, and the Bullets on the analyzer page and the Finder cards.
Spec branch: `manager-brain`.
Source: the map `.scratch/manager-brain/MAP.md` and decision tickets 01 to 08. ADR 0030 (proposed), ADR 0029, ADR 0003 and ADR 0004 (superseded in part), ADR 0005 and ADR 0009 (stand as measures).
Tickets: none yet. `cpc:to-tickets` writes them.

## Problem Statement

The trade analyzer and the Finder grade a trade with a rubric. The chart ratio gives a start letter, and seven adjusters each move it by one step. Brian finds that the rules "sometimes work, but also often (more times than not) don't work". In week 8, the Finder called Gibbs for Bijan and Henry for Tuten and Higgins good for both. Each fix adds one more rule, and each new rule brings its own edge cases.

A manager of the league does not think in steps. A manager weighs the RB room after the trade, the record and the odds, a hot streak against a slump, how a player did late last season, the quality of his NFL team, and the news, such as a trade rumor. Then the manager makes a gut call with a condition: "if you believe in X, this is worth it". The page today shows a letter-free answer word and factor rows, and the factor rows read as code, not as advice.

The Finder has a second problem. It searches one partner at a time and ranks by the sum of steps. So it misses good partners, and it carries the bugs of the rubric into its picks.

## Solution

The analyzer and the Finder advise as a league-mate does. Code builds a fact sheet and keeps the hard rules. Jev answers small yes or no questions at scale. Claude, the Advisor, reads the sheet, the Jev answers, and the Playbook of the client, and makes the call.

For one trade, the manager sees a Lean (Send it, Lean yes, Gut call, Lean no, or Pass) on a 5-step scale, a Case that leads with its condition, and a fairness line. Under it, one tab per team holds 3 to 5 Bullets in For, Against, and Even bands. Each Bullet rests on one fact, and a tap shows that fact. No letter shows anywhere.

For the Finder, the manager presses Find with no partner. Jev filters the partners, picks the targets on each side, and makes a shortlist from offers that code builds. The Advisor picks up to three trades and gives each a headline and 2 to 3 Bullets: why you send it, and why he says yes. With no good match, the Finder says so in plain words.

Prototype 04 tested this design on 28 trades. Brian agreed with the Advisor on 20 of 24 trades. A press costs about 11 cents and takes about 20 s.

## User Stories

### The read of one trade

1. As a manager, I want one Lean of five for my trade, so that I know which way to go at a glance.
2. As a manager, I want the Lean on a 5-step scale from Pass to Send it, so that I see how strong the call is.
3. As a manager, I want "Gut call" as a real answer for a close trade, so that the tool does not fake a sure answer.
4. As a manager, I want a Case under the Lean that reads like advice from a league-mate, so that I trust the call.
5. As a manager, I want the Case to lead with its condition, such as "if you believe a healthy QB today matters more", so that the first lines tell me what the call rests on.
6. As a manager on a phone, I want the Case clamped to 3 lines with "Read the full case", so that the page stays short.
7. As a manager, I want the Case to name the risk and the upside, so that I can weigh them myself.
8. As a manager, I want the Case to back its claims with data but not list stats, so that it reads as advice.
9. As a manager, I want a fairness line, "Fair" or "Lopsided: <team> gives more.", so that I know if the other manager can take it.
10. As a manager, I want 3 to 5 Bullets for my side and 3 to 5 for the other side, so that I see both reads.
11. As a manager, I want each Bullet marked for, against, or even with a ▲, ▼, or – glyph, so that I can scan the reasons without color.
12. As a manager, I want the Bullets of a side in For, then Against, then Even bands, so that the good and the bad sit apart.
13. As a manager, I want one tab per team, with my tab open first, so that the same pattern works for a 2-team and a 3-team trade.
14. As a manager, I want to tap a Bullet and see the fact behind it, so that I can check the claim.
15. As a manager, I want no letter grade anywhere, so that I read the advice and not a score.
16. As a manager, I want the read of "would he accept" to weigh the depth of the other team, so that the Advisor does not suggest a trade that leaves him short.
17. As a manager, I want the Advisor to know the RB room I have after the trade, so that it never tells me to send my last reliable RB.
18. As a manager, I want the Advisor to know the quality of each player's NFL team, so that a player on a bad offense is not read as a safe start.
19. As a manager, I want the Advisor to read my race group (In, Bubble, Out) and my odds, so that a contender firms up and a bubble team takes risks.
20. As a manager of an eliminated team, I want the Advisor to say so plainly, so that I am not told to push for the playoffs.
21. As a manager, I want a bye in the trade week to be a fact for every side, so that the Advisor weighs it with my race group.
22. As a manager, I want history claims to carry a number from past seasons, such as weeks 9 to 17 last year, with the game count, so that I know how strong the history is.
23. As a manager, I want the Advisor to say when a split rests on few games, so that I do not over-trust it.
24. As a manager, I want the Advisor to speak of a player with no past season in words, with no number, so that it never invents a stat.
25. As a manager, I want the Advisor to know the latest player news, such as a trade rumor, so that the read is current on the day I press.
26. As a manager, I want a rumor to read as a report with its source, such as "Rotoballer reports…", so that I never take a rumor as fact.
27. As a manager, I want the chart value to count as one fact among many, so that a market price informs the call but never decides it.
28. As a manager, I want a week with no chart to still grade, with the Case saying the chart is missing, so that the tool still works.
29. As a manager, I want a player who is not on the chart to stay in play, with a fact that says so, so that a waiver pickup can still be traded.
30. As a manager, I want an honest error when the Advisor fails twice, so that I never see a code answer dressed as advice.
31. As a manager, I want a failed grade not to count toward my grade limit, so that a failure costs me nothing.
32. As a manager, I want the same trade in the same week to give the same read on a repeat press, so that the page does not flip-flop.

### The Finder

33. As a manager, I want to press Find with no partner, so that the Finder searches the whole league for me.
34. As a manager, I want the partner picker to stay as an option, so that I can search one partner when I want.
35. As a manager, I want the Finder to skip a partner who has nothing I need or cannot spare it, so that the search stays fast.
36. As a manager, I want the Finder to pick the players a manager would want on each side, not a code screen on points, so that a backup about to start still counts.
37. As a manager, I want the Finder to build 1-for-1, 2-for-1, and 1-for-2 offers only, so that the picks stay simple.
38. As a manager, I want no kicker, no defense, no player out with no return week, and no handcuff in an offer, so that every pick is a legal and real trade.
39. As a manager, I want up to three picks, each with a headline and 2 to 3 Bullets, so that I know why I send it and why he says yes.
40. As a manager, I want the Finder Bullets to use the same rows, Marks, and tap as the analyzer, so that both pages read the same.
41. As a manager, I want "See the full result" on a pick to grade it in the analyzer, so that I get the full read of that trade.
42. As a manager, I want the analyzer and the Finder never to disagree on one trade, so that I trust both.
43. As a manager, I want a plain line when no good trade exists, so that I am not shown a bad trade to fill space.
44. As a manager, I want the Finder to show its shortlist with plain fact lines when the Advisor fails, so that a press still gives me something useful.
45. As a manager, I want a Finder press to finish in about 25 s, so that I wait no longer than a cold grade.

### The commissioner and the client

46. As the commissioner, I want a Playbook in the voice folder of each client, so that the Advisor thinks the way this league thinks.
47. As the commissioner, I want the cpc Playbook to say RBs first in half PPR, contenders firm up, bubble teams take risks, a top 3 to 5 player beats two good ones, and managers here chase recent points, so that the Advisor reads this league.
48. As the commissioner, I want the Advisor to write in the voice of the client, so that the page reads like the rest of the site.
49. As the commissioner, I want one manual step to give a chart before a build, so that a missed fetch never blocks a week.
50. As the commissioner, I want the build log to say plainly when a week has no chart, so that I know to place one.
51. As the commissioner, I want the chart cache to trust a hash of the PNG, not file times, so that a hand-placed chart is read.
52. As the commissioner, I want the cost of a press to stay near 11 cents for the analyzer and 12 cents for the Finder, so that the tool stays cheap to run.

### The guards

53. As the commissioner, I want each number and name in a Bullet or the Case to come from a cited fact, so that the Advisor never invents a stat.
54. As the commissioner, I want each cited fact id to exist on the sheet, so that a tap always opens a real fact.
55. As the commissioner, I want no inner word, such as "trade value" or "return bet", to reach the page, so that the copy reads as plain football talk.
56. As the commissioner, I want a Bullet that cites news to say "reported", "per", or the source, so that a rumor stays a rumor.
57. As the commissioner, I want a Jev check of faithfulness and of rumors to run log-only first, so that I can see its hit rate before it can block a read.
58. As the commissioner, I want a failed check to retry the Advisor once, so that one slip does not cost the manager a read.
59. As the commissioner, I want the copy never to say "rival" and never to name me, so that the site follows the house rules.

### The developer

60. As a developer, I want the rubric, the start letter, the breakdown, the adjuster steps, and the factor rows gone, so that one way of judging remains.
61. As a developer, I want each adjuster kept as a Measure that writes a fact and moves nothing, so that its data still informs the Advisor.
62. As a developer, I want the analyze document and the finder document to carry the Lean, the Case, the fairness, and the Bullets with their Marks and fact text, so that the site renders with no logic of its own.
63. As a developer, I want the document version to change, so that no cached result of the rubric serves after the deploy.
64. As a developer, I want Jev requests sent in waves under the token limit, so that a press never hits the rate limit.
65. As a developer, I want the news feed cached per player for 1 hour, so that a second press makes no new call.
66. As a developer, I want a failed news fetch to give a sheet with no news, so that the feed never stops a grade.
67. As a developer, I want the history splits of past seasons cached for good, so that a press never fetches them again.
68. As a developer, I want the glossary and ADR 0030 to match the code, so that the next agent reads one meaning per term.

## Implementation Decisions

### The roles (ADR 0030)

- Code measures. It builds the fact sheet, lists the candidates of the Finder, and checks the hard rules and the words. A Measure moves nothing.
- Jev answers atomic questions at scale, through the Jev port of ADR 0029. It runs the partner filter, the targets, the shortlist, the atomic questions of one trade, and the log-only checks.
- Claude, the Advisor, makes the call and writes it. It reads the sheet, the Jev answers, and the Playbook.
- ADR 0030 moves from proposed to accepted when this spec merges.

### The fact sheet

- Each fact has an id, a text, and its numbers, as the facts of the analyzer have now. The fact id carries its kind in its prefix or suffix. The `Fact` model gets no new field.
- The player facts: points per game, the position rank, the last 3 games, the snap and usage trend, and the injury tag with the return week.
- The history facts (decision 06): from the nflverse weekly player file of the last 3 complete seasons, now 2023 to 2025. Per player and season: the team, the half-PPR points per game in weeks 1 to 8 and in weeks 9 to 17, and the points per game in cold games, each with its game count. A cold game is outdoors at 40 F or below. The gsis ids map to Sleeper ids through the player id table. A past season file is cached with no max age. A player with no past season gets no split.
- The team facts: the record, the race group (In, Bubble, Out) and the playoff odds, the RB depth before and after the trade in plain words ("your RBs in the top 36 go from 2 to 3"), the depth of the other team at the positions of the trade, and a bye in the trade week for every side. The pipeline uses the term race group, the same as the site.
- The NFL team fact: a quality measure of each player's NFL team, from the nflverse team stats.
- The chart fact (decision 07): the chart value as one fact with no gates. An unlisted player gets a fact that says so. A week with no chart gets a fact that says so, and the Case says it. The Playbook wins over the chart.
- The Measures: each old adjuster (roster fit, standing, trend and usage, injury, upside, superstar, handcuff, schedule, expected gap, consolidation) writes facts and moves nothing. Known bad reads get a fix as facts, such as the trend that reads only snaps.
- The news facts (decision 08): code fetches the Sleeper news feed of each trade player on each call, through the existing `fetch_news`. The sheet gets the newest 2 items from the last 7 days, newest first, as facts `NEWS.{player_id}.{n}`. The text is "Reported on <YYYY-MM-DD> by <Source>: <description cut at 300 characters>". The URL stays out of the numbers. An item with no description drops. A cache in memory keeps the feed of a player for 1 hour. A failed fetch gives no news fact and never stops the call.

### The chart cache (decision 07)

- The saved read of a chart stores a hash of its PNG. A read runs again only when the hash differs, not when a file time differs.
- The manual step: put the PNG in the chart cache folder of the week, then run `cornerstone chart --client <slug> --week NN` to read and check it.
- The build log says plainly when a week has no chart.
- This fix also helps `main`, so it ships as the first ticket.

### The Playbook

- Each client has a Playbook file in its voice folder. The Advisor reads it on each call.
- The cpc Playbook holds the tips of decision 01: RBs are worth more in half PPR, and QBs and TEs the least. A trade is a gut call on trends and schedule. A contender firms up, and a bubble or low team takes risks. One consensus top 3 to 5 player at his position beats two good ones. Managers here chase recent points. Upside and the trend of usage matter. The RB scarcity tip is strong after trade 6 of prototype 04.
- The NorCal client gets a Playbook too. Until the commissioner writes its tips, it holds the general tips with no league-specific claim.

### The Jev questions

- The wording "a" of the fairness and need questions won the probe of prototype 04. The questions and the state shapes are in `decisions/04-prototype-judge-arms.notes.md`.
- One trade: Jev answers "is it fair?", "does the asker need it?", and "does the other manager need it and would he accept?". The answers join the sheet as facts.
- Code sends Jev requests in waves under the limits that Brian read: 80 requests per second and 100,000 tokens per second.

### The Advisor call

- One Claude call per analyzer press, and one per Finder press. The model and the effort are those of prototype 04.
- The output of one trade:

  ```
  lean: "Send it" | "Lean yes" | "Gut call" | "Lean no" | "Pass"
  case: string            # 4 to 6 sentences, the condition first
  fairness: "fair" | "lopsided"
  lopsided_toward: roster id | null
  asker_bullets: [ { text, mark: "for" | "against" | "even", fact_id } ]   # 3 to 5
  other_bullets: [ ... ]                                                    # 3 to 5, per side
  ```

  This shape came from prototype 04. A trade of 3 or more sides has one Bullet list per side.
- The output of one Finder press: up to 3 picks, each `{ offer_id, headline, bullets }` with 2 to 3 Bullets, or a `none_line` in plain words when no offer is good.
- The prompt rules: advise the asker in the voice of the client. Lead the Case with its condition. Name the risk and the upside. Back claims with data, but do not list stats. Say when a split rests on few games. A news fact is a report: name the source or say "reported", and never state a trade or a role change as done. Never write "rival". Never name the commissioner.
- Fairness is set by the Advisor. The fairness block of the document keeps one reason per side.

### The guards

- Facts check: each cited fact id is on the sheet, and the Bullets of a side cite at least one fact.
- Number and name check: each number and each name in a Bullet or the Case comes from a cited fact.
- Inner words check: no Bullet and no Case holds an inner word, such as "trade value" or "return bet".
- Attribution check: a Bullet that cites a `NEWS.` fact holds "reported", "report", "per", "according to", "rumor", or the source name.
- A failed check retries the Advisor once. After two failed calls, the analyzer returns an honest error, and the call does not count toward the grade limit.
- The Jev faithfulness check and the Jev rumor check ("does the Bullet state the report as a sure fact?") run log-only. They never block a read in this spec.
- The upside rule and the letter rule go.

### The Finder

1. The partner filter: for each partner, Jev asks four questions, with the weak slots of the asker in the state. Does he have your need? Can he spare it? Do you have his need? Can you spare it? Code counts the depth. Only a partner with four yes answers gets a full search. With a partner picked, the filter runs on that partner alone.
2. The targets: for each partner that passes, Jev asks of each of his players "would the asker want him?" and of each player of the asker "would that manager want him?". A target needs p 0.6 or more, at most 4 per side.
3. The offers: code builds every 1-for-1, 2-for-1, and 1-for-2 offer from the targets only. Code keeps only the hard rules: no kicker, no defense, no player out with no return week, and no handcuff.
4. The shortlist: Jev asks the fair and need questions of each offer. Code keeps the 10 offers with the highest product of "close to fair for both" and "fills a starting need" for each side.
5. The pick: code builds a fact sheet for each shortlist offer, with news only for those players. The Advisor picks up to 3.
6. The fallback: when the Advisor fails twice, the document holds the Jev shortlist, with plain fact lines and a fallback flag.

### The documents and the API

- The analyze document drops the decision, the answer word, the factor rows, and the letters. It gains `lean`, `case`, and per side a list of Bullets, each `{ text, mark, fact_id, fact_text }`. The fairness block stays in its shape, set by the Advisor.
- The finder document gives each pick a `headline` and its Bullets in the same shape, and keeps the fallback flag and the empty line.
- The find request makes the partner optional.
- The document version changes, so no cached rubric result serves.
- The result cache of a week keys on the trade, as now, so a repeat press gives the same read.

### The page (decision 05)

- The hero shows the Lean word, then the 5-step scale with the Lean step lit, then the Case clamped to 3 lines on the phone with "Read the full case", then the fairness line.
- Under the swap card, a switcher holds one tab per team at every width, with the tab of the asker open first. Inside a tab, the Bullets sit as rows in For, Against, and Even bands. A band with no Bullet is left out.
- The Mark is a glyph: ▲ for, ▼ against, – even. The glyph is decorative, and a screen reader hears the word.
- A tap on a row opens its fact text under it, as an accordion.
- The Finder card shows the headline, the swap, then its Bullet rows with the same Marks and tap. The partner picker becomes optional.
- The motion is small: the Lean word rises in once, and the bands may stagger in. Each motion respects reduced motion.
- No letter shows anywhere. The copy says "manager" or "another manager", never "rival", and "the commissioner", never a name.

### The records

- The glossary on the Spec branch already holds the terms: Advisor, Grade, Lean, Case, Bullets, Mark, Measure, Playbook, Partner filter, Target, Shortlist, and race group. The build removes the old terms from code and copy.
- ADR 0030 becomes accepted at merge. It supersedes ADR 0003 and ADR 0004 in part.

## Testing Decisions

A good test checks the behavior a caller sees: the document that the API returns, or the page that the site renders. A test does not check the prompt text, the order of internal calls, or the private helpers.

The seams, highest first:

1. **The API documents.** The routes `/analyze` and `/find` with a stub Advisor and the existing fake Jev at the port. This is the main seam. Prior art: `StubAnalyzer` and the route tests of the API, and `FakeJev` of the Jev port. The tests cover the document shape, the guards and the retry, the honest error with no grade count, the fallback of the Finder, the optional partner, the hard rules of the offers, the news facts and their attribution check, the fetch failure of the news, and the document version.
2. **The site render.** The analyze result and the Finder card render from fixture documents. Prior art: the render tests of the analyze result and the trade finder. The tests cover the Lean and the scale, the clamp of the Case, the tabs, the bands, the Marks and their screen-reader words, the tap on a fact, a 3-team trade, and no letter anywhere.
3. **The fact sheet.** The measures that build facts from snapshot fixtures: the history splits, the RB depth after the trade, the NFL team quality, the race group, the chart fact, and the news facts. Prior art: the fact tests of the pipeline. A test checks the fact text and its numbers, not how the measure computes them.
4. **The chart cache.** A hand-placed PNG with an older time than its JSON is read again when its hash differs, and is not read again when the hash matches.
5. **The live eval.** One script runs the real Advisor and the real Jev on the 28 trades of the test set and on the two Finder askers of prototype 04. It records the fact sheet, the Lean, the Case, and the Bullets of each trade, with the cost and the time. The fact tests of the acceptance file use these sheets as evidence. This is evidence for the Judge and for Brian's reactions, not a pass or fail in CI. The test set stays out of the public repo, because it names league managers.

Brian checks these seams with the spec.

## Out of Scope

- Finder trades of 2-for-2 and larger. The candidate shapes stay small, so any gain comes from the Advisor alone.
- A free-text trade request, such as "find me a WR". It is a later spec on the Jev roadmap.
- The Jev checks of the weekly copy. The `jev` spec and its later specs own them.
- A Jev check that blocks a read. The checks of this spec run log-only.
- The waiver web search for trade players. Decision 08 rejected it.
- Suggested counters on the analyzer page. The slot stays as it is.

## Further Notes

- The risk of the tabs: they hide the other side until a tap, and "would he accept" is half the advice. Brian chose tabs for one pattern across all trade sizes.
- The risk of the news feed: the Sleeper news endpoint is unofficial and can change with no notice. The fallback is a sheet with no news.
- The risk of the targets: a target that Jev misses drops every offer with that player.
- The same trade can get a different read on two calls with a cold cache. The result cache of the week covers a repeat press.
- The prototype 04 output and the test set name league teams. Keep them out of commits and out of published artifacts (ADR 0021).
- The trade deadline of 2026 is 2026-11-10. A rumor of the deadline lives for days, so the feed is read on each call.
- The architecture diagram of this spec is a private artifact: https://claude.ai/artifact/RoBLfmmqRGs4zZkMdWAgze
