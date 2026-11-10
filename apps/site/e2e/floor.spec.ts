/**
 * The readability floor on the static export in out/ of the current CLIENT. Run it after pnpm build, with the same CLIENT.
 * The full floor runs on the pages of FULL_FLOOR_PAGES, and a fast sweep runs on every other built page.
 * A check of the shell reads the top band at the tablet and desktop widths between the two widths of the floor.
 */
import type { Theme } from "@cpc/design/lib/theme";
import { expect, test, type Page } from "@playwright/test";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join, relative, sep } from "node:path";
import { openPage, scanContrast, scanScroll, scanTargets, scanText, scanWords } from "./floor";
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

/* The season of the latest week, from its route. The managers index and the manager pages sit under it. */
const SEASON = LATEST_WEEK_ROUTE.split("/")[1];

/*
 * The manager page of the longest team name of the client, from the managers file of the export: the page where a long
 * name most likely breaks the floor. A tie goes to the lowest roster id, so the choice is the same at each run.
 * The name counts in code points, so an emoji counts as one character.
 */
function longestNameRoute(): string {
  const path = join(OUT, SEASON, "managers.json");
  if (!existsSync(path)) return "/no-managers-file/";
  const { managers } = JSON.parse(readFileSync(path, "utf8")) as { managers: { roster_id: number; team: { name: string } }[] };
  const length = (name: string) => [...name].length;
  const [longest] = [...managers].sort((a, b) => length(b.team.name) - length(a.team.name) || a.roster_id - b.roster_id);
  return `/${SEASON}/managers/${longest.roster_id}/`;
}

/*
 * The pages and the open states of the full floor: all four rules, in both themes, at both widths.
 * The spec names 7 pages and 4 open states per client. The home page is one of the 7 pages, and it shows the sheet of
 * Your team on a first visit. The open strip of weeks is a tap on the latest week page. The Season So Far dial sits on the manager page of the list, so that page covers it.
 * A page not in the list, such as a past week, gets the fast sweep only, so it still has the text floor.
 */
