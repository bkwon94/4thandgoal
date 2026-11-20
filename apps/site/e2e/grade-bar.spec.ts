/**
 * The place of the "Grade the Trade" bar on the analyzer page of a client with the finder on, at the width of a phone.
 * The bar stays pinned at the bottom of the screen over the trade form in Grade mode, and Find mode shows the finder with no bar.
 */
import { expect, test, type Page } from "@playwright/test";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { LOCAL_API } from "./evidence";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");
// Run it on the export of NorCal, the client with the finder on, built against the local API URL:
// CLIENT=norcal NEXT_PUBLIC_API_URL=http://localhost:8080 pnpm build
// The finder document of the analyzer tests, in the exact shape of the API. Its asker is roster 2.
const FIND = readFileSync(join(process.cwd(), "..", "..", "packages", "analyzer", "site", "lib", "fixtures", "find-response.json"), "utf8");
// The find stream of the API: the document of the fixture in its answer part, as one event stream.
const FIND_STREAM = `data: ${JSON.stringify({ type: "data-answer", data: { kind: "find", document: JSON.parse(FIND) } })}\n\ndata: [DONE]\n\n`;
const CORS = { "access-control-allow-origin": "*", "access-control-allow-headers": "*", "access-control-allow-methods": "GET, POST" };

/* The teams of the find fixture: the asker and the partner of the first trade, each with the players it gives. */
function teamsOfFind() {
  const [first] = JSON.parse(FIND).trades;
  const teams = first.sides.map((side: { roster_id: number; team: string; gives: { player_id: string; name: string; position: string; nfl_team: string; headshot: string }[] }) => ({
    roster_id: side.roster_id,
    team: side.team,
    manager: side.team,
    avatar: null,
    players: side.gives.map(({ player_id, name, position, nfl_team, headshot }) => ({ player_id, name, position, nfl_team, headshot })),
  }));
  return JSON.stringify({ teams });
}

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server?.close();
});

test.use({ viewport: { width: 390, height: 600 }, reducedMotion: "reduce" });

/* Opens the analyzer in its first mode, Grade, with Your Team picked. The API answers from the fixtures. */
async function openAnalyzer(page: Page) {
  await page.route((url) => !["127.0.0.1", "localhost"].includes(url.hostname), (route) => route.abort());
  await page.route(`${LOCAL_API}/**`, (route) => {
    const request = route.request();
    if (request.method() === "OPTIONS") return route.fulfill({ status: 204, headers: CORS });
    if (request.url().includes("/find-stream")) return route.fulfill({ status: 200, headers: CORS, contentType: "text/event-stream", body: FIND_STREAM });
    const body = request.url().includes("/teams") ? teamsOfFind() : FIND;
    return route.fulfill({ status: 200, headers: CORS, contentType: "application/json", body });
  });
  await page.addInitScript(() => {
    localStorage.setItem("cpc.passphrase", "test");
    // Your Team of the front door, roster 2, so the form picks it for the first side.
    localStorage.setItem("cpc.your-team", "2");
  });
  await page.goto(`${server.url}/analyze/`);
}

/* Opens the analyzer in Find mode with Your Team picked and the finder showing its three cards. */
async function openFinder(page: Page) {
  await openAnalyzer(page);
  // The analyzer opens in Grade mode. A reader taps "Find a trade" on the switch of the hero to show the finder.
  await page.getByRole("radiogroup", { name: "Mode" }).getByRole("radio", { name: "Find a trade" }).click();
  const find = page.getByRole("button", { name: "Find a Trade" });
  await expect(find).toBeVisible();
  await find.click();
  await expect(page.getByRole("article", { name: "Trade 3" })).toBeAttached();
}

test("the bar covers no part of the finder (grade-bar-finder item 1)", async ({ page }) => {
  await openFinder(page);
  // Find mode takes the place of the form and its bar, so no bar sits over the finder.
  await expect(page.getByRole("button", { name: "Grade the Trade" })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Find a Trade" })).toBeVisible();
  await expect(page.getByRole("article", { name: "Trade 1" })).toBeVisible();
});

test("the bar stays pinned at the bottom of the screen over the top of the form", async ({ page }) => {
  await openAnalyzer(page);
  const grade = page.getByRole("button", { name: "Grade the Trade" });
  await expect(grade).toBeVisible();
  await page.evaluate(() => window.scrollTo(0, 0));
  const bar = await grade.boundingBox();
  expect(bar).not.toBeNull();
  // The bar sits within 40px of the bottom edge of the screen.
  expect(600 - (bar!.y + bar!.height)).toBeLessThan(40);
  expect(bar!.y).toBeGreaterThan(0);
});
