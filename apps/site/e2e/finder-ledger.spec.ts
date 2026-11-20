/**
 * The Ledger cards and the near fold of the Finder, in WebKit, as Safari runs, on the phone, the iPad, and the desktop.
 * It checks the columns of each shape, the gap line, the fold, no text overlap, no sideways scroll, and no fixed bar over content.
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
  near: unknown[];
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

/* Opens the analyzer in Find mode with the asker as Your team, taps Find, and waits for the cards. */
async function openFinder(page: Page, theme: Theme) {
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
  await openPage(page, `${server.url}/analyze/?mode=find`, theme);
  const find = page.getByRole("button", { name: "Find a Trade" });
  await expect(find).toBeVisible();
  await find.click();
  await expect(page.getByRole("article")).toHaveCount(DOC.trades.length);
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
