/**
 * The smoke run of the verify skill: it drives each picked flow of the flow list at the smoke sizes, in the light theme.
 * A flow fails on a failed step, a failed expect, a page error, a console error, an API error, or an overlap of two texts.
 */
import { chromium, devices, webkit, type Browser, type BrowserContextOptions, type Page } from "@playwright/test";
import { mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { checkStep, LOCAL_API, runSteps, type EvidenceTest, type Step } from "./evidence";
import { openPage } from "./floor";

/*
 * One flow of the flow list. The expect steps hold its expected results; "expected" says them in words for the Judge.
 * "claude" marks a flow whose steps call Claude, and "layout" marks a flow whose layout changes with the width.
 */
export type Flow = { name: string; globs: string[]; route: string; steps: Step[]; expected: string; claude: boolean; layout: boolean };

/* The keys of a flow, as the spec names them. Any other key is an error. */
const KEYS = ["name", "globs", "route", "steps", "expected", "claude", "layout"] as const;

/* One size of a smoke run: its name in the log, its browser, and its context. */
type Size = { name: string; browser: "webkit" | "chromium"; width: number; context: BrowserContextOptions };

// The iPhone and iPad profiles with no browser type, because the size names its own browser.
const { defaultBrowserType: _phoneBrowser, ...phone } = devices["iPhone 15"];
const { defaultBrowserType: _tabletBrowser, ...tablet } = devices["iPad Pro 11"];

/*
 * The two smoke sizes of each flow: the iPhone in WebKit at 390x660, the screen that Safari leaves under its bars, and the
 * desktop at 1280x800. The acceptance rounds of the evidence runner keep their own sizes.
 */
const PHONE: Size = { name: "390x660", browser: "webkit", width: 390, context: { ...phone, viewport: { width: 390, height: 660 } } };
const DESKTOP: Size = { name: "1280x800", browser: "chromium", width: 1280, context: { viewport: { width: 1280, height: 800 } } };

/* The two iPad sizes of a layout flow, in WebKit as on an iPad: upright at 810x980, and on its side at 1080x740. */
const TABLETS: readonly Size[] = [
  { name: "810x980", browser: "webkit", width: 810, context: { ...tablet, viewport: { width: 810, height: 980 } } },
  { name: "1080x740", browser: "webkit", width: 1080, context: { ...tablet, viewport: { width: 1080, height: 740 } } },
];

/*
 * The sizes of one flow. A flow that calls Claude runs once, on the iPhone, so a smoke run costs a few cents, and the
 * Claude flag wins over the layout flag. A layout flow adds the two iPad sizes between the iPhone and the desktop.
 */
export function sizesOf(flow: Pick<Flow, "claude" | "layout">): readonly Size[] {
  if (flow.claude) return [PHONE];
  return flow.layout ? [PHONE, ...TABLETS, DESKTOP] : [PHONE, DESKTOP];
}

/* The smoke run uses the light theme only. */
const THEME = "light";

/* The time in ms that a step waits for its element. A missing element fails the flow after this time. */
const STEP_MS = 10_000;

/* The time in ms that a step of a flow that calls Claude waits for its element, because one answer of Claude takes up to a minute. */
const CLAUDE_STEP_MS = 120_000;

/* Two text boxes overlap when they share more than this many px on each axis. Less is the touch of two near lines. */
const OVERLAP_PX = 2;

export type SmokeOptions = {
  flows: readonly Flow[];
  // The slug of the client that the run built. Its test labels and file names use it. The default is cpc.
  client?: string;
  // The origin of the served export of the client.
  url: string;
  // The origin of the API of the run. A response of 4xx or 5xx from it fails the flow. The default is LOCAL_API.
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

/* The token of a route for the latest published season of the client, such as /{season}/managers/. */
export const SEASON = "{season}";

/*
 * The real route of a flow on a client: {latest-week} gives the latest published week, and {season} gives its season.
 * The tokens keep the flow list true after each weekly publish and each new season.
 */
export function routeOf(route: string, published: string): string {
  if (route === LATEST_WEEK) return latestWeek(published);
  if (!route.includes(SEASON)) return route;
  return route.replaceAll(SEASON, latestWeek(published).split("/")[1]);
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
    const { name, globs, route, steps, expected, claude, layout } = flow as Record<string, unknown>;
    if (typeof name !== "string" || name === "" || names.has(name)) throw new Error(`${at}: "name" must be a distinct name`);
    names.add(name);
    if (!Array.isArray(globs) || !globs.every((glob) => typeof glob === "string" && glob !== "")) throw new Error(`${at} "${name}": "globs" must be a list of globs`);
    if (typeof route !== "string" || !(route.startsWith("/") || route === LATEST_WEEK)) {
      throw new Error(`${at} "${name}": "route" must be a path that starts with "/", with ${SEASON} for the season, or ${LATEST_WEEK}`);
    }
    if (typeof expected !== "string" || expected === "") throw new Error(`${at} "${name}": "expected" must say the expected results`);
    if (typeof claude !== "boolean") throw new Error(`${at} "${name}": "claude" must be true or false`);
    if (typeof layout !== "boolean") throw new Error(`${at} "${name}": "layout" must be true or false`);
    return { name, globs, route, expected, claude, layout, steps: checkSteps(`${at} "${name}"`, steps) };
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
export async function findOverlap(page: Page): Promise<string | null> {
  return page.evaluate((limit) => {
    type Box = { owner: Element; top: number; bottom: number; left: number; right: number };
    const describe = (element: Element) => {
      const id = element.id ? `#${element.id}` : "";
      const text = (element.textContent ?? "").trim().replace(/\s+/g, " ").slice(0, 40);
      return `<${element.tagName.toLowerCase()}${id}> "${text}"`;
    };
    // The clip box of an element: the box of the element and of each ancestor with an overflow that is not visible, cut
    // together. The element counts too, so the 1 px box of a screen-reader text clips its own text away.
    const clipOf = (element: Element) => {
      let clip = { top: -Infinity, bottom: Infinity, left: -Infinity, right: Infinity };
      for (let at: Element | null = element; at && at !== document.documentElement; at = at.parentElement) {
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
      // A glyph box can be taller than the line height, so with tight leading two lines of one paragraph share a few px.
      // Each line keeps only its line height, cut evenly from the top and the bottom. A line height of "normal" cuts none.
      const lineHeight = parseFloat(getComputedStyle(owner).lineHeight);
      const range = document.createRange();
      range.selectNodeContents(node);
      for (const line of range.getClientRects()) {
        const trim = Number.isNaN(lineHeight) ? 0 : Math.max(0, (line.height - lineHeight) / 2);
        const box = {
          owner,
          top: Math.max(line.top + trim, clip.top),
          bottom: Math.min(line.bottom - trim, clip.bottom),
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
async function runFlow(browser: Browser, size: Size, flow: Flow, client: string, url: string, api: string, out: string): Promise<string[]> {
  const folder = join(out, flowSlug(flow.name));
  mkdirSync(folder, { recursive: true });
  const test: EvidenceTest = { id: flow.name, file: "", folder, route: flow.route, steps: flow.steps, widths: [size.width], themes: [THEME], clients: [client] };
  const context = await browser.newContext({ ...size.context, reducedMotion: "no-preference" });
  const page = await context.newPage();
  page.setDefaultTimeout(flow.claude ? CLAUDE_STEP_MS : STEP_MS);
  const causes: string[] = [];
  page.on("pageerror", (error) => causes.push(`page error: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() !== "error" || isOtherHostLoad(message.text(), message.location().url, url, api)) return;
    causes.push(`console error: ${message.text()}`);
  });
  page.on("response", (response) => {
    if (response.url().startsWith(api) && response.status() >= 400) {
      causes.push(`API error: ${response.status()} ${response.request().method()} ${response.url()}`);
    }
  });
  page.on("request", (request) => {
    if (isForeignLocal(request.url(), url, api)) causes.push(`foreign local call: ${request.method()} ${request.url()}`);
  });
  page.on("requestfailed", (request) => {
    if (request.url().startsWith(api)) causes.push(`API error: ${request.method()} ${request.url()} failed: ${request.failure()?.errorText}`);
  });
  try {
    await openPage(page, `${url}${flow.route}`, THEME);
    await page.waitForLoadState("networkidle");
    await runSteps(page, test, client, size.width, THEME);
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

/*
 * Whether a console error is the load log of a file of another host, such as a headshot of the CDN of Sleeper. The site
 * swaps a failed image of another host for its default, so the log is no fault of the page. A failed file of the site or
 * of the API still fails the flow.
 */
function isOtherHostLoad(text: string, from: string, site: string, api: string): boolean {
  return text.startsWith("Failed to load resource") && from !== "" && !from.startsWith(site) && !from.startsWith(api);
}

/* The host names of this machine. A server on one of them is a server of this run or of another session. */
const LOCAL_HOSTS = ["localhost", "127.0.0.1", "[::1]", "0.0.0.0"];

/*
 * Whether a request goes to a local server that is not the site or the API of this run. Another session can run its
 * own site or API on this machine, and a call to it tests the code of that session, so the call fails the flow.
 */
function isForeignLocal(target: string, site: string, api: string): boolean {
  const { hostname, origin, protocol } = new URL(target);
  if (!protocol.startsWith("http") || !LOCAL_HOSTS.includes(hostname)) return false;
  return origin !== new URL(site).origin && origin !== new URL(api).origin;
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
      for (const size of sizesOf(flow)) {
        const start = Date.now();
        const causes = await runFlow(browsers[size.browser], size, flow, options.client ?? "cpc", options.url, options.api ?? LOCAL_API, options.out);
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
