# Front door tour: map

App: site.
Spec branch: `front-door-tour`.

## DESTINATION

A first-visit Tour on the front door of each client. It shows a league mate what the front door does, and where the weekly reports and the tools are.

## DECISIONS SO FAR

- The feature is one spec in the site app only. It has no pipeline change and no API change. Grill of 2026-11-18.
- Every browser sees the Tour once after the release, which includes the browsers that already have Your team. The menu gets a link that shows the Tour again. Grill of 2026-11-18.
- On a new browser, the Tour starts after the team sheet closes, so the Stops point at the real Suggestions of Your team. Grill of 2026-11-18.
- The Tour has four Stops: the Suggestions, the ask box, the team switch, and the menu button or the pill bar. The menu sheet does not open during the Tour. Grill of 2026-11-18.
- The Tour is passive. Each Stop has Next and Skip and a count such as "2 of 4". The last Stop says Done. A tap on the dim area goes to the next Stop. The real controls do not respond during the Tour. Skip counts as seen. Grill of 2026-11-18.
- The glossary names the feature "Tour" and each spotlight "Stop". Grill of 2026-11-18, in `GLOSSARY.md`.
- The Stop card is a modal ui-sdk `Popover` in a new wrapper of `packages/design/site/ui/`. The spotlight is a `box-shadow` dim that `framer-motion` moves. The motion uses transitions-dev tokens. No scrolltide item fits. `decisions/01-research-the-tour-build.md`.
- The look is Spotlight glide: a dim with a centered rounded hole, and a card with a header, ride one `GLIDE` spring together. The card places itself, not ui-sdk. Next and Done use the brand accent. `decisions/02-prototype-the-stop-look.md`.

## NOT YET SPECIFIED

- What is the header and the line of each Stop, and where does the replay link sit on desktop? `decisions/03-grill-stop-copy-and-replay.md`.
- What does the Tour do under reduced motion, and what browser key marks it as seen? `decisions/04-spec-reduced-motion-and-key.md`.

## OUT OF SCOPE

- A Tour on the other pages. The front door is where a league mate lands, and the menu Stop points at the other pages.
- Live facts of the week in the Stops. Static copy keeps the Tour the same from week to week.
- Any pipeline or API change. The Tour needs only data that the front door already has.
