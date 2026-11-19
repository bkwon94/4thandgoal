/**
 * The smoke run of the verify skill: it drives each picked flow of the flow list at the smoke sizes, in the light theme.
 * A flow fails on a failed step, a failed expect, a page error, a console error, an API error, or an overlap of two texts.
 */
import { chromium, devices, webkit, type Browser, type BrowserContextOptions, type Page } from "@playwright/test";
import { mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { checkStep, LOCAL_API, runSteps, type EvidenceTest, type Step } from "./evidence";
import { openPage } from "./floor";

/* One flow of the flow list. The expect steps hold its expected results; "expected" says them in words for the Judge. */
export type Flow = { name: string; globs: string[]; route: string; steps: Step[]; expected: string };

/* The keys of a flow, as the spec names them. Any other key is an error. */
const KEYS = ["name", "globs", "route", "steps", "expected"] as const;

/* One size of a smoke run: its name in the log, its browser, and its context. */
type Size = { name: string; browser: "webkit" | "chromium"; width: number; context: BrowserContextOptions };

// The iPhone profile with no browser type, because the size names its own browser.
const { defaultBrowserType: _phoneBrowser, ...phone } = devices["iPhone 15"];

/*
 * The sizes of each flow: the iPhone in WebKit at 390x660, the screen that Safari leaves under its bars, and the desktop
 * at 1280x800. The acceptance rounds of the evidence runner keep their own sizes.
 */
const SIZES: readonly Size[] = [
  { name: "390x660", browser: "webkit", width: 390, context: { ...phone, viewport: { width: 390, height: 660 } } },
  { name: "1280x800", browser: "chromium", width: 1280, context: { viewport: { width: 1280, height: 800 } } },
];

/* The smoke run uses the light theme only. */
const THEME = "light";

/* The time in ms that a step waits for its element. A missing element fails the flow after this time. */
const STEP_MS = 10_000;

/* Two text boxes overlap when they share more than this many px on each axis. Less is the touch of two near lines. */
const OVERLAP_PX = 2;

export type SmokeOptions = {
  flows: readonly Flow[];
  // The origin of the served export of the client.
  url: string;
  // The origin of the API. A response of 4xx or 5xx from it fails the flow. The default is the local API of the evidence run.
  api?: string;
  // The smoke folder. Each flow gets a folder of its shots, and the run writes smoke.log here.
  out: string;
  log: (line: string) => void;
};

/* The folder name of a flow: its name in lower case, with a hyphen for each run of other characters. */
export const flowSlug = (name: string) => name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

/* The route of a flow that opens the latest published week of the client. */
export const LATEST_WEEK = "{latest-week}";

/*
 * The route of the latest published week of a client, such as /2026/week-10/: the highest week of the highest season.
 * A flow names it as {latest-week}, so the flow list stays true after each weekly publish.
 */
export function latestWeek(published: string): string {
  const folders = (dir: string, pattern: RegExp) =>
    readdirSync(dir, { withFileTypes: true })
      .filter((entry) => entry.isDirectory() && pattern.test(entry.name))
      .map((entry) => entry.name)
      .sort();
  const season = folders(published, /^\d{4}$/).at(-1);
  const week = season && folders(join(published, season), /^week-\d{2}$/).at(-1);
  if (!week) throw new Error(`${published}: no published week`);
  return `/${season}/${week}/`;
}

/* Reads the flow list and checks each flow and each step. The error names the file and the flow. */
export function readFlows(file: string): Flow[] {
  const list: unknown = JSON.parse(readFileSync(file, "utf8"));
  if (!Array.isArray(list)) throw new Error(`${file}: the file must hold a list of flows`);
  const names = new Set<string>();
  return list.map((flow, index) => {
    const at = `${file}: flow ${index + 1}`;
    if (typeof flow !== "object" || flow === null || Array.isArray(flow)) throw new Error(`${at} must be an object`);
    for (const key of Object.keys(flow)) {
      if (!(KEYS as readonly string[]).includes(key)) throw new Error(`${at}: unknown key "${key}". The known keys are ${KEYS.join(", ")}.`);
    }
    const { name, globs, route, steps, expected } = flow as Record<string, unknown>;
    if (typeof name !== "string" || name === "" || names.has(name)) throw new Error(`${at}: "name" must be a distinct name`);
    names.add(name);
    if (!Array.isArray(globs) || !globs.every((glob) => typeof glob === "string" && glob !== "")) throw new Error(`${at} "${name}": "globs" must be a list of globs`);
    if (typeof route !== "string" || !(route.startsWith("/") || route === LATEST_WEEK)) {
      throw new Error(`${at} "${name}": "route" must be a path that starts with "/", or ${LATEST_WEEK}`);
    }
    if (typeof expected !== "string" || expected === "") throw new Error(`${at} "${name}": "expected" must say the expected results`);
    return { name, globs, route, expected, steps: checkSteps(`${at} "${name}"`, steps) };
  });
}

/* Checks a list of steps in the shape of the evidence runner. */
function checkSteps(at: string, steps: unknown): Step[] {
  if (!Array.isArray(steps)) throw new Error(`${at}: "steps" must be a list`);
  const checked: Step[] = [];
  steps.forEach((step, index) => checked.push(checkStep(`${at}: step ${index + 1} ${JSON.stringify(step)}`, step, checked)));
  return checked;
}

/*
 * Adds the steps of a change to its flows. The file maps a flow name to the steps that go after the steps of the flow.
 * An agent adds steps for its change this way, and each flow keeps its own steps, so no picked step drops.
 */
export function addSteps(flows: readonly Flow[], file: string): Flow[] {
  const added: unknown = JSON.parse(readFileSync(file, "utf8"));
  if (typeof added !== "object" || added === null || Array.isArray(added)) throw new Error(`${file}: the file must map a flow name to its steps`);
  for (const name of Object.keys(added)) {
    if (!flows.some((flow) => flow.name === name)) throw new Error(`${file}: no picked flow is named "${name}"`);
  }
  return flows.map((flow) => {
    const more = (added as Record<string, unknown>)[flow.name];
    return more === undefined ? flow : { ...flow, steps: checkSteps(`${file} "${flow.name}"`, [...flow.steps, ...(more as unknown[])]) };
  });
}

/*
 * Finds the first two texts that overlap on the page, and names each one. A text is the box of each line of a visible
 * text node, cut to the boxes of its ancestors that clip it. Two texts of one element never count.
 */
async function findOverlap(page: Page): Promise<string | null> {
  return page.evaluate((limit) => {
    type Box = { owner: Element; top: number; bottom: number; left: number; right: number };
    const describe = (element: Element) => {
      const id = element.id ? `#${element.id}` : "";
      const text = (element.textContent ?? "").trim().replace(/\s+/g, " ").slice(0, 40);
      return `<${element.tagName.toLowerCase()}${id}> "${text}"`;
    };
    // The clip box of an element: the box of each ancestor with an overflow that is not visible, cut together.
    const clipOf = (element: Element) => {
      let clip = { top: -Infinity, bottom: Infinity, left: -Infinity, right: Infinity };
      for (let at = element.parentElement; at && at !== document.documentElement; at = at.parentElement) {
        const style = getComputedStyle(at);
        if (style.overflowX === "visible" && style.overflowY === "visible") continue;
        const box = at.getBoundingClientRect();
        clip = {
          top: Math.max(clip.top, box.top),
          bottom: Math.min(clip.bottom, box.bottom),
          left: Math.max(clip.left, box.left),
          right: Math.min(clip.right, box.right),
        };
      }
      return clip;
    };
    const boxes: Box[] = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      const owner = node.parentElement;
      if (!owner || !node.textContent?.trim() || owner.closest("script, style, noscript")) continue;
      if (!owner.checkVisibility({ opacityProperty: true, visibilityProperty: true })) continue;
      const clip = clipOf(owner);
      const range = document.createRange();
      range.selectNodeContents(node);
      for (const line of range.getClientRects()) {
        const box = {
          owner,
          top: Math.max(line.top, clip.top),
          bottom: Math.min(line.bottom, clip.bottom),
          left: Math.max(line.left, clip.left),
          right: Math.min(line.right, clip.right),
        };
        if (box.bottom - box.top > limit && box.right - box.left > limit) boxes.push(box);
      }
    }
    boxes.sort((a, b) => a.top - b.top);
    for (const [index, a] of boxes.entries()) {
      for (const b of boxes.slice(index + 1)) {
        if (b.top >= a.bottom - limit) break;
        if (a.owner === b.owner) continue;
        const across = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        const down = Math.min(a.bottom, b.bottom) - b.top;
        if (across > limit && down > limit) return `${describe(a.owner)} and ${describe(b.owner)}`;
      }
    }
    return null;
  }, OVERLAP_PX);
}