const FULL_FLOOR_PAGES: readonly (string | OpenState)[] = [
  NOT_FOUND_ROUTE,
  "/rankings/",
  // The card at rank 2 is the first card of the Ladder, because rank 1 sits in the hero. The chevron has its own label, so the selector names the head.
  { route: "/rankings/", tap: "main ol > li:first-child button[aria-expanded]:not([aria-label])" },
  `/${SEASON}/managers/`,
  // The open first row of the Index list. The row name of each closed row is muted, so axe reads it beside the open row.
  { route: `/${SEASON}/managers/`, tap: 'ul[aria-label="Index List"] > li:first-child > button[aria-expanded]' },
  // The manager page of the longest team name of the client: To Infinity and Bijan of cpc, The Mean Machine of norcal.
  // In cpc, rosters 7, 9, and 11 tie at 21 characters, and roster 7 stands for the three.
  longestNameRoute(),
  "/analyze/",
  LATEST_WEEK_ROUTE,
  // The open recap of game 3 of the latest week. The head button and the chevron of each game card control the recap
  // panel of its game. The chevron has its own label, so the selector names the head.
  { route: LATEST_WEEK_ROUTE, tap: 'button[aria-controls="recap-3"]:not([aria-label])' },
  "/",
  // The open strip of weeks: a tap on the week chip of the top band opens the strip of the weeks of the season. The
  // sheet of Your team covers the band of the home page on a first visit, so the tap opens the strip on the latest week.
  { route: LATEST_WEEK_ROUTE, tap: "header details > summary", scope: 'header nav[aria-label="Weeks of the season"]' },
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
/* The spec of the floor names 7 pages and 4 open states per client: home, the latest week, rankings, the managers index,
   the manager page with the longest team name, the empty analyzer, and 404, then an open game card, ladder card,
   Index list row, and strip. */
test("the full floor holds the 7 pages and the 4 open states of the spec", () => {
  const pages = FULL_FLOOR_PAGES.filter((entry) => typeof entry === "string");
  expect(new Set(pages).size).toBe(pages.length);
  expect(pages.length).toBe(7);
  expect(FULL_FLOOR_PAGES.length - pages.length).toBe(4);
});

test("no waiver page is built, and its URL shows the 404 page", async ({ page }) => {
  expect(routes.filter((route) => route.includes("waiver"))).toEqual([]);
  const response = await page.goto(`${server.url}${LATEST_WEEK_ROUTE}waiver/`);
  expect(response?.status()).toBe(404);
  await expect(page.getByRole("heading", { level: 1, name: "Page not found" })).toBeVisible();
});

/* The ink copy of each rolled letter of the Index list is CSS content with empty alt text, so a screen reader hears each
   name once. A minifier that drops the alt text form would make each name read twice, so the check reads the built CSS. */
test("the built CSS keeps the empty alt text of the rolled letters of the Index list", () => {
  const files: string[] = [];
  const walk = (dir: string) => {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const path = join(dir, entry.name);
      if (entry.isDirectory()) walk(path);
      else if (entry.name.endsWith(".css")) files.push(path);
    }
  };
  walk(join(OUT, "_next"));
  const css = files.map((path) => readFileSync(path, "utf8")).join("\n");
  expect(css).toMatch(/content:\s*attr\(data-ch\)\s*\/\s*""/);
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
        // Each exempt link prints, so a reader of the log sees each link that the tap floor skips. A page with none says so.
        if (targets.exempt.length === 0) console.log(`${label}: exempt links inside prose: none`);
        for (const link of targets.exempt) console.log(`${label}: exempt link inside prose: ${link}`);
        failures.push(...targets.failures, ...(await scanContrast(page, typeof entry === "string" ? undefined : entry.scope)));
        expect(failures, `${label} breaks the readability floor`).toEqual([]);
      });
    }
  }
}

/* The managers index and the row heads of its Index list. The stage of the list shows from the desktop tier only. */
const MANAGERS_ROUTE = `/${SEASON}/managers/`;
const INDEX_ROW = 'ul[aria-label="Index List"] > li';

/* The stage on desktop: the full floor after a hover on the second row swaps the stage, in both themes at 1280px.
   The run has reduced motion, so the new row is in the stage at once, with no layer under it. */
for (const theme of THEMES) {
  test(`stage floor: ${CLIENT} ${MANAGERS_ROUTE} hover on row 2 ${theme} 1280px`, async ({ page }) => {
    const label = `${CLIENT} ${MANAGERS_ROUTE} stage ${theme} 1280px`;
    const started = Date.now();
    await page.setViewportSize(DESKTOP);
    await openPage(page, `${server.url}${MANAGERS_ROUTE}`, theme);
    const second = page.locator(`${INDEX_ROW}:nth-child(2)`);
    await second.hover();
    const name = (await second.locator(".ix-name").textContent())!;
    await expect(page.getByRole("region", { name: `Stage: ${name}` })).toBeVisible();
    const failures = await textFloor(page, label, started);
    failures.push(...(await scanTargets(page)).failures, ...(await scanContrast(page)));
    expect(failures, `${label} breaks the readability floor`).toEqual([]);
  });
}

/* AT-25: a hover on row 5 and then a focus on row 6 each swap the stage beside the ledger. In cpc week 8 these are
   The Blue Tent and Lil Fridge. The stage holds the six hero slots. */
