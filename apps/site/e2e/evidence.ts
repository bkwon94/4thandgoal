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

/* The client of a test with no "clients" key. */
const CLIENT = "cpc";

// prefix is true when the test names more than one client, so the shots of each client get distinct file names.
export type EvidenceTest = { id: string; file: string; folder: string; route: string; clients: string[]; prefix: boolean };

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
  for (const [key, value] of Object.entries({ widths, themes })) {
    if (value !== undefined) throw new Error(`${file}: the key "${key}" is not built yet`);
  }
  if (clients !== undefined) {
    const valid = Array.isArray(clients) && clients.length > 0 && clients.every((client) => typeof client === "string" && client !== "");
    if (!valid || new Set(clients).size !== clients.length) {
      throw new Error(`${file}: "clients" must be a list of distinct client slugs, such as ["cpc", "norcal"]`);
    }
  }
  const names = (clients as string[] | undefined) ?? [CLIENT];
  return { file, route, clients: names, prefix: names.length > 1 };
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

/*
 * The path of one shot file. The client prefix lives only here, so each shot name gets it the same way. A test with
 * more than one client needs it, or the shots of the second client overwrite the shots of the first.
 */
function shotFile(test: EvidenceTest, client: string, name: string): string {
  return join(test.folder, `${test.prefix ? `${client}-` : ""}${name}.png`);
}

/* Takes the shots of one test for one client: one full-page shot for each width and theme, each in a fresh page. */
async function shoot(browser: Browser, url: string, test: EvidenceTest, client: string): Promise<void> {
  for (const width of WIDTHS) {
    for (const theme of THEMES) {
      // A fresh page per shot, because openPage adds an init script that sets the theme, and a page keeps each one.
      const page = await browser.newPage({ viewport: { width, height: HEIGHT }, reducedMotion: "no-preference" });
      try {
        await openPage(page, `${url}${test.route}`, theme);
        await page.waitForLoadState("networkidle");
        await scrollPass(page);
        await page.screenshot({ path: shotFile(test, client, `${width}-${theme}`), fullPage: true });
      } finally {
        await page.close();
      }
    }
  }
}

const seconds = (start: number) => `${((Date.now() - start) / 1000).toFixed(1)} s`;

/*
 * Runs one round: checks every step list, then for each client serves its site and takes the shots of each test of
 * that client. Each client builds into the same out/ folder, so the round serves one client at a time, one time each.
 */
export async function runRound(options: RoundOptions): Promise<void> {
  const start = Date.now();
  const tests = loadTests(options.scratch, options.slug, options.ids);
  // The clients in the order the tests first name them, so the default cpc of the first test builds first.
  const clients = [...new Set(tests.flatMap((test) => test.clients))];
  for (const client of clients) {
    const server = await options.serve(client);
    try {
      for (const test of tests.filter((each) => each.clients.includes(client))) {
        const begin = Date.now();
        await shoot(options.browser, server.url, test, client);
        options.log(`${test.id} ${test.route} ${client}: ${WIDTHS.length * THEMES.length} shots in ${seconds(begin)}`);
      }
    } finally {
      await server.close();
    }
  }
  options.log(`Total: ${tests.length} ${tests.length === 1 ? "test" : "tests"} of ${options.slug} in ${seconds(start)}`);
}
