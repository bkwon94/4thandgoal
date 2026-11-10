# Front door: map

App: site, pipeline, and api.
Spec branch: `front-door`.

## DESTINATION

One spec makes `/` an open, personal front door. A manager picks a team, sees Suggestions for that team, asks in an ask box, and gets each Answer in a Thread. The pages stay as the long form.

The goal: managers use the site because it is easy and about their own team. Now many managers skip the menu and the long reports.

## DESIGN BAR

Each UI decision and each UI ticket meets this bar: smooth, beautiful, cohesive, and clear with no help. Brian, 2026-11-09.

1. Search scrolltide for ideas before a layout prototype.
2. Use `transitions-dev` for each transition, and `transitions-polish` for its tokens.
3. Use `apple-design`, `animate`, `emil-design-eng`, and `make-interfaces-feel-better` for the motion and the detail.
4. Use the Artifact design type for a visual design, when a design helps more than code.
5. Run `critique` and `polish` on each prototype before Brian sees it.

## DECISIONS SO FAR

- The destination is the full revamp of the UI and the UX. The map holds the size. Brian, 2026-11-09, in the Stage 1 grill.
- The direction is as close to a chat as we can get. A chat of only free text is not the first build. Brian, 2026-11-09.
- `your-league` is scrapped. This map takes its ideas: Your team in the browser, the sheet that asks for it, and the live Finder. Brian, 2026-11-09.
- The pages break into short Answers. Each Answer is a short form of chapters of a page, and it links to the page. No page goes away. Brian, 2026-11-09.
- The first visit asks for Your team in a sheet, with no skip. Every Suggestion comes from Your team. Brian, 2026-11-09.
- The weekly build makes the Answers of the league Topics. The personal Topics, trade ideas, and the trade check are live from the API. Brian, 2026-11-09, changed by decision 01.
- Jev routes each question to a Topic. With no Topic, Jev asks "Can the facts of the week answer this?" A yes gets a short Claude answer that Jev checks. A no gets an honest miss, the 3 closest Topics, and a log entry. Brian, 2026-11-09.
- The ask box uses the league passphrase, a cap for each team, and one cap for the league each month. Past the cap, only Jev routes and honest misses run. Brian, 2026-11-09.
- The terms are Topic, Answer, Suggestion, and Thread. `GLOSSARY.md`.
- The first build has 13 Topics. The personal Topics use the Roster grade, the slot ranks, and facts side by side, with no new formula. The Advisor judges sell high. Only the personal Topics get new Claude text. `decisions/01-grill-the-first-topics.md`.
- Jev costs close to nothing, and Claude is over 95% of the cost. TypeSafe allows 80 requests and 100,000 tokens per second. Jev picks the slice of facts by the Topic, and an open question gets the full sheet. A new ADR covers the text that managers type. `decisions/03-research-jev-live-cost.md`.
- The day of the week sets the order of the Suggestions, and Jev lifts an urgent Topic. Each one shows its name and one fact from code. Three show, plus a "More" row. An opened Topic drops off until its fact changes. `decisions/02-grill-how-suggestions-rank.md`.
- The front door takes the structure and the motion of variant C in the brand of variant A. The look of C becomes the dark theme, with a light theme beside it. `decisions/07-prototype-the-design-language.md`.
- A free answer gets tools over this season and the nflverse game logs. Pydantic AI runs them on the API and streams through `VercelAIAdapter` to `useChat`. Jev checks each claim against the tool results, with at most 4 tool calls. `decisions/12-grill-free-answer-width.md`.
- `/` becomes the front door. The hero and the tool tiles go away. The menu stays with fewer links. Brian, 2026-11-09.

## NOT YET SPECIFIED

- What are the numbers of the caps? `decisions/04-grill-the-cap-numbers.md`.
- Does the Thread stay across visits, and does it reset each week? `decisions/05-grill-the-thread-across-visits.md`.
- Where is the border with `manager-brain`? `decisions/06-grill-the-manager-brain-border.md`.
- How does the front door look and move on a phone? `decisions/08-prototype-the-front-door.md`.
- Does the Jev route pick the right Topic for real questions? `decisions/09-prototype-the-jev-route.md`.
- How does a live personal Answer stay fast and cheap? `decisions/11-grill-live-answer-speed.md`.
- Which links stay in the menu, and what does each Answer link to? `decisions/10-spec-the-menu-and-pages.md`.

## OUT OF SCOPE

- Past seasons of the league in a free answer. It needs a new fetch and store. A later spec adds it if managers ask about history.
- A live news source. It adds a vendor and a cost, and its facts have no ground truth for the Jev check.

- A login for each manager. Your team lives in the browser, and nothing private depends on it.
- A chat of only free text with no Topics. Topics keep each Answer checked. The log of misses tells us when free text is worth its cost.
- A change to the content of a weekly report. The page stays the long form.