test(`stage swap: ${CLIENT} ${MANAGERS_ROUTE} on a hover and a focus at 1280px`, async ({ page }) => {
  await page.setViewportSize(DESKTOP);
  await openPage(page, `${server.url}${MANAGERS_ROUTE}`, "dark");
  const stage = () => page.getByRole("region", { name: /^Stage: / });
  for (const [n, act] of [
    [5, "hover"],
    [6, "focus"],
  ] as const) {
    const row = page.locator(`${INDEX_ROW}:nth-child(${n})`);
    const head = row.locator("button[aria-expanded]");
    await (act === "hover" ? head.hover() : head.focus());
    const name = (await row.locator(".ix-name").textContent())!;
    await expect(stage()).toHaveAttribute("aria-label", `Stage: ${name}`);
    await expect(stage().locator('[data-hero-slot="title"]')).toHaveText(name);
  }
  const slots = await stage().locator("[data-hero-slot]").evaluateAll((els) => els.map((el) => el.getAttribute("data-hero-slot")));
  expect(slots).toEqual(["eyebrow", "title", "meta", "feature", "stats", "action"]);
  // The stage sits beside the ledger, to the right of it, and stays in view as the page scrolls.
  const ledger = (await page.locator('ul[aria-label="Index List"]').boundingBox())!;
  const box = (await page.locator("[data-ix-stage]").boundingBox())!;
  expect(box.x).toBeGreaterThanOrEqual(ledger.x + ledger.width);
  expect(await page.locator("[data-ix-stage]").evaluate((el) => getComputedStyle(el).position)).toBe("sticky");
});

/* Under the desktop tier the Index list is the ledger alone, with no stage. */
for (const width of [390, 768]) {
  test(`no stage: ${CLIENT} ${MANAGERS_ROUTE} shows the ledger alone at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await openPage(page, `${server.url}${MANAGERS_ROUTE}`, "dark");
    await expect(page.getByRole("list", { name: "Index List" })).toBeVisible();
    await expect(page.locator("[data-ix-stage]")).toBeHidden();
  });
}

/* The widths of the word check: a phone, a tablet, and a laptop. The tiles of the week page change columns between them. */
const WORD_WIDTHS = [375, 768, 1280] as const;

/* No label, number, or name of the latest week splits inside a word, such as "UNDERPERF" over "ORMER", at any width. */
for (const width of WORD_WIDTHS) {
  test(`no split word: ${CLIENT} ${LATEST_WEEK_ROUTE} ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await openPage(page, `${server.url}${LATEST_WEEK_ROUTE}`, "dark");
    expect(await scanWords(page), `${CLIENT} ${LATEST_WEEK_ROUTE} ${width}px splits a word`).toEqual([]);
  });
}

/* The marked link of the chapter rail. The rail shows from the rail tier, so the checks run at the laptop width. */
const railMark = (page: Page) => page.locator('nav[aria-label="Chapters"] a[aria-current="location"]');

/* The rail marks the chapter that a reader reads, not the one whose tail still sits under the top band.
   The scroll puts the heading of Position leaders 80px under the top band, as after a scroll past Awards. */
test(`chapter rail: ${CLIENT} ${LATEST_WEEK_ROUTE} marks Position leaders in view at 1280px`, async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await openPage(page, `${server.url}${LATEST_WEEK_ROUTE}`, "dark");
  await page.evaluate(() => {
    const leaders = document.getElementById("leaders")!;
    const bar = parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop);
    window.scrollTo(0, window.scrollY + leaders.getBoundingClientRect().top - bar - 80);
  });
  await expect(railMark(page)).toHaveText("Position leaders");
});

/* A tap on each rail link jumps to its chapter and marks that link. */
test(`chapter rail: ${CLIENT} ${LATEST_WEEK_ROUTE} marks each chapter after a jump at 1280px`, async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await openPage(page, `${server.url}${LATEST_WEEK_ROUTE}`, "dark");
  const links = page.locator('nav[aria-label="Chapters"] a');
  const labels = await links.allTextContents();
  for (const label of labels) {
    await links.filter({ hasText: label }).click();
    await expect(railMark(page)).toHaveText(label);
  }
});

