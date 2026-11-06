/**
 * The evidence runner: it reads each evidence/AT-<n>/steps.json of a feature and takes the shots of each test beside it.
 * It checks every step list before the first shot, so a bad list stops the run with no shot written.
 */
import type { Theme } from "@cpc/design/lib/theme";
import type { Browser, Page } from "@playwright/test";
import { existsSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
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

/*
 * One step of a step list. Each step is an object with one verb as its key:
 * {"click": "<selector>"}, {"fill": {"selector": "<selector>", "value": "<text>"}}, {"scroll": "<selector>" or "end"},
 * {"wait": "<selector>", "url", or a time in ms}, {"shot": "<name>"}, and {"url": true}.
 */
export type Step =
  | { click: string }
  | { fill: { selector: string; value: string } }
  | { scroll: string }
  | { wait: string | number }
  | { shot: string }
  | { url: true };

export type EvidenceTest = {
  id: string;
  file: string;
  folder: string;
  route: string;
  steps: Step[];
  widths: number[];
  themes: Theme[];
};

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
  if (steps !== undefined && !Array.isArray(steps)) throw new Error(`${file}: "steps" must be a list`);
  const checked: Step[] = [];
  ((steps ?? []) as unknown[]).forEach((step, index) => {
    checked.push(checkStep(`${file}: step ${index + 1} ${JSON.stringify(step)}`, step, checked));
  });
  if (clients !== undefined) throw new Error(`${file}: the key "clients" is not built yet`);
  return {
    file,
    route,
    steps: checked,
    widths: widths === undefined ? [...WIDTHS] : checkWidths(file, widths),
    themes: themes === undefined ? [...THEMES] : checkThemes(file, themes),
  };
}

/* Checks one step against the steps before it. The error starts with name, which holds the file and the step. */
function checkStep(name: string, step: unknown, before: readonly Step[]): Step {
  const verbs = typeof step === "object" && step !== null && !Array.isArray(step) ? Object.keys(step) : [];
  if (verbs.length !== 1) throw new Error(`${name} must hold exactly one verb`);
  const [verb] = verbs;
  if (!(VERBS as readonly string[]).includes(verb)) {
    throw new Error(`${name}: unknown verb "${verb}". The known verbs are ${VERBS.join(", ")}.`);
  }
  const value = (step as Record<string, unknown>)[verb];
  const text = typeof value === "string" && value.length > 0;
  const fail = (rule: string): never => {
    throw new Error(`${name}: "${verb}" ${rule}`);
  };
  switch (verb) {
    case "click":
      if (!text) fail("takes a selector");
      break;
    case "fill": {
      const fields = typeof value === "object" && value !== null ? (value as Record<string, unknown>) : {};
      const keys = Object.keys(fields).sort().join(",");
      if (keys !== "selector,value" || typeof fields.selector !== "string" || typeof fields.value !== "string") {
        fail('takes {"selector": "<selector>", "value": "<text>"}');
      }
      break;
    }
    case "scroll":
      if (!text) fail('takes a selector or "end"');
      break;
    case "wait":
      if (!text && !(typeof value === "number" && Number.isFinite(value) && value >= 0)) {
        fail('takes a selector, "url", or a time in ms');
      }
      // "url" waits for the URL to change from the URL before the last click, so it needs a click before it.
      if (value === "url" && !before.some((earlier) => "click" in earlier)) fail('"url" needs a click before it');
      break;
    case "shot":
      // The name goes into a file name, so it holds only lower-case letters, digits, and hyphens.
      if (typeof value !== "string" || !/^[a-z0-9][a-z0-9-]*$/.test(value)) fail("takes a name of a-z, 0-9, and -");
      if (before.some((earlier) => "shot" in earlier && earlier.shot === value)) fail(`name "${value}" is used twice`);
      break;
    case "url":
      if (value !== true) fail("takes the value true");
      break;
  }
  return step as Step;
}

