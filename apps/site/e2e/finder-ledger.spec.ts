/**
 * The Ledger cards and the near fold of the Finder, in WebKit, as Safari runs, on the phone, the iPad, and the desktop.
 * It checks the layout of each shape, the streamed cards with their count line, and the step 5 lines of the wait.
 */
import { type Page, devices, expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { Theme } from "@cpc/design/lib/theme";
import { LOCAL_API } from "./evidence";
import { openPage } from "./floor";
import { serveDir } from "./serve";
import { findOverlap } from "./smoke";

const OUT = join(process.cwd(), "out");
// Run it on the export of NorCal built against the local API URL, as the grade-bar project does:
// CLIENT=norcal NEXT_PUBLIC_API_URL=http://localhost:8080 pnpm build
// The recorded find answer of a real press for Bo Girds with the RB chip on the local API, week 11 of cpc: 4 picks of
// two shapes, and 3 near ideas.
const FIND = readFileSync(join(process.cwd(), "..", "..", "packages", "analyzer", "site", "lib", "fixtures", "find-response-bo-girds-rb.json"), "utf8");
const DOC = JSON.parse(FIND) as {
  trade_pair: { asker: { roster_id: number } };
  trades: { sides: { roster_id: number; team: string; gives: { player_id: string; name: string; position: string; nfl_team: string; headshot: string }[] }[] }[];
  near: { sides: { roster_id: number; gives: { name: string }[] }[] }[];
};
// The find stream of the API: the document of the fixture in its answer part, as one event stream.
const FIND_STREAM = `data: ${JSON.stringify({ type: "data-answer", data: { kind: "find", document: DOC } })}\n\ndata: [DONE]\n\n`;
const CORS = { "access-control-allow-origin": "*", "access-control-allow-headers": "*", "access-control-allow-methods": "GET, POST" };
const ASKER = DOC.trade_pair.asker.roster_id;

// The browser of a file is set at its top, because a group cannot pick the browser. Safari runs on WebKit.
test.use({ browserName: "webkit", reducedMotion: "reduce" });

/* The iPhone 15 with no browser of its own, because a group cannot pick the browser. The file runs WebKit. */
const { defaultBrowserType: _browser, ...IPHONE } = devices["iPhone 15"];

/* The iPhone 15 at 390 by 660 first, then the iPad upright and on its side, then the desktop. */
const VIEWPORTS = [
  { name: "iPhone 15 390x660", use: { ...IPHONE, viewport: { width: 390, height: 660 } } },
  { name: "iPad 810x980", use: { viewport: { width: 810, height: 980 } } },
  { name: "iPad 1080x740", use: { viewport: { width: 1080, height: 740 } } },
  { name: "desktop 1280x800", use: { viewport: { width: 1280, height: 800 } } },
] as const;

/* The teams of the find answer: the asker and each partner, each with the players it gives in the answer. */
function teamsOfFind() {
  const teams = new Map<number, { roster_id: number; team: string; manager: string; avatar: null; players: unknown[] }>();
  for (const trade of DOC.trades)
    for (const side of trade.sides) {
      const team = teams.get(side.roster_id) ?? { roster_id: side.roster_id, team: side.team, manager: side.team, avatar: null, players: [] };
      for (const { player_id, name, position, nfl_team, headshot } of side.gives)
        if (!team.players.some((p) => (p as { player_id: string }).player_id === player_id)) team.players.push({ player_id, name, position, nfl_team, headshot });
      teams.set(side.roster_id, team);
    }
  return JSON.stringify({ teams: [...teams.values()] });
}

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server?.close();
});

/* The short name of a player as the API sends it: the last word that is not a suffix, such as "Walker". */
const SUFFIXES = new Set(["jr.", "sr.", "ii", "iii", "iv"]);
const lastOf = (name: string) => name.split(" ").filter((word) => !SUFFIXES.has(word.toLowerCase())).at(-1) ?? name;
/* The Shortlist of the press: each trade and each near idea of the fixture was a Shortlist trade, from the side of the
   asker, the players he gives, then the players he gets. */