for (const route of routes.filter((route) => !fullFloorRoutes.includes(route))) {
  test(`fast sweep: ${CLIENT} ${route} dark 390px`, async ({ page }) => {
    const label = `${CLIENT} ${route} dark 390px`;
    const started = Date.now();
    await page.setViewportSize(PHONE);
    await openPage(page, `${server.url}${route}`, "dark");
    expect(await textFloor(page, label, started), `${label} breaks the readability floor`).toEqual([]);
  });
}

/*
 * The shell at the widths between the two of the floor. The top band is one row at every width.
 * On a tablet the dock holds the destinations. From the desktop tier the pill bar holds them with full labels on the row.
 */
const bandRow = async (page: Page) => {
  const parts = [
    page.locator("header > div > a").first(),
    page.locator("header details > summary"),
    page.getByRole("button", { name: /theme/i }),
  ];
  const bar = page.getByRole("navigation", { name: "Site menu" });
  if (await bar.isVisible()) parts.push(bar);
  const boxes = await Promise.all(parts.map((part) => part.boundingBox()));
  const brand = boxes[0]!;
  // Each part shares the row of the brand mark: the middle of each part sits inside the box of the mark.
  return boxes.map((box) => box !== null && Math.abs(box.y + box.height / 2 - (brand.y + brand.height / 2)) < brand.height / 2);
};

for (const width of [768, 1024, 1280]) {
  const pills = width >= 1024;
  test(`the top band of ${CLIENT} is one row at ${width}px, with the ${pills ? "pill bar" : "dock"}`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await openPage(page, `${server.url}/rankings/`, "dark");
    const bar = page.getByRole("navigation", { name: "Site menu" });
    const dock = page.getByRole("navigation", { name: "Bottom menu" });
    await expect(pills ? bar : dock).toBeVisible();
    await expect(pills ? dock : bar).toBeHidden();
    expect(await bandRow(page)).toEqual(pills ? [true, true, true, true] : [true, true, true]);
    // The pill bar shows each full label with no scroll of its own.
    if (pills) expect(await bar.evaluate((el) => el.scrollWidth <= el.clientWidth)).toBe(true);
    const targets = await scanTargets(page);
    expect([...targets.failures, ...(await scanScroll(page))]).toEqual([]);
  });
}

