/**
 * The evidence runner: it reads each evidence/AT-<n>/steps.json of a feature and takes the shots of each test beside it.
 * It checks every step list before the first shot, so a bad list stops the run with no shot written.
 */
import type { Theme } from "@cpc/design/lib/theme";
import type { Browser, Page } from "@playwright/test";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { openPage } from "./floor";

/* The keys and the verbs of the step list, as the spec names them. Any other key or verb is an error. */
const KEYS = ["route", "steps", "widths", "themes", "clients"] as const;
const VERBS = ["click", "fill", "scroll", "wait", "shot", "url"] as const;

/* The defaults of a test that does not narrow them. Each shot of a test is one width in one theme. */
const WIDTHS = [375, 768, 1280] as const;
const THEMES: readonly Theme[] = ["light", "dark"];
// The viewport height of a shot. Each shot is a full-page shot, so the height only sets the first screen.
const HEIGHT = 900;

/* The longest reveal of the site, with its stagger, in ms. The runner waits this long after the scroll pass. */
const SETTLE_MS = 1200;

export type EvidenceTest = { id: string; file: string; folder: string; route: string };

export type RoundOptions = {
  // The root of the tracker, .scratch/ at the repo root, and the feature under it.
  scratch: string;
  slug: string;
  // The test ids to run, such as ["AT-32"]. Empty or missing runs every test of the feature.
  ids?: readonly string[];
  browser: Browser;
  // Serves the site of one client and gives its url. The real run builds the client first.
  serve: (client: string) => Promise<{ url: string; close: () => Promise<void> }>;
  log: (line: string) => void;
};

/* The number of a test id, so AT-10 sorts after AT-9. */
const order = (id: string) => Number(id.slice(3));

/* Reads one step list and checks each key and each step. The error names the file and the key or the step. */
export function readSteps(file: string): Omit<EvidenceTest, "id" | "folder"> {
  let list: unknown;
  try {
    list = JSON.parse(readFileSync(file, "utf8"));
  } catch (error) {
    throw new Error(`${file}: the file is not valid JSON: ${(error as Error).message}`);
  }
  if (typeof list !== "object" || list === null || Array.isArray(list)) throw new Error(`${file}: the file must hold one object`);
  for (const key of Object.keys(list)) {
    if (!(KEYS as readonly string[]).includes(key)) {
      throw new Error(`${file}: unknown key "${key}". The known keys are ${KEYS.join(", ")}.`);
    }
  }
  const { route, steps, widths, themes, clients } = list as Record<string, unknown>;
  if (typeof route !== "string" || !route.startsWith("/")) throw new Error(`${file}: "route" must be a path that starts with "/"`);
  if (steps !== undefined) {
    if (!Array.isArray(steps)) throw new Error(`${file}: "steps" must be a list`);
    steps.forEach((step: unknown, index) => {
      const name = `step ${index + 1} ${JSON.stringify(step)}`;
      const verbs = typeof step === "object" && step !== null && !Array.isArray(step) ? Object.keys(step) : [];
      if (verbs.length !== 1) throw new Error(`${file}: ${name} must hold exactly one verb`);
      const [verb] = verbs;
      if (!(VERBS as readonly string[]).includes(verb)) {
        throw new Error(`${file}: ${name}: unknown verb "${verb}". The known verbs are ${VERBS.join(", ")}.`);
      }
      // Each verb is part of the spec, so the check knows it. The runner takes only a route-only list so far.
      throw new Error(`${file}: ${name}: the verb "${verb}" is not built yet`);
    });
  }
  for (const [key, value] of Object.entries({ widths, themes, clients })) {
    if (value !== undefined) throw new Error(`${file}: the key "${key}" is not built yet`);
  }
  return { file, route };
}

/* Finds and checks the step list of each test of the feature, or of each named test. */
export function loadTests(scratch: string, slug: string, ids: readonly string[] = []): EvidenceTest[] {
  const root = join(scratch, slug, "evidence");
  const found = existsSync(root)
    ? readdirSync(root).filter((id) => /^AT-\d+$/.test(id) && existsSync(join(root, id, "steps.json")))
    : [];
  for (const id of ids) {
    if (!found.includes(id)) throw new Error(`${join(root, id, "steps.json")}: the file does not exist`);
  }
  const chosen = ids.length > 0 ? found.filter((id) => ids.includes(id)) : found;
  if (chosen.length === 0) throw new Error(`${root}: no evidence/AT-<n>/steps.json to run`);
  return chosen
    .sort((a, b) => order(a) - order(b))
    .map((id) => ({ id, folder: join(root, id), ...readSteps(join(root, id, "steps.json")) }));
}

/*
 * Scrolls the page down one half screen at a time to the end, then back to the top. A section that reveals on scroll
 * plays only when it enters the viewport, and a full-page shot does not scroll, so with no pass it stays hidden.
 */
async function scrollPass(page: Page): Promise<void> {
  await page.evaluate(async () => {
    const pause = () => new Promise((done) => setTimeout(done, 50));
    const step = Math.max(window.innerHeight / 2, 100);
    for (let y = 0; y < document.documentElement.scrollHeight; y += step) {
      window.scrollTo(0, y);
      await pause();
    }
    window.scrollTo(0, document.documentElement.scrollHeight);
    await pause();
    window.scrollTo(0, 0);
  });
  await page.waitForTimeout(SETTLE_MS);
}

/* Takes the shots of one test: one full-page shot for each width and theme, each in a fresh page. */
async function shoot(browser: Browser, url: string, test: EvidenceTest): Promise<void> {
  for (const width of WIDTHS) {
    for (const theme of THEMES) {
      // A fresh page per shot, because openPage adds an init script that sets the theme, and a page keeps each one.
      const page = await browser.newPage({ viewport: { width, height: HEIGHT }, reducedMotion: "no-preference" });
      try {
        await openPage(page, `${url}${test.route}`, theme);
        await page.waitForLoadState("networkidle");
        await scrollPass(page);
        await page.screenshot({ path: join(test.folder, `${width}-${theme}.png`), fullPage: true });
      } finally {
        await page.close();
      }
    }
  }
}

const seconds = (start: number) => `${((Date.now() - start) / 1000).toFixed(1)} s`;

/* Runs one round: checks every step list, serves the site, takes the shots of each test, and logs each time and the total. */
export async function runRound(options: RoundOptions): Promise<void> {
  const start = Date.now();
  const tests = loadTests(options.scratch, options.slug, options.ids);
  const client = "cpc";
  const server = await options.serve(client);
  try {
    for (const test of tests) {
      const begin = Date.now();
      await shoot(options.browser, server.url, test);
      options.log(`${test.id} ${test.route}: ${WIDTHS.length * THEMES.length} shots in ${seconds(begin)}`);
    }
  } finally {
    await server.close();
  }
  options.log(`Total: ${tests.length} ${tests.length === 1 ? "test" : "tests"} of ${options.slug} in ${seconds(start)}`);
}
