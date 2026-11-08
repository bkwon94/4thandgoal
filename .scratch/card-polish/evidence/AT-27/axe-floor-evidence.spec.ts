/**
 * Evidence only for AT-27 of card-polish: the axe scan of each page and open state of the full floor, as one line each.
 * Copy it to apps/site/e2e/ with axe-evidence.config.ts in apps/site/, run it, then delete both copies.
 */
import AxeBuilder from "@axe-core/playwright";
import type { Theme } from "@cpc/design/lib/theme";
import { expect, test } from "@playwright/test";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join, relative, sep } from "node:path";
import { openPage } from "./floor";
import { serveDir } from "./serve";

// The same pages, open states, widths, and themes as FULL_FLOOR_PAGES of e2e/floor.spec.ts, plus the stage state of its stage floor:
// a hover on row 2 of the Index list at 1280 px, in both themes.
const OUT = join(process.cwd(), "out");
const CLIENT = process.env.CLIENT ?? "cpc";
const NOT_FOUND_ROUTE = "/404-floor-check/";
type OpenState = { route: string; tap: string; scope?: string; hover?: boolean; widths?: number[] };

function builtRoutes(): string[] {
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
const LATEST_WEEK_ROUTE = builtRoutes().filter((route) => /^\/\d{4}\/week-\d{2}\/$/.test(route)).at(-1) ?? "/no-week/";
const SEASON = LATEST_WEEK_ROUTE.split("/")[1];
function longestNameRoute(): string {
  const { managers } = JSON.parse(readFileSync(join(OUT, SEASON, "managers.json"), "utf8")) as { managers: { roster_id: number; team: { name: string } }[] };
  const length = (name: string) => [...name].length;
  const [longest] = [...managers].sort((a, b) => length(b.team.name) - length(a.team.name) || a.roster_id - b.roster_id);
  return `/${SEASON}/managers/${longest.roster_id}/`;
}
const PAGES: readonly (string | OpenState)[] = [
  NOT_FOUND_ROUTE,
  "/rankings/",
  { route: "/rankings/", tap: "main ol > li:first-child button[aria-expanded]:not([aria-label])" },
  `/${SEASON}/managers/`,
  { route: `/${SEASON}/managers/`, tap: 'ul[aria-label="Index List"] > li:first-child > button[aria-expanded]' },
  longestNameRoute(),
  "/analyze/",
  LATEST_WEEK_ROUTE,
  { route: LATEST_WEEK_ROUTE, tap: 'button[aria-controls="recap-3"]:not([aria-label])' },
  "/",
  { route: "/", tap: "header details > summary", scope: 'header nav[aria-label="Weeks of the season"]' },
  // The stage on desktop, as the stage floor checks it: a hover on the second row swaps the stage, at 1280 px only.
  { route: `/${SEASON}/managers/`, tap: 'ul[aria-label="Index List"] > li:nth-child(2)', hover: true, widths: [1280] },
];
const THEMES: readonly Theme[] = ["dark", "light"];
const SIZES = [{ width: 390, height: 844 }, { width: 1280, height: 800 }];

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server.close();
});

test(`axe color-contrast of the full floor of ${CLIENT}`, async ({ browser }) => {
  test.setTimeout(0);
  let violations = 0;
  let incomplete = 0;
  let scans = 0;
  for (const entry of PAGES) {
    const route = typeof entry === "string" ? entry : entry.route;
    const state = typeof entry === "string" ? "closed" : `${entry.hover ? "hover" : "tap"} ${entry.tap}`;
    for (const theme of THEMES) {
      for (const size of SIZES.filter((s) => typeof entry === "string" || entry.widths === undefined || entry.widths.includes(s.width))) {
        // axe-core/playwright needs a page of its own context, so each scan opens one.
        const context = await browser.newContext({ viewport: size, reducedMotion: "reduce" });
        const page = await context.newPage();
        await openPage(page, `${server.url}${route}`, theme);
        if (typeof entry !== "string") {
          const control = page.locator(entry.tap);
          if (entry.hover) {
            // The stage floor waits for the stage of the hovered row, as e2e/floor.spec.ts does.
            await control.hover();
            const name = (await control.locator(".ix-name").textContent())!;
            await expect(page.getByRole("region", { name: `Stage: ${name}` })).toBeVisible();
          } else {
          await control.click();
          await expect
            .poll(() => control.evaluate((el) => (el.tagName === "SUMMARY" ? el.parentElement?.hasAttribute("open") === true : el.getAttribute("aria-expanded") === "true")))
            .toBe(true);
          }
        }
        // The same rule as scanContrast of e2e/floor.ts: color-contrast only, limited to the scope of an open state.
        const builder = new AxeBuilder({ page }).withRules(["color-contrast"]);
        const result = await (typeof entry === "string" || entry.scope === undefined ? builder : builder.include(entry.scope)).analyze();
        const v = result.violations.reduce((sum, rule) => sum + rule.nodes.length, 0);
        const i = result.incomplete.reduce((sum, rule) => sum + rule.nodes.length, 0);
        const p = result.passes.reduce((sum, rule) => sum + rule.nodes.length, 0);
        violations += v;
        incomplete += i;
        scans += 1;
        console.log(`${CLIENT} | ${route} | ${state} | ${size.width}px | ${theme} | axe ${result.testEngine.version} color-contrast | violations ${v} | incomplete ${i} | nodes checked with no finding ${p}`);
        for (const rule of [...result.violations, ...result.incomplete]) for (const node of rule.nodes) console.log(`  finding: ${node.target.join(" ")} ${node.failureSummary ?? rule.help}`.replace(/\s+/g, " "));
        await context.close();
      }
    }
  }
  console.log(`${CLIENT} total: ${scans} scans, violations ${violations}, incomplete ${incomplete}`);
});