const SHORTLIST = [...DOC.trades, ...DOC.near].map((item, i) => ({
  offer_id: `offer-${i}`,
  gives: item.sides[0].gives.map(({ name }) => ({ name, last: lastOf(name) })),
  gets: item.sides[1].gives.map(({ name }) => ({ name, last: lastOf(name) })),
}));
/* The parts of a find before the pick sends its first trade: steps 1 to 4 with their done lines, the Shortlist, and
   the live line of step 5. They go out with the response, as the API sends them in about the first 5 s. */
// The search reads each team of the find answer but the asker, as the teams route of the test lists them.
const PARTNERS = new Set(DOC.trades.flatMap((trade) => trade.sides.map((side) => side.roster_id))).size - 1;
const LEAD = [
  [`Reading ${PARTNERS} teams`, true],
  [`Read ${PARTNERS} teams`, false],
  ["Matching trade value", true],
  ["Matched 4,667 trades by trade value", false],
  ["Checking 4,667 trades for fairness", true],
  ["Checked 4,667 trades for fairness", false],
  ["Checking 77 against both lineups", true],
  [`Made a shortlist of ${SHORTLIST.length}`, false],
].map(([line, live]) => ({ type: "data-step", data: { line, live } }));
/* The pick can keep 5, as the live line "Picking the best 5" says, and it states that it keeps the 4 trades of the
   fixture before it writes them. So the count part goes out after the live line of step 5, before the first trade. */
const MOST = DOC.trades.length;
const LEAD_PARTS = [
  ...LEAD,
  { type: "data-shortlist", data: { trades: SHORTLIST } },
  { type: "data-step", data: { line: "Picking the best 5", live: true } },
  { type: "data-trades-count", data: { count: MOST } },
];

/* The parts of a streamed find: one trade part per trade of the fixture, in order, each with the count of trades that
   the pick keeps, then the part that says the pick has no more trades, then the answer with the whole document. The
   trades-done part follows the last trade, as the API sends it when the picks list closes. */
const STREAMED = [
  ...DOC.trades.map((trade, index) => ({ type: "data-trade", data: { index, most: MOST, trade } })),
  { type: "data-trades-done", data: {} },
  { type: "data-answer", data: { kind: "find", document: DOC } },
];

/* A find stream that the test feeds one part at a time. The browser fetch of the find stream gets a held body, and
   window.__sendNext sends the next part, so the test reads the page between two parts. Every other request goes on. */
