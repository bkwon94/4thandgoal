# Site answer: map

App: site and api.
Spec branch: `site-answer`.

## DESTINATION

One spec: the chat answers a question about the site, such as "where is the trade analyzer", "what tools are there", or "how do I use the sim", with a Site answer. The Site answer shows a new block that links to each page it names, so a manager finds each part of the site from the chat.

## DECISIONS SO FAR

- The apps are site and api. The pipeline does not change. Grill of 2026-11-18.
- Three question shapes count: "where is X", "what tools are there", and "how do I use X". Grill of 2026-11-18.
- Jev routes the question to a new route kind `site`, and a Jev Choice picks the Menu item it asks about. The site renders a new block kind from its own Menu. No Claude call runs, so a Site answer uses no cap. Grill of 2026-11-18.
- The Site answer shows the link only. It never moves the manager to the page on its own. Grill of 2026-11-18.
- The pages are each Menu item of the client, plus the midseason report when the client has one. The egg board, the past weeks, and the manager pages of other teams stay out. Grill of 2026-11-18.
- The list view splits the pages into two groups: Tools, and the pages to read. Tool is a term in `GLOSSARY.md`. Grill of 2026-11-18.
- "How do I use X" shows the card of X with one fixed blurb from the client copy. Code writes the blurb, never Claude. Grill of 2026-11-18.
- The honest miss does not change, and it gets no page links. Grill of 2026-11-18.
- The terms Site answer and Tool are in `GLOSSARY.md`. The Menu definition now says "links", because Destination is a term of a trade. Grill of 2026-11-18.
- The Noul `n5` and the Choice `c1` route 21 of 22 site questions and keep 18 of 18 traps. A clear yes routes to `site` right after `ABUSE`. A Topic wins over a bare page name. `decisions/01-prototype-the-site-route.md`.

## NOT YET SPECIFIED

- What do the list view of the Tools and the "where is X" card look like and move like? `decisions/02-prototype-the-site-blocks.md`.
- What does the lead line say, what does each blurb say, and what does a client with the front door flag off show? `decisions/03-spec-the-copy-and-the-flag.md`.

## OUT OF SCOPE

- A step-by-step tutorial flow for each Tool. It needs content of its own: the steps of each Tool, who writes them, and how they stay true when a Tool changes. Brian chose to skip it for now, 2026-11-18. A later spec can start it with `4ag:plan`.
- Page links in the honest miss. A miss says only "I can't answer that."
- A move to the page with no tap. A wrong route would send the manager to a page they did not ask for.