/*
 * Runs one flow at one size in a fresh context. It gives the causes of a failure, or an empty list for a pass.
 * The page listens for errors from the first load, so an error before the first step still fails the flow.
 */
async function runFlow(browser: Browser, size: Size, flow: Flow, url: string, api: string, out: string): Promise<string[]> {
  const folder = join(out, flowSlug(flow.name));
  mkdirSync(folder, { recursive: true });
  const test: EvidenceTest = { id: flow.name, file: "", folder, route: flow.route, steps: flow.steps, widths: [size.width], themes: [THEME], clients: ["cpc"] };
  const context = await browser.newContext({ ...size.context, reducedMotion: "no-preference" });
  const page = await context.newPage();
  page.setDefaultTimeout(STEP_MS);
  const causes: string[] = [];
  page.on("pageerror", (error) => causes.push(`page error: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error") causes.push(`console error: ${message.text()}`);
  });
  page.on("response", (response) => {
    if (response.url().startsWith(api) && response.status() >= 400) {
      causes.push(`API error: ${response.status()} ${response.request().method()} ${response.url()}`);
    }
  });
  page.on("requestfailed", (request) => {
    if (request.url().startsWith(api)) causes.push(`API error: ${request.method()} ${request.url()} failed: ${request.failure()?.errorText}`);
  });
  try {
    await openPage(page, `${url}${flow.route}`, THEME);
    await page.waitForLoadState("networkidle");
    await runSteps(page, test, "cpc", size.width, THEME);
    const overlap = await findOverlap(page);
    if (overlap) causes.push(`overlap: ${overlap}`);
  } catch (error) {
    causes.push((error as Error).message.split("\n")[0]);
  }
  // A shot of the page as it failed, so the Judge and the agent see the cause.
  if (causes.length > 0) await page.screenshot({ path: join(folder, `fail-${size.width}-${THEME}.png`), fullPage: true }).catch(() => undefined);
  await context.close();
  return causes;
}

const seconds = (start: number) => `${((Date.now() - start) / 1000).toFixed(1)} s`;

/*
 * Runs each flow at each size, and writes smoke.log into the smoke folder. Each flow runs at each size even after a
 * failure, so the log names each cause of one run. The result lists each failure as one line of the log.
 */
export async function runSmoke(options: SmokeOptions): Promise<{ failures: string[] }> {
  mkdirSync(options.out, { recursive: true });
  const lines: string[] = [];
  const log = (line: string) => {
    lines.push(line);
    options.log(line);
  };
  const failures: string[] = [];
  const browsers = { webkit: await webkit.launch(), chromium: await chromium.launch() };
  let passed = 0;
  try {
    for (const flow of options.flows) {
      let green = true;
      for (const size of SIZES) {
        const start = Date.now();
        const causes = await runFlow(browsers[size.browser], size, flow, options.url, options.api ?? LOCAL_API, options.out);
        const where = `${flow.name} ${size.name} ${size.browser}`;
        if (causes.length === 0) log(`PASS ${where} in ${seconds(start)}`);
        for (const cause of causes) {
          const line = `FAIL ${where}: ${cause}`;
          failures.push(line);
          log(line);
        }
        green &&= causes.length === 0;
      }
      if (green) passed += 1;
    }
  } finally {
    await browsers.webkit.close();
    await browsers.chromium.close();
  }
  const count = options.flows.length;
  log(`Smoke run: ${count} ${count === 1 ? "flow" : "flows"}, ${passed} passed, ${count - passed} failed`);
  writeFileSync(join(options.out, "smoke.log"), `${lines.join("\n")}\n`);
  return { failures };
}