async function holdFindStream(page: Page) {
  await page.addInitScript(([lead, parts]) => {
    const realFetch = window.fetch.bind(window);
    window.fetch = async (input, init) => {
      const url = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
      if (!url.includes("/find-stream")) return realFetch(input, init);
      let controller!: ReadableStreamDefaultController<Uint8Array>;
      const body = new ReadableStream<Uint8Array>({
        start: (c) => {
          controller = c;
          for (const part of lead) c.enqueue(new TextEncoder().encode(`data: ${JSON.stringify(part)}\n\n`));
        },
      });
      const left = [...parts];
      (window as unknown as { __sendNext: () => number }).__sendNext = () => {
        controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify(left.shift())}\n\n`));
        if (left.length === 0) controller.close();
        return left.length;
      };
      return new Response(body, { status: 200, headers: { "content-type": "text/event-stream" } });
    };
  }, [LEAD_PARTS, STREAMED] as const);
}

/* Opens the analyzer in Find mode with the asker as Your team, taps Find, and waits for the cards. With `streamed`,
   the find stream is held, so no card shows until the test sends its part. */
async function openFinder(page: Page, theme: Theme, streamed = false, clock = false) {
  await page.route((url) => !["127.0.0.1", "localhost"].includes(url.hostname), (route) => route.abort());
  await page.route(`${LOCAL_API}/**`, (route) => {
    const request = route.request();
    if (request.method() === "OPTIONS") return route.fulfill({ status: 204, headers: CORS });
    if (request.url().includes("/find-stream")) return route.fulfill({ status: 200, headers: CORS, contentType: "text/event-stream", body: FIND_STREAM });
    if (request.url().includes("/teams")) return route.fulfill({ status: 200, headers: CORS, contentType: "application/json", body: teamsOfFind() });
    return route.abort();
  });
  await page.addInitScript((asker) => {
    localStorage.setItem("cpc.passphrase", "test");
    localStorage.setItem("cpc.your-team", String(asker));
  }, ASKER);
  if (streamed) await holdFindStream(page);
  await openPage(page, `${server.url}/analyze/?mode=find`, theme);
  // The fixed clock starts after the page settles, so the settle wait of openPage runs on the real clock.
  // A clock that runs on its own would move the lines while the test reads them, so it stands still until runFor.
  if (clock) {
    const now = Date.now();
    await page.clock.install({ time: now });
    await page.clock.pauseAt(now + 1000);
  }
  const find = page.getByRole("button", { name: "Find a Trade" });
  await expect(find).toBeVisible();
  await find.click();
  if (!streamed) await expect(page.getByRole("article")).toHaveCount(DOC.trades.length);
}

/* No text of the page overlaps another, and the page never scrolls sideways. The fixed and sticky parts sit over
   content that the reader scrolls past, so the scan hides each one for its run. */
async function expectNoOverlap(page: Page) {
  await page.evaluate(() => {
    for (const el of document.querySelectorAll<HTMLElement>("body *")) if (["fixed", "sticky"].includes(getComputedStyle(el).position)) el.style.visibility = "hidden";
  });
  expect(await findOverlap(page)).toBeNull();
  await page.evaluate(() => {
    for (const el of document.querySelectorAll<HTMLElement>("body *")) if (el.style.visibility === "hidden") el.style.visibility = "";
  });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
}

/* The fixed and sticky parts of the page that show and cover a part of the screen. */
async function fixedBars(page: Page) {
  return page.evaluate(() =>
    [...document.querySelectorAll<HTMLElement>("body *")]
      .filter((el) => ["fixed", "sticky"].includes(getComputedStyle(el).position) && el.checkVisibility({ opacityProperty: true, visibilityProperty: true }))
      .map((el) => ({ name: el.getAttribute("aria-label") ?? el.tagName.toLowerCase(), ...el.getBoundingClientRect().toJSON() }))
      .filter((box) => box.width > 0 && box.height > 0 && box.bottom > 0 && box.top < window.innerHeight),
  );
}

for (const viewport of VIEWPORTS) {
  test.describe(viewport.name, () => {
    test.use(viewport.use);
    for (const theme of ["light", "dark"] as const) {
      // It streams the trades one part at a time. Each card shows as its part comes, with the count line, and the
      // first card scrolls into view.
      test(`each card shows as its trade part comes, with the count line under the cards, ${theme} (AT-72)`, async ({ page }, info) => {
        await openFinder(page, theme, true);
        const cards = page.getByRole("article");
        const more = page.getByText(/^Writing \d+ more trades?$/);
        await expect(page.getByRole("region", { name: "Finding Trades" })).toBeVisible();
        await expect(cards).toHaveCount(0);
        const count = DOC.trades.length;
        for (let shown = 1; shown <= count; shown++) {
          await page.evaluate(() => (window as unknown as { __sendNext: () => number }).__sendNext());
          await expect(cards).toHaveCount(shown);
          // The count comes from the pick before the first card, so the line counts only the trades that still come.
          const left = MOST - shown;
          if (left > 0) await expect(more).toHaveText(`Writing ${left} more ${left === 1 ? "trade" : "trades"}`);
          else await expect(more).toHaveCount(0);
          await expect(cards.first()).toHaveAttribute("aria-label", `Trade 1 of ${MOST}`);
          // The wait stays while the cards come, and the near fold waits for the end.
          await expect(page.getByRole("region", { name: "Finding Trades" })).toBeVisible();
          await expect(page.getByRole("button", { name: /Close, but not sent/ })).toHaveCount(0);
          if (shown === 1) {
            // The first card lands in view on its own, so the reader sees it with no scroll of his own.
            await expect.poll(async () => {
              const box = (await cards.first().boundingBox())!;
              return box.y >= 0 && box.y < viewport.use.viewport.height / 2;
            }).toBe(true);
            await page.screenshot({ path: info.outputPath(`stream-first-card-view-${theme}.png`) });
            await expectNoOverlap(page);
            await page.screenshot({ path: info.outputPath(`stream-first-card-${theme}.png`), fullPage: true });
          }
        }
        // The pick has no more trades, so the count line goes under the last card before the answer comes.
        await page.evaluate(() => (window as unknown as { __sendNext: () => number }).__sendNext());
        await expect(more).toHaveCount(0);
        await expect(cards.last()).toHaveAttribute("aria-label", `Trade ${count} of ${count}`);
        await expect(page.getByRole("region", { name: "Finding Trades" })).toBeVisible();
        await page.evaluate(() => (window as unknown as { __sendNext: () => number }).__sendNext());
        await expect(page.getByRole("button", { name: `Close, but not sent · ${DOC.near.length}` })).toBeVisible();
        await expect(cards).toHaveCount(count);
        await expect(cards.first().getByRole("button", { name: "See the Full Result" })).toBeEnabled();
        await expectNoOverlap(page);
        await page.screenshot({ path: info.outputPath(`stream-last-card-${theme}.png`), fullPage: true });
      });

      // A card opens its Full Result with a pushed entry, so the back gesture returns to the same cards and the near
      // fold, and the card that opened sits in view.
      test(`back from a Full Result returns to the cards, the near fold, and the opened card, ${theme}`, async ({ page }, info) => {
        test.skip(!["iPhone 15 390x660", "desktop 1280x800"].includes(viewport.name), "the phone and the desktop only");
        await openFinder(page, theme, true);
        const cards = page.getByRole("article");
        // Each part comes at the call: the trades, the end of the picks, and the answer.
        while ((await page.evaluate(() => (window as unknown as { __sendNext: () => number }).__sendNext())) > 0);
        const fold = page.getByRole("button", { name: `Close, but not sent · ${DOC.near.length}` });
        await expect(fold).toBeVisible();
        await expect(cards).toHaveCount(DOC.trades.length);
        const last = cards.last();
        await last.getByRole("button", { name: "See the Full Result" }).click();
        await expect(page.getByRole("region", { name: "The Read" })).toBeVisible();
        await expect(page.getByRole("button", { name: "Back to trade ideas" })).toBeVisible();
        await page.screenshot({ path: info.outputPath(`full-result-back-button-${theme}.png`) });
        await expectNoOverlap(page);
        await page.goBack();
        await expect(cards).toHaveCount(DOC.trades.length);
        await expect(fold).toBeVisible();
        await expect(page.getByRole("region", { name: "The Read" })).toHaveCount(0);
        // The opened card is in view after the scroll, and the page holds the address of Find.
        await expect.poll(async () => {
          const box = (await last.boundingBox())!;
          return box.y >= 0 && box.y < viewport.use.viewport.height;
        }).toBe(true);
        expect(page.url()).toContain("mode=find");
        await page.screenshot({ path: info.outputPath(`back-to-cards-${theme}.png`) });
        await expectNoOverlap(page);
        // The button does the same as the gesture.
        await last.getByRole("button", { name: "See the Full Result" }).click();
        await page.getByRole("button", { name: "Back to trade ideas" }).click();
        await expect(cards).toHaveCount(DOC.trades.length);
        await expect(fold).toBeVisible();
      });

      for (const motion of ["no-preference", "reduce"] as const) {
        // On a fixed clock, step 5 names each Shortlist trade in turn on one line of the wait.
        test(`step 5 names each Shortlist trade on one line, motion ${motion}, ${theme} (AT-36, AT-73)`, async ({ page }, info) => {
          await page.emulateMedia({ reducedMotion: motion });
          await openFinder(page, theme, true, true);
          const status = page.getByRole("status");
          // The stream sends steps 1 to 4 at once, and each line still holds 1.5 s on the screen, then gives way.
          await expect(status).toHaveText(`1 of 5 · Reading ${PARTNERS} teams`);
          for (const line of ["2 of 5 · Matching trade value", "3 of 5 · Checking 4,667 trades for fairness", "4 of 5 · Checking 77 against both lineups", "5 of 5 · Picking the best 5"]) {
            await page.clock.runFor(1400);
            await expect(status).not.toHaveText(line);
            await page.clock.runFor(100);
            await expect(status).toHaveText(line);
          }
          const seen: string[] = [];
          const fits: string[] = [];
          // The step 5 line holds 1.5 s, as each step line does, and then each trade line holds 3 s (V2).
          await page.clock.runFor(1400);
          await expect(status).toHaveText("5 of 5 · Picking the best 5");
          for (let turn = 0; turn < SHORTLIST.length + 1; turn++) {
            await page.clock.runFor(turn === 0 ? 100 : 3000);
            // The page renders the new line after the timer fires, so the read waits for the line to change.
            await expect(status).not.toHaveText(seen.at(-1) ?? "5 of 5 · Picking the best 5");
            const text = (await status.textContent())!;
            seen.push(text);
            // Each line names one Shortlist trade by its players, in the order of the Shortlist, and loops at the end.
            const item = SHORTLIST[turn % SHORTLIST.length];
            expect(text).toMatch(/^Weighing .+ for .+$/);
            for (const player of [...item.gives, ...item.gets]) expect(text).toContain(player.last);
            // The line on the screen is the line of the status. A line by full names fits its box. A longer line takes
            // the last names. A line that still runs past the box scrolls once to its end with motion on, and wraps in
            // full with motion off, so no line runs past the hero and no text overlaps.
            const think = page.locator(".t-think").first();
            await expect(think.locator(".t-think-text").last()).toHaveText(text);
            const fit = await think.evaluate((box) => {
              const line = box.querySelectorAll<HTMLElement>(".t-think-text");
              const live = line[line.length - 1];
              return { room: box.clientWidth, width: live.scrollWidth, scrolls: live.classList.contains("is-scroll"), height: live.getBoundingClientRect().height, lineHeight: parseFloat(getComputedStyle(live).lineHeight) };
            });
            const full = [...item.gives, ...item.gets].every((player) => text.includes(player.name));
            if (full) expect(fit.width, `"${text}" fits the line`).toBeLessThanOrEqual(fit.room + 1);
            if (motion === "no-preference") {
              expect(fit.width <= fit.room + 1 || fit.scrolls, `"${text}" fits or scrolls`).toBe(true);
              expect(fit.height, `"${text}" sits on one line`).toBeLessThan(fit.lineHeight * 1.5);
            }
            fits.push(`${fit.width}/${fit.room}${fit.scrolls ? " scrolls" : ""}`);
            await expectNoOverlap(page);
            if (turn < 2 && motion === "no-preference") {
              // The swap of the line ends after its release timer, so the shot waits for the line to rest. It stays
              // well inside the hold of 3 s, so the next turn still reads the next line.
              await page.clock.runFor(400);
              await page.screenshot({ path: info.outputPath(`step-5-line-${turn + 1}-${theme}.png`) });
            }
          }
          console.log(`${viewport.name} ${theme} ${motion}: ${seen.map((text, i) => `${text} [${fits[i]}]`).join(" | ")}`);
          // The first card stops the lines: the wait goes back to the step line and holds.
          await page.evaluate(() => (window as unknown as { __sendNext: () => number }).__sendNext());
          await expect(page.getByRole("article")).toHaveCount(1);
          await expect(status).toHaveText("5 of 5 · Picking the best 5");
          await page.clock.runFor(9000);
          await expect(status).toHaveText("5 of 5 · Picking the best 5");
        });
      }

      // It checks the columns of each shape, the gap line, the fold, no text overlap, no sideways scroll, and no fixed
      // bar over content.
      test(`the Ledger cards and the near fold, with no overlap and no fixed bar over content, ${theme} (AT-65, AT-66, AT-67)`, async ({ page }, info) => {
        await openFinder(page, theme);
        const cards = page.getByRole("article");
        // Each card is a Ledger: the two columns with their counts, a total under each, and the gap line.
        const shapes = new Set<string>();
        for (const card of await cards.all()) {
          const get = (await card.getByText(/^You get · \d$/).textContent())!.split("· ")[1];
          const give = (await card.getByText(/^You give · \d$/).textContent())!.split("· ")[1];
          shapes.add(`${give}-for-${get}`);
          await expect(card.locator("[data-total]")).toHaveCount(2);
          await expect(card.locator("[data-gap]")).toHaveText(/^(You get \d+% more trade value|You give \d+% more trade value|Even in trade value)$/);
        }
        console.log(`${viewport.name} ${theme}: shapes ${[...shapes].join(", ")}`);
        expect(shapes.size, "the picks hold at least two shapes").toBeGreaterThanOrEqual(2);
        await page.screenshot({ path: info.outputPath(`ledger-${theme}.png`), fullPage: true });

        // The near fold sits after the last card, closed, then opens on a tap.
        const fold = page.getByRole("button", { name: `Close, but not sent · ${DOC.near.length}` });
        await expect(fold).toHaveAttribute("aria-expanded", "false");
        await fold.click();
        await expect(fold).toHaveAttribute("aria-expanded", "true");
        await page.screenshot({ path: info.outputPath(`ledger-near-open-${theme}.png`), fullPage: true });

        // No text of the page overlaps another, and the page never scrolls sideways. A fixed or sticky bar sits over
        // content that the reader scrolls past, so the text scan hides each one, and the check below covers the bars.
        const hidden = await page.evaluate(() => {
          const bars = [...document.querySelectorAll<HTMLElement>("body *")].filter((el) => ["fixed", "sticky"].includes(getComputedStyle(el).position));
          for (const bar of bars) bar.style.visibility = "hidden";
          return bars.length;
        });
        console.log(`${viewport.name} ${theme}: the text scan hides ${hidden} fixed or sticky parts`);
        expect(await findOverlap(page)).toBeNull();
        await page.evaluate(() => {
          for (const el of document.querySelectorAll<HTMLElement>("body *")) if (el.style.visibility === "hidden") el.style.visibility = "";
        });
        expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);

        // At the end of the page, no fixed bar covers the last card, the fold, or the open ideas.
        await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
        const parts = [cards.last(), fold, page.getByRole("button", { name: /Close, but not sent/ }).locator("xpath=../..")];
        for (const bar of await fixedBars(page)) {
          for (const part of parts) {
            const box = (await part.boundingBox())!;
            const top = Math.max(box.y, 0);
            const bottom = Math.min(box.y + box.height, viewport.use.viewport.height);
            if (bottom <= top) continue;
            const across = Math.min(box.x + box.width, bar.right) - Math.max(box.x, bar.left);
            const down = Math.min(bottom, bar.bottom) - Math.max(top, bar.top);
            // A bar at the top of the screen sits over content that scrolled up past it, which the reader can scroll back.
            if (bar.top < 1) continue;
            expect(across > 0 && down > 0, `the fixed part ${bar.name} covers a part of the result`).toBe(false);
          }
        }
      });
    }
  });
}
