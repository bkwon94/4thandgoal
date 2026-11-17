/**
 * The frame of each player headshot in the result of the trade analyzer, at the width of a phone.
 * The frame fills its player chip edge to edge, so no strip of the chip shows at the right of the headshot.
 */
import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { LOCAL_API } from "./evidence";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");
// Run it on the export of NorCal built against the local API URL, as the grade-bar project does:
// CLIENT=norcal NEXT_PUBLIC_API_URL=http://localhost:8080 pnpm build
// The analyze document of the analyzer tests, in the exact shape of the API. Its trade has one player on one side and two on the other.
const ANALYZE = readFileSync(join(process.cwd(), "..", "..", "packages", "analyzer", "site", "lib", "fixtures", "analyze-response.json"), "utf8");
const CORS = { "access-control-allow-origin": "*", "access-control-allow-headers": "*", "access-control-allow-methods": "GET, POST" };

type Player = { player_id: string; name: string; position: string; nfl_team: string; headshot: string };

/* The teams of the analyze fixture, each with the players it gives. */
function teamsOfAnalyze() {
  const teams = JSON.parse(ANALYZE).trade.sides.map((side: { roster_id: number; team: string; gives: Player[] }) => ({
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

test.use({ viewport: { width: 390, height: 900 }, reducedMotion: "reduce" });

test("each headshot frame fills its player chip, centered, with no strip at the right (headshot-black-bar item 1)", async ({ page }) => {
  await page.route((url) => !["127.0.0.1", "localhost"].includes(url.hostname), (route) => route.abort());
  await page.route(`${LOCAL_API}/**`, (route) => {
    const request = route.request();
    if (request.method() === "OPTIONS") return route.fulfill({ status: 204, headers: CORS });
    const body = request.url().includes("/teams") ? teamsOfAnalyze() : ANALYZE;
    return route.fulfill({ status: 200, headers: CORS, contentType: "application/json", body });
  });
  await page.addInitScript(() => localStorage.setItem("cpc.passphrase", "test"));
  // The link of the front door names the trade of the fixture, so the form opens filled.
  await page.goto(`${server.url}/analyze/?team=4&with=12&give=7569&get=10236,8146`);
  await page.getByRole("button", { name: "Grade the Trade" }).click();
  await expect(page.getByText("Garrett Wilson").first()).toBeVisible();

  // Each visible chip of the result: the list item that holds a headshot frame on top of the player name.
  const chips = await page.locator("li:has(> img)").evaluateAll((items) =>
    items
      .map((item) => {
        const chip = item.getBoundingClientRect();
        const frame = item.querySelector(":scope > img")!.getBoundingClientRect();
        return { name: item.querySelector("b")?.textContent ?? "", left: frame.left - chip.left, right: chip.right - frame.right };
      })
      .filter((chip) => chip.name !== ""),
  );
  console.log(chips.map((chip) => `${chip.name}: ${chip.left.toFixed(1)}px left gap, ${chip.right.toFixed(1)}px right gap`).join("\n"));
  expect(chips.length).toBeGreaterThan(0);
  for (const chip of chips) {
    expect(chip.left, `${chip.name}: the gap at the left of the frame`).toBeCloseTo(0, 0);
    expect(chip.right, `${chip.name}: the gap at the right of the frame`).toBeCloseTo(0, 0);
  }
});