/* The open strip of weeks takes its own space under the top band, so it covers no part of the page, such as the page title. */
for (const width of [375, 768, 1280]) {
  test(`the open strip of weeks of ${CLIENT} covers no page title at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    await openPage(page, `${server.url}/`, "dark");
    await page.locator("header details > summary").click();
    const strip = await page.getByRole("navigation", { name: "Weeks of the season" }).boundingBox();
    const title = await page.locator("h1").first().boundingBox();
    expect(strip).not.toBeNull();
    expect(title).not.toBeNull();
    expect(strip!.y + strip!.height).toBeLessThanOrEqual(title!.y);
  });
}

/* The week chips of the Ladder stay on one row at a phone width. A long season scrolls inside the row, not the page,
   and the chosen week shows in full. */
test(`the week chips of the Ladder of ${CLIENT} stay on one row at 375px`, async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 900 });
  await openPage(page, `${server.url}/rankings/`, "dark");
  const group = page.getByRole("group", { name: "Week" });
  const chips = await group.getByRole("button").evaluateAll((els) => els.map((el) => el.getBoundingClientRect().top));
  expect(chips.length).toBeGreaterThan(1);
  expect(new Set(chips).size).toBe(1);
  const chosen = await group.locator('button[aria-pressed="true"]').boundingBox();
  const box = await group.boundingBox();
  expect(chosen!.x).toBeGreaterThanOrEqual(box!.x);
  expect(chosen!.x + chosen!.width).toBeLessThanOrEqual(box!.x + box!.width);
  expect(await scanScroll(page)).toEqual([]);
});

/* The midseason report of the latest season. A client builds it only when it takes midseason and the season has a
   published midseason file, so each check of the report skips a client with no report page. */
const MIDSEASON_ROUTE = `/midseason/${SEASON}/`;
const hasReport = routes.includes(MIDSEASON_ROUTE);

/* The widths of the report: a phone, a tablet, and a laptop (ticket 11 of midseason-report). */
const REPORT_WIDTHS = [375, 768, 1280] as const;

for (const theme of THEMES) {
  for (const width of REPORT_WIDTHS) {
    test(`midseason floor: ${CLIENT} ${MIDSEASON_ROUTE} ${theme} ${width}px`, async ({ page }) => {
      test.skip(!hasReport, `${CLIENT} builds no midseason report`);
      const label = `${CLIENT} ${MIDSEASON_ROUTE} ${theme} ${width}px`;
      await page.setViewportSize({ width, height: 900 });
      await openPage(page, `${server.url}${MIDSEASON_ROUTE}`, theme);
      const failures = await textFloor(page, label, Date.now());
      failures.push(...(await scanTargets(page)).failures, ...(await scanWords(page)), ...(await scanContrast(page)));
      expect(failures, `${label} breaks the readability floor`).toEqual([]);
    });

    /* AT-27: from Act II, a tap on "What Comes Next" in the rail moves the page to Act III, and the rail stays at the top. */
    test(`midseason rail: ${CLIENT} ${MIDSEASON_ROUTE} jumps to Act III and stays at the top, ${theme} ${width}px`, async ({ page }) => {
      test.skip(!hasReport, `${CLIENT} builds no midseason report`);
      await page.setViewportSize({ width, height: 900 });
      await openPage(page, `${server.url}${MIDSEASON_ROUTE}`, theme);
      const rail = page.getByRole("navigation", { name: "Chapters" });
      const railTop = (await rail.boundingBox())!.y;
      await page.evaluate(() => document.getElementById("the-moves")!.scrollIntoView());
      await rail.getByRole("link", { name: "What Comes Next" }).click();
      const box = await rail.boundingBox();
      const title = await page.getByRole("heading", { level: 2, name: "What Comes Next" }).boundingBox();
      // The rail sits under the top band at every scroll, and the title of Act III sits just under the rail.
      expect(box!.y).toBe(railTop);
      expect(title!.y).toBeGreaterThanOrEqual(box!.y + box!.height);
      expect(title!.y).toBeLessThan(900 / 2);
    });
  }
}

/* AT-59 and AT-8: the schedule swap is one text row per team with no grid and no bar, and the page never says
   "All-play" (decision ticket 16). */
for (const width of REPORT_WIDTHS) {
  test(`midseason swap rows: ${CLIENT} ${MIDSEASON_ROUTE} text rows and no All-play, ${width}px`, async ({ page }) => {
    test.skip(!hasReport, `${CLIENT} builds no midseason report`);
    await page.setViewportSize({ width, height: 900 });
    await openPage(page, `${server.url}${MIDSEASON_ROUTE}`, "dark");
    const swap = page.getByRole("list", { name: "Schedule swap" });
    await expect(swap.getByRole("listitem")).not.toHaveCount(0);
    await expect(swap.locator("table, svg, [role=meter], [role=progressbar]")).toHaveCount(0);
    await expect(page.getByRole("table", { name: "Schedule swap" })).toHaveCount(0);
    expect(await page.locator("body").innerText()).not.toMatch(/all-play/i);
  });
}

/* AT-28: on a phone, each shown table of the report fits its card, or its card scrolls it and the first cell of each
   row stays in place. The page itself never scrolls sideways. */
test(`midseason tables: ${CLIENT} ${MIDSEASON_ROUTE} fit their cards or scroll with the team column fixed, 375px`, async ({ page }) => {
  test.skip(!hasReport, `${CLIENT} builds no midseason report`);
  await page.setViewportSize({ width: 375, height: 900 });
  await openPage(page, `${server.url}${MIDSEASON_ROUTE}`, "dark");
  const failures = await page.locator("main table").evaluateAll((tables) =>
    tables
      .filter((table) => table.getClientRects().length > 0)
      .flatMap((table) => {
        const name = table.getAttribute("aria-label") ?? table.closest("[id]")?.id ?? "a table";
        const card = table.parentElement!;
        if (table.getBoundingClientRect().width <= card.clientWidth + 1) return [];
        if (!["auto", "scroll"].includes(getComputedStyle(card).overflowX)) return [`${name} runs past its card`];
        const first = table.querySelector("tbody tr > :first-child")!;
        const before = first.getBoundingClientRect().left;
        card.scrollLeft = card.scrollWidth;
        const after = first.getBoundingClientRect().left;
        card.scrollLeft = 0;
        return Math.abs(after - before) > 1 ? [`${name} scrolls its team column out of view`] : [];
      }),
  );
  expect(failures).toEqual([]);
  expect(await scanScroll(page)).toEqual([]);
});

/* AT-11: Position top 10 opens on RB and shows one position. */
test(`midseason top 10: ${CLIENT} ${MIDSEASON_ROUTE} opens on RB at 375px`, async ({ page }) => {
  test.skip(!hasReport, `${CLIENT} builds no midseason report`);
  await page.setViewportSize({ width: 375, height: 900 });
  await openPage(page, `${server.url}${MIDSEASON_ROUTE}`, "dark");
  const chapter = page.locator("#top10");
  await expect(chapter.getByRole("button", { name: "RB" })).toHaveAttribute("aria-pressed", "true");
  await expect(chapter.getByRole("list")).toHaveCount(1);
  await expect(chapter.getByRole("list", { name: "RB top 10" })).toBeVisible();
});

/* AT-33: the odds of all runs sit below the replay at every width, and the stage takes the full width of the column.
   Beside the odds on a laptop, the stage had room for one letter of each team name. A report with no sim file has no
   replay, so the check skips it too. */
for (const width of REPORT_WIDTHS) {
  test(`sim odds: ${CLIENT} ${MIDSEASON_ROUTE} below the replay at full width, ${width}px`, async ({ page }) => {
    test.skip(!hasReport, `${CLIENT} builds no midseason report`);
    await page.setViewportSize({ width, height: 900 });
    await openPage(page, `${server.url}${MIDSEASON_ROUTE}`, "dark");
    const stage = page.getByRole("region", { name: "The replay" });
    test.skip((await stage.count()) === 0, `${CLIENT} publishes no sim file`);
    const box = (await stage.boundingBox())!;
    const odds = (await page.getByRole("table", { name: /^The Odds of All/ }).boundingBox())!;
    expect(odds.y).toBeGreaterThanOrEqual(box.y + box.height);
    const column = (await stage.evaluate((el) => el.parentElement!.getBoundingClientRect().width))!;
    expect(box.width).toBeCloseTo(column, 0);
  });
}

/* The text boxes of the bracket that a chip or a cut must never hide: each team name and each score. */
const bracketText = (page: Page) => page.locator('ol[aria-label="Bracket"] [data-team-name], ol[aria-label="Bracket"] [data-score]');

/* Each team name of the bracket shows in full at each width of the report, and the seed chip that waits at the edge of
   a decided card covers no name or score. */
for (const width of REPORT_WIDTHS) {
  test(`sim bracket: ${CLIENT} ${MIDSEASON_ROUTE} shows full team names and no chip on a card, ${width}px`, async ({ page }) => {
    test.skip(!hasReport, `${CLIENT} builds no midseason report`);
    await page.setViewportSize({ width, height: 900 });
    await openPage(page, `${server.url}${MIDSEASON_ROUTE}`, "dark");
    const stage = page.getByRole("region", { name: "The replay" });
    test.skip((await stage.count()) === 0, `${CLIENT} publishes no sim file`);
    await page.getByRole("button", { name: "Sim the season" }).click();
    // Mid-run, after the results of round 1: the winner chips wait at the edge of their cards.
    await expect(stage.getByRole("status")).toHaveText("Round 1 results", { timeout: 30_000 });
    const chips = await stage.locator("[data-departed]").evaluateAll((els) => els.map((el) => el.getBoundingClientRect().toJSON()));
    expect(chips.length).toBeGreaterThan(0);
    const texts = await bracketText(page).evaluateAll((els) => els.map((el) => el.getBoundingClientRect().toJSON()));
    const overlaps = chips.flatMap((chip) =>
      texts.filter((text) => chip.left < text.right && text.left < chip.right && chip.top < text.bottom && text.top < chip.bottom),
    );
    expect(overlaps, `a waiting chip covers a name or a score at ${width}px`).toEqual([]);
    // At rest, after a skip, every name of every round shows in full.
    await page.getByRole("button", { name: "Skip to the end" }).click();
    const cut = await stage
      .locator("[data-team-name]")
      .evaluateAll((els) => els.filter((el) => el.scrollWidth > el.clientWidth + 1).map((el) => el.textContent));
    expect(cut, `the bracket cuts a team name at ${width}px`).toEqual([]);
  });
}

/* The label of the first week of the replay: the first regular week of the sim file of the export. A later sim file
   starts at a later week, so the test reads the week from the file. */
function firstReplayWeek(): string {
  const path = join(OUT, SEASON, "sim.json");
  if (!existsSync(path)) return "no sim file";
  const { weeks, bracket_weeks } = JSON.parse(readFileSync(path, "utf8")) as { weeks: number[]; bracket_weeks: number[] };
  return `Week ${weeks.find((week) => !bracket_weeks.includes(week))} final`;
}

/* AT-32 and AT-34: a press plays a run, and a skip shows the final state at once: the champion card with the title odds
   of all runs, and the complete bracket below it, with no part of the bracket under the card. */
for (const width of [375, 1280]) {
  test(`sim replay: ${CLIENT} ${MIDSEASON_ROUTE} plays a run and skips to the champion and the bracket at ${width}px`, async ({ page }) => {
    test.skip(!hasReport, `${CLIENT} builds no midseason report`);
    await page.setViewportSize({ width, height: 900 });
    await openPage(page, `${server.url}${MIDSEASON_ROUTE}`, "dark");
    const stage = page.getByRole("region", { name: "The replay" });
    test.skip((await stage.count()) === 0, `${CLIENT} publishes no sim file`);
    await page.getByRole("button", { name: "Sim the season" }).click();
    await expect(stage.getByRole("group", { name: firstReplayWeek() })).toBeVisible();
    await page.getByRole("button", { name: "Skip to the end" }).click();
    const card = stage.getByRole("group", { name: "Champion of This Run" });
    await expect(card).toContainText(/Wins the title in [\d.]+% of all [\d,]+ runs/);
    expect(await scanScroll(page)).toEqual([]);
    const rounds = stage.getByRole("list", { name: "Bracket" }).getByRole("listitem");
    await expect(rounds).toHaveCount(3);
    for (const round of await rounds.all()) await expect(round).toBeVisible();
    const cardBox = (await card.boundingBox())!;
    const bracketBox = (await stage.getByRole("list", { name: "Bracket" }).boundingBox())!;
    expect(bracketBox.y, `the champion card covers the bracket at ${width}px`).toBeGreaterThanOrEqual(cardBox.y + cardBox.height);
    // The stage clips its parts, so the whole bracket must sit inside the stage.
    const stageBox = (await stage.boundingBox())!;
    expect(bracketBox.y + bracketBox.height).toBeLessThanOrEqual(stageBox.y + stageBox.height);
    // The trophy sits centered over the avatar of the champion.
    const trophy = (await card.locator("[data-trophy]").boundingBox())!;
    const avatar = (await card.locator("[data-avatar]").boundingBox())!;
    expect(trophy.x + trophy.width / 2).toBeCloseTo(avatar.x + avatar.width / 2, 0);
    expect(trophy.y + trophy.height).toBeLessThanOrEqual(avatar.y + 1);
  });
}
