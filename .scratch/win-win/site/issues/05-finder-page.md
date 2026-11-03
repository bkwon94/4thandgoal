# 05 — Finder page

**Repo:** site. **Spec:** pipeline repo `.scratch/win-win/pipeline/PRD.md`, phase 2.

**What to build:** A manager picks a partner team on the analyze page, taps "Find a trade", and reads three cards: each with the two sides, the fairness line, and one reason. Each card links to the full result for that trade through the analyze route. An empty result shows the line that no swap between these rosters is good for both. The as-of line shows the data week. A 429 shows the same wait line as the analyze form.

**Blocked by:** 02 — Fairness line on the result page; 04 — Finder route (pipeline).

**Status:** done

- [x] A partner picker on the analyze page with the eleven other teams.
- [x] The "Find a trade" action calls the finder route with the passphrase and the two roster ids.
- [x] Three cards render from the fixture finder document, with a test. Each card links to the analyze result for its trade, with a test.
- [x] The empty-list line renders, with a test.
- [x] The 429 wait line renders, with a test.
- [x] The fixture finder document is a byte-identical copy of the pipeline's.
- [x] The tests pass.

## Comments

2026-10-22: The fixture finder document is a byte-identical copy of the pipeline fixture on `main`, next to the analyze fixture. The analyze fixture still matches the pipeline `main`. A new `TradeFinder` component shows under the trade form once "My team" has a pick. Its "Trade partner" picker lists the eleven other teams. "Find a trade" posts `season`, `asker`, and `partner` to `/find` with the passphrase. The result shows up to three cards, the empty line word for word, and the as-of line of the analyze result.

Each card shows the swap card, the `FairnessBlock` from ticket 02, and the reason. A null reason shows the fairness line alone. A 429 shows the same wait line as the analyze form. A 422 shows the API message and asks the page for fresh rosters. A 503 shows the same fixed line as the trade form. A 401 asks for the passphrase again.

Each card links to the full result through a button. The button "See the full result" fills the trade form with the trade and submits it through the existing analyze path. The analyze page reads no query, so this is the smallest change. The `submit` of the trade form now takes an optional trade, because the new picks land in state one render later. `analyze-result.tsx` now exports `SwapCard`, `FairnessBlock`, and `AsOfLine` for the cards. All 198 tests pass, and the typecheck and the build pass. The site push is for Brian.

2026-10-22: The finder is behind `NEXT_PUBLIC_FINDER` and off by default, because the page felt crowded.
