/**
 * The readability floor on the static export in out/ of the current CLIENT. Run it after pnpm build, with the same CLIENT.
 * The full floor runs on the pages of FULL_FLOOR_PAGES, and a fast sweep runs on every other built page.
 */
import type { Theme } from "@cpc/design/lib/theme";
import { expect, test, type Page } from "@playwright/test";
import { existsSync, readdirSync } from "node:fs";
import { join, relative, sep } from "node:path";
import { openPage, scanContrast, scanScroll, scanTargets, scanText } from "./floor";
import { serveDir } from "./serve";

// check:floor runs in apps/site, as pnpm runs each script of the site there.
const OUT = join(process.cwd(), "out");
const CLIENT = process.env.CLIENT ?? "cpc";

/* The route of the 404 page: a path that no page has. builtRoutes lists it when the export holds 404.html. */
const NOT_FOUND_ROUTE = "/404-floor-check/";

/*
 * An open state of a page: the page after one tap on the element that the CSS selector names, such as an open card or an open strip.
 * The floor taps it after the load, and the run has reduced motion, so the open part is at rest at once.
 * A scope, a CSS selector of the open part, limits the contrast scan to that part. An open part that covers the page
 * hides the text under it from axe, and the closed page has its own entry in the full floor.
 */
type OpenState = { route: string; tap: string; scope?: string };

/* The route of the latest week: the last week page of the export, as the routes sort by season and then by week. */
const LATEST_WEEK_ROUTE = builtRoutes().filter((route) => /^\/\d{4}\/week-\d{2}\/$/.test(route)).at(-1) ?? "/no-week/";

/*
 * The pages and the open states of the full floor: all four rules, in both themes, at both widths.
 * A page not in the list, such as a past week, gets the fast sweep only, so it still has the text floor.
 */
const FULL_FLOOR_PAGES: readonly (string | OpenState)[] = [
  NOT_FOUND_ROUTE,
  "/rankings/",
  // The card at rank 2 is the first card of the Ladder, because rank 1 sits in the hero.
  { route: "/rankings/", tap: "main ol > li:first-child button[aria-expanded]" },
  "/2026/managers/",
  // The manager page of the longest team name of each client: To Infinity and Bijan of cpc, The Mean Machine of norcal.
  // In cpc, rosters 7, 9, and 11 tie at 21 characters, and roster 7 stands for the three.
  // Both clients build both roster ids, so each client checks both pages.
  "/2026/managers/7/",
  "/2026/managers/4/",
  "/analyze/",
  LATEST_WEEK_ROUTE,
  // The open recap of game 3 of the latest week. Each game card button controls the recap panel of its game.
  { route: LATEST_WEEK_ROUTE, tap: 'button[aria-controls="recap-3"]' },
  "/",
  // The open strip of weeks: a tap on the week chip of the top band opens the strip of the weeks of the season.
  { route: "/", tap: "header details > summary", scope: 'header nav[aria-label="Weeks of the season"]' },
];

const routeOf = (entry: string | OpenState) => (typeof entry === "string" ? entry : entry.route);
const fullFloorRoutes = FULL_FLOOR_PAGES.map(routeOf);

/* Every client has both sets (decision 12), so the full floor checks both themes. */
const THEMES: readonly Theme[] = ["dark", "light"];
const PHONE = { width: 390, height: 844 };
const DESKTOP = { width: 1280, height: 800 };

/*
 * The route of each built page. The folders _not-found/ and 404/ hold copies of 404.html, so the list skips them.
 * The route of 404.html is a path that does not exist, so the server gives the page with its real status, as the Worker does.
 */
function builtRoutes(): string[] {
  if (!existsSync(OUT)) throw new Error(`${OUT} does not exist. Run CLIENT=${CLIENT} pnpm build first.`);
  const routes: string[] = [];
  const walk = (dir: string) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const path = join(dir, entry.name);
      if (entry.isDirectory()) {
        if (!["_next", "_not-found", "404"].includes(entry.name) || dir !== OUT) walk(path);
      } else if (entry.name === "index.html") {
        const folder = relative(OUT, dir).split(sep).join("/");
        routes.push(folder ? `/${folder}/` : "/");
      }
    }
  };
  walk(OUT);
  if (existsSync(join(OUT, "404.html"))) routes.push(NOT_FOUND_ROUTE);
  return routes.sort();
}

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

/* Runs the text scan, and prints the count of each tier and the time of the page, so a slow page shows in the log. */
async function textFloor(page: Page, label: string, started: number): Promise<string[]> {
  const scan = await scanText(page);
  const scroll = await scanScroll(page);
  console.log(`${label}: prose ${scan.prose}, other text ${scan.other}, in ${Date.now() - started} ms`);
  return [...scan.failures, ...scroll];
}

const routes = builtRoutes();
const unknown = fullFloorRoutes.filter((route) => !routes.includes(route));
test("each page of the full floor is a built page", () => {
  expect(unknown, `FULL_FLOOR_PAGES names a page that ${CLIENT} does not build`).toEqual([]);
});

/* No client takes the waiver package, so no client builds a waiver page, even where the week publishes a waiver file.
   The URL of the waiver page of the latest week then gives the 404 page, as the Worker does. */
test("no waiver page is built, and its URL shows the 404 page", async ({ page }) => {
  expect(routes.filter((route) => route.includes("waiver"))).toEqual([]);
  const response = await page.goto(`${server.url}${LATEST_WEEK_ROUTE}waiver/`);
  expect(response?.status()).toBe(404);
  await expect(page.getByText("ERROR // PAGE NOT FOUND")).toBeVisible();
});

for (const entry of FULL_FLOOR_PAGES) {
  const route = routeOf(entry);
  const state = typeof entry === "string" ? "" : ` tap ${entry.tap}`;
  for (const theme of THEMES) {
    for (const size of [PHONE, DESKTOP]) {
      test(`full floor: ${CLIENT} ${route}${state} ${theme} ${size.width}px`, async ({ page }) => {
        const label = `${CLIENT} ${route}${state} ${theme} ${size.width}px`;
        const started = Date.now();
        await page.setViewportSize(size);
        await openPage(page, `${server.url}${route}`, theme);
        if (typeof entry !== "string") {
          const control = page.locator(entry.tap);
          await control.click();
          // A tap that opens nothing fails here, so the floor never checks a closed state by mistake.
          // A button shows its open state with aria-expanded, and a summary shows it with the open attribute of its details.
          await expect
            .poll(() =>
              control.evaluate((el) =>
                el.tagName === "SUMMARY" ? el.parentElement?.hasAttribute("open") === true : el.getAttribute("aria-expanded") === "true",
              ),
            )
            .toBe(true);
        }
        const failures = await textFloor(page, label, started);
        const targets = await scanTargets(page);
        for (const link of targets.exempt) console.log(`${label}: exempt link inside prose: ${link}`);
        failures.push(...targets.failures, ...(await scanContrast(page, typeof entry === "string" ? undefined : entry.scope)));
        expect(failures, `${label} breaks the readability floor`).toEqual([]);
      });
    }
  }
}

for (const route of routes.filter((route) => !fullFloorRoutes.includes(route))) {
  test(`fast sweep: ${CLIENT} ${route} dark 390px`, async ({ page }) => {
    const label = `${CLIENT} ${route} dark 390px`;
    const started = Date.now();
    await page.setViewportSize(PHONE);
    await openPage(page, `${server.url}${route}`, "dark");
    expect(await textFloor(page, label, started), `${label} breaks the readability floor`).toEqual([]);
  });
}