/* Checks the widths of a step list: a list of whole widths in px, each one time. */
function checkWidths(file: string, value: unknown): number[] {
  const ok = Array.isArray(value) && value.length > 0 && value.every((width) => Number.isInteger(width) && width > 0);
  if (!ok || new Set(value).size !== value.length) throw new Error(`${file}: "widths" must be a list of widths in px, such as [768, 1280]`);
  return value as number[];
}

/* Checks the themes of a step list: a list of light and dark, each one time. */
function checkThemes(file: string, value: unknown): Theme[] {
  const ok = Array.isArray(value) && value.length > 0 && value.every((theme) => (THEMES as readonly unknown[]).includes(theme));
  if (!ok || new Set(value).size !== value.length) throw new Error(`${file}: "themes" must be a list of ${THEMES.join(", ")}`);
  return value as Theme[];
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

/* Takes one full-page shot, after the scroll pass, so each section that reveals on scroll shows. */
async function takeShot(page: Page, path: string): Promise<void> {
  await scrollPass(page);
  await page.screenshot({ path, fullPage: true });
}

/* Runs the steps of one test in one page. A shot or a url step writes its file for this width and theme. */
async function runSteps(page: Page, test: EvidenceTest, width: number, theme: Theme): Promise<void> {
  // The URL before the last click, for "wait": "url".
  let clickedFrom = page.url();
  for (const step of test.steps) {
    if ("click" in step) {
      clickedFrom = page.url();
      await page.locator(step.click).first().click();
    } else if ("fill" in step) {
      await page.locator(step.fill.selector).first().fill(step.fill.value);
    } else if ("scroll" in step) {
      if (step.scroll === "end") await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
      else await page.locator(step.scroll).first().scrollIntoViewIfNeeded();
      // The scroll events and the IntersectionObserver callbacks of the page run in the next frames. Two frames let them
      // run, so the next step sees the page after its scroll.
      await page.evaluate(() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done))));
    } else if ("wait" in step) {
      // "url" waits until the URL changes from the URL before the last click, so a tap that opens a page has opened it.
      if (step.wait === "url") await page.waitForURL((now) => now.href !== clickedFrom);
      else if (typeof step.wait === "number") await page.waitForTimeout(step.wait);
      else await page.locator(step.wait).first().waitFor({ state: "visible" });
    } else if ("shot" in step) {
      await takeShot(page, join(test.folder, `${step.shot}-${width}-${theme}.png`));
    } else {
      // The page itself gives the URL, because page.url() can lag a change that history.replaceState makes.
      const href = await page.evaluate(() => location.href);
      writeFileSync(join(test.folder, `url-${width}-${theme}.txt`), `${href}\n`);
    }
  }
  // With no shot step, the test gets one shot after its last step, with the plain name.
  if (!test.steps.some((step) => "shot" in step)) await takeShot(page, join(test.folder, `${width}-${theme}.png`));
}

/* The number of shots that one test takes. */
const shotCount = (test: EvidenceTest) =>
  test.widths.length * test.themes.length * Math.max(1, test.steps.filter((step) => "shot" in step).length);

/* Takes the shots of one test: its steps run once for each width and theme, each in a fresh page. */
async function shoot(browser: Browser, url: string, test: EvidenceTest): Promise<void> {
  for (const width of test.widths) {
    for (const theme of test.themes) {
      // A fresh page per width and theme, because openPage adds an init script that sets the theme, and a page keeps each one.
      const page = await browser.newPage({ viewport: { width, height: HEIGHT }, reducedMotion: "no-preference" });
      try {
        await openPage(page, `${url}${test.route}`, theme);
        await page.waitForLoadState("networkidle");
        await runSteps(page, test, width, theme);
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
      options.log(`${test.id} ${test.route}: ${shotCount(test)} ${shotCount(test) === 1 ? "shot" : "shots"} in ${seconds(begin)}`);
    }
  } finally {
    await server.close();
  }
  options.log(`Total: ${tests.length} ${tests.length === 1 ? "test" : "tests"} of ${options.slug} in ${seconds(start)}`);
}
