/**
 * The site evidence of easter-eggs: each phase sets the state of the local API with its real routes, then takes the shots.
 * The runner of apps/site could not use its fixed port 4173, so this spec serves each export on 4174 and 4175 itself.
 */
import { expect, test, type Browser, type Page } from "../../../../apps/site/node_modules/@playwright/test/index.js";
import { execFileSync } from "node:child_process";
import { mkdirSync, writeFileSync, appendFileSync } from "node:fs";
import { join } from "node:path";
import { scanContrast, scanTargets, scanText, scanScroll } from "../../../../apps/site/e2e/floor";
// The same axe that floor.ts uses. floor.ts gives only its failure lines, so the spec runs axe again to print each count.
import AxeBuilder from "../../../../apps/site/node_modules/@axe-core/playwright";
import { createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, normalize } from "node:path";

const TYPES: Record<string, string> = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css",
  ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp",
  ".woff2": "font/woff2", ".ico": "image/x-icon", ".txt": "text/plain; charset=utf-8" };

/* Serve one export on 127.0.0.1. A missing path gets 404.html with the status 404, as the Worker gives it. */
function serveDir(dir: string, port: number): Promise<{ close: () => Promise<void> }> {
  const server = createServer((request, response) => {
    const path = new URL(request.url ?? "/", "http://localhost").pathname;
    let file: string | null = normalize(join(dir, decodeURIComponent(path)));
    if (!(existsSync(file) && statSync(file).isFile())) file = existsSync(join(file, "index.html")) ? join(file, "index.html") : null;
    const body = file ?? join(dir, "404.html");
    response.statusCode = file ? 200 : 404;
    response.setHeader("content-type", TYPES[extname(body)] ?? "application/octet-stream");
    createReadStream(body).pipe(response);
  });
  return new Promise((done) => server.listen(port, "127.0.0.1", () => done({ close: () => new Promise((c) => server.close(() => c())) })));
}

const SCRATCH = process.env.EGGS_SCRATCH!;
// EGGS_EV moves the output to a folder outside the repo, so a run again changes no file of a test outside its list.
const EV = process.env.EGGS_EV ?? join(__dirname, "..");
const TOOLS = __dirname;
const CPC = "http://127.0.0.1:4174";
const NORCAL = "http://127.0.0.1:4175";
const API = "http://127.0.0.1:8080/clients/cpc/eggs";
const KEY = { "X-Commissioner-Key": "localkey", "Content-Type": "application/json" };
const PASS = { "X-League-Passphrase": "localtest", "Content-Type": "application/json" };
const WIDTHS = [375, 768, 1280];
const THEMES = ["light", "dark"] as const;
type Theme = (typeof THEMES)[number];

// The test eggs of ACCEPTANCE.md and the fillers of each drop. The API gives the letters A, C, D, E, G, L in this order.
const F1 = { page: "/2026/week-08/", target: "number-top-score", action: "tap2", conditions: {} };
const T1 = { page: "/midseason/2026/", target: "luck-3", action: "tap2", conditions: { theme: "light" } };
const T2 = { page: "/2026/week-08/", target: "number-median", action: "tap2", conditions: { clock: "23:00-00:00" } };
const T3 = { page: "/midseason/2026/", target: "sim-trophy", action: "tap2", conditions: { sim_champion: 12 } };
const F5 = { page: "/midseason/2026/", target: "heading-luck", action: "tap2", conditions: {} };
const F6 = { page: "/2026/week-08/", target: "heading-awards", action: "hold", conditions: {} };
const LIL_FRIDGE = 3;
const TEEHEE = 12;

let servers: { close: () => Promise<void> }[] = [];

test.beforeAll(async () => {
  servers = [await serveDir(join(SCRATCH, "out-cpc"), 4174), await serveDir(join(SCRATCH, "out-norcal"), 4175)];
});
test.afterAll(async () => {
  for (const server of servers) await server.close();
});

/* Start the API on the store, fresh or kept. A restart also clears the limits of the address, which only live in memory. */
function api(store: string, fresh = false) {
  const dir = join(SCRATCH, `eggs-${store}`);
  execFileSync("bash", [join(TOOLS, "stop-api.sh")], { env: { ...process.env }, stdio: "pipe" });
  if (fresh) execFileSync("rm", ["-rf", dir]);
  execFileSync("bash", [join(TOOLS, "start-api.sh"), dir, join(SCRATCH, `api-site-${store}.log`)], { env: { ...process.env }, stdio: "pipe" });
}
function storeFile(store: string) {
  return join(SCRATCH, `eggs-${store}`, "cpc.sqlite");
}

/* A fetch that tries again on a reset connection. The first call after a start of the API can meet a reset. */
async function retry(url: string, init?: RequestInit): Promise<Response> {
  for (let attempt = 1; ; attempt += 1) {
    try {
      return await fetch(url, init);
    } catch (error) {
      if (attempt >= 5) throw error;
      await new Promise((done) => setTimeout(done, 1000));
    }
  }
}
async function post(path: string, body: unknown, headers: Record<string, string> = { "Content-Type": "application/json" }) {
  const response = await retry(`${API}${path}`, { method: "POST", headers, body: JSON.stringify(body) });
  return { status: response.status, body: await response.json().catch(() => null) };
}
const drop = (week: number, eggs: unknown[]) => post("/drop", { week, eggs }, KEY);
/* A check of the egg, then a claim of its token for the roster into the word, or a block for a null word. */
async function claim(egg: { page: string; target: string; action: string; conditions: Record<string, unknown> }, roster: number, word: string | null) {
  const check = await post("/check", egg);
  // A run of a phase again finds its own claims of the first run, so a claimed egg keeps its claim.
  if (check.body?.claimed) return { kept: "the egg already holds a claim from an earlier run of this phase", letter: check.body.letter };
  const answer = await post("/claim", { token: check.body.token, roster_id: roster, word }, PASS);
  expect(answer.status, JSON.stringify(answer.body)).toBe(200);
  return answer.body;
}
const undo = (eggId: number) => post("/undo", { egg_id: eggId }, KEY);
async function board() {
  return (await retry(`${API}/board`)).json();
}

function folder(at: string) {
  const path = join(EV, at);
  mkdirSync(path, { recursive: true });
  return path;
}
// Each phase writes its lines to <AT>/site-<phase>.txt. The first line of a run clears the file, so a run again starts clean.
let PHASE = "";
const written = new Set<string>();
function log(at: string, line: string) {
  const file = join(folder(at), `site-${PHASE}.txt`);
  if (!written.has(file)) writeFileSync(file, "");
  written.add(file);
  appendFileSync(file, `${line}\n`);
}

/* A page at the width, in the theme, with motion on unless `reduced`, and the passphrase in the browser when `pass`. */
async function open(browser: Browser, width: number, theme: Theme, options: { pass?: boolean; reduced?: boolean; clock?: string } = {}) {
  const context = await browser.newContext({ viewport: { width, height: 900 }, reducedMotion: options.reduced ? "reduce" : "no-preference" });
  await context.addInitScript(({ theme, pass }) => {
    try {
      if (!sessionStorage.getItem("ee-init")) {
        localStorage.setItem("cpc.theme", theme);
        if (pass) localStorage.setItem("cpc.passphrase", "localtest");
        sessionStorage.setItem("ee-init", "1");
      }
    } catch {}
  }, { theme, pass: options.pass ?? false });
  const page = await context.newPage();
  if (options.clock) await page.clock.setFixedTime(new Date(options.clock));
  const checks: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/eggs/check")) checks.push(request.postData() ?? "");
  });
  return { page, checks, close: () => context.close() };
}

/* Switch the open page to the theme, as the theme button does: the class on the root and the stored choice. */
async function setTheme(page: Page, theme: Theme) {
  await page.evaluate((theme) => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem("cpc.theme", theme);
  }, theme);
  await page.waitForTimeout(300);
}

async function settle(page: Page) {
  await page.waitForLoadState("networkidle", { timeout: 4000 }).catch(() => {});
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(1200);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(600);
}
const shot = (page: Page, at: string, name: string, width: number, theme: Theme, fullPage = false) =>
  page.screenshot({ path: join(folder(at), `${name ? `${name}-` : ""}${width}-${theme}.png`), fullPage });

/* Find T1 in the light theme: a double-tap on the Luck cell of Lil Fridge. */
async function findT1(page: Page) {
  await page.goto(`${CPC}/midseason/2026/`);
  // T1 holds only in the light theme. A shot in the dark theme switches the theme after the find.
  await setTheme(page, "light");
  // The hunt mounts its listener only after the board answer names a drop, so the taps wait for the egg button.
  await page.getByRole("link", { name: /^Egg board/ }).first().waitFor({ timeout: 30000 });
  const cell = page.locator('[data-stable-id="luck-3"]');
  await cell.scrollIntoViewIfNeeded();
  await cell.click({ clickCount: 2 });
}
async function crack(page: Page) {
  await page.getByRole("button", { name: "Crack the egg" }).click();
  await expect(page.getByTestId("egg-letter")).toBeVisible();
}

/* The full text of the banner line and whether the line is cut: its scrollWidth is wider than its clientWidth. */
async function bannerLine(page: Page) {
  return page.locator("[data-banner-line]").evaluate((line) => `line "${(line.textContent ?? "").replace(/\s+/g, " ").trim()}", scrollWidth ${line.scrollWidth}, clientWidth ${line.clientWidth}, cut ${line.scrollWidth > line.clientWidth}, height ${Math.round(line.getBoundingClientRect().height)} px`);
}

test.describe.configure({ mode: "serial" });
test.setTimeout(0);

test("phase A0: an empty store, NorCal", async ({ browser }) => {
  PHASE = "A0";
  test.setTimeout(0);
  api("A", true);
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { page, close } = await open(browser, width, theme);
    await page.goto(`${CPC}/eggs/`);
    await expect(page.getByText("CORNERSTONE").first()).toBeVisible();
    await settle(page);
    await shot(page, "AT-47", "", width, theme, true);
    const how = page.getByRole("region", { name: /How the hunt works/i });
    if (await how.count()) {
      await how.scrollIntoViewIfNeeded();
      await how.screenshot({ path: join(folder("AT-46"), `${width}-${theme}.png`) });
    } else {
      await shot(page, "AT-46", "", width, theme, true);
    }
    if (width === 1280 && theme === "light") {
      writeFileSync(join(folder("AT-47"), "board.json"), JSON.stringify(await board(), null, 2));
      log("AT-47", `/eggs/ text of the hero: ${(await page.locator("main").innerText()).slice(0, 600).replace(/\n+/g, " | ")}`);
      log("AT-46", `The text of the last card: ${how ? (await how.innerText()).replace(/\n+/g, " | ") : "no region named How the hunt works"}`);
    }
    await close();
  }
  // NorCal: the home page and /eggs/, with no egg button and no listener.
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { page, checks, close } = await open(browser, width, theme);
    await page.goto(`${NORCAL}/`);
    await settle(page);
    await shot(page, "AT-24", "home", width, theme, true);
    const buttons = await page.locator('a[href$="/eggs/"]').count();
    await page.locator('[data-stable-id="page-end"]').first().click({ clickCount: 2, force: true }).catch(() => {});
    await page.locator("main").click({ clickCount: 2, position: { x: 20, y: 20 } }).catch(() => {});
    await page.waitForTimeout(800);
    const response = await page.goto(`${NORCAL}/eggs/`);
    await settle(page);
    await shot(page, "AT-24", "eggs", width, theme, true);
    const notFound = await page.locator("[data-not-found]").count();
    log("AT-24", `norcal ${width}-${theme}: links to /eggs/ on home ${buttons}, egg checks sent after two double-taps ${checks.length}, /eggs/ status ${response?.status()}, 404 mark ${notFound}`);
    await close();
  }
  const { page, close } = await open(browser, 1280, "light");
  await page.goto(`${NORCAL}/`);
  const html = await page.content();
  log("AT-24", `norcal home: the text "egg" in the HTML of the page: ${(html.match(/\begg/gi) ?? []).length}; the script names of the eggs package: ${(html.match(/egg-hunt|EggHunt|egg-button|egg-banner/g) ?? []).length}`);
  await close();
});

test("phase A1: six eggs, none claimed", async ({ browser }) => {
  PHASE = "A1";
  api("A");
  const dropped = await drop(9, [F1, T1, T2, T3, F5, F6]);
  writeFileSync(join(folder("AT-40"), "drop.json"), JSON.stringify(dropped.body, null, 2));

  // AT-25: one tap on a game card.
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { page, checks, close } = await open(browser, width, theme);
    await page.goto(`${CPC}/2026/week-08/`);
    const card = page.locator('button[aria-controls="recap-3"]');
    await card.scrollIntoViewIfNeeded();
    await card.click();
    await page.waitForTimeout(1200);
    await page.locator("#recap-3").scrollIntoViewIfNeeded().catch(() => {});
    await shot(page, "AT-25", "", width, theme);
    log("AT-25", `${width}-${theme}: aria-expanded of the game 3 card after one tap ${await card.getAttribute("aria-expanded")}; egg checks sent ${checks.length} ${JSON.stringify(checks)}`);
    await close();
  }

  // AT-26 to AT-31: the listener. One browser at 1280 px in the light theme.
  {
    const { page, checks, close } = await open(browser, 1280, "light");
    await page.goto(`${CPC}/midseason/2026/`);
    await page.getByRole("link", { name: /^Egg board/ }).first().waitFor({ timeout: 30000 });
    const cell = page.locator('[data-stable-id="luck-3"]');
    await cell.scrollIntoViewIfNeeded();
    await page.evaluate(() => {
      const w = window as unknown as { eeTimes: number[] };
      w.eeTimes = [];
      window.addEventListener("pointerup", () => w.eeTimes.push(Math.round(performance.now())), true);
    });
    for (let i = 0; i < 2; i += 1) {
      await tapAt(page, '[data-stable-id="luck-3"]');
      if (i < 1) await page.waitForTimeout(150);
    }
    await page.waitForTimeout(1000);
    const times = await page.evaluate(() => (window as unknown as { eeTimes: number[] }).eeTimes);
    log("AT-26", `Two mouse taps on [data-stable-id="luck-3"] of /midseason/2026/ in the light theme. The pointerup times of the page, in ms from the first: ${times.map((t) => t - times[0]).join(", ")}.`);
    log("AT-26", `Checks sent: ${checks.length}`);
    checks.forEach((body) => log("AT-26", `body: ${body}`));
    await page.keyboard.press("Escape");
    await close();
  }
  {
    const { page, checks, close } = await open(browser, 1280, "light");
    await page.goto(`${CPC}/midseason/2026/`);
    await page.getByRole("link", { name: /^Egg board/ }).first().waitFor({ timeout: 30000 });
    const cell = page.locator('[data-stable-id="luck-3"]');
    await cell.scrollIntoViewIfNeeded();
    const box = (await cell.boundingBox())!;
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
    // A hold of 3.5 s, then a hold of 1.5 s. The log shows the checks sent after each hold.
    for (const ms of [3500, 1500]) {
      const before = checks.length;
      const down = Date.now();
      await page.mouse.down();
      await page.waitForTimeout(ms);
      await page.mouse.up();
      const held = Date.now() - down;
      await page.waitForTimeout(1000);
      log("AT-27", `A press on [data-stable-id="luck-3"] of /midseason/2026/, held ${held} ms from the pointer down to the pointer up. Checks sent by this press: ${checks.length - before}`);
      checks.slice(before).forEach((body) => log("AT-27", `body: ${body}`));
      await page.keyboard.press("Escape");
      await page.waitForTimeout(800);
    }
    log("AT-27", `Checks sent in all: ${checks.length}`);
    await close();
  }
  {
    const { page, checks, close } = await open(browser, 1280, "light");
    await page.goto(`${CPC}/2026/week-08/`);
    const a = page.locator('[data-stable-id="number-top-score"]');
    const b = page.locator('[data-stable-id="number-median"]');
    const c = page.locator('[data-stable-id="number-closest"]');
    await a.scrollIntoViewIfNeeded();
    const start = Date.now();
    await a.click();
    await page.waitForTimeout(600);
    await b.click();
    await page.waitForTimeout(600);
    await c.click();
    await page.waitForTimeout(120);
    await c.click();
    const end = Date.now();
    await page.waitForTimeout(1000);
    log("AT-28", `Tap A [data-stable-id="number-top-score"], wait 600 ms, tap B [data-stable-id="number-median"], wait 600 ms, then two taps 120 ms apart on C [data-stable-id="number-closest"] of /2026/week-08/. First tap to last tap: ${end - start} ms.`);
    log("AT-28", `Checks sent: ${checks.length}`);
    checks.forEach((body) => log("AT-28", `body: ${body}`));
    await close();
  }
  {
    const { page, checks, close } = await open(browser, 1280, "light");
    await page.goto(`${CPC}/midseason/2026/`);
    const blurb = page.locator('[data-stable-id="blurb-1jo5mqe"]');
    await blurb.scrollIntoViewIfNeeded();
    const word = await blurb.evaluate((element) => {
      const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
      const node = walker.nextNode()!;
      const text = node.textContent ?? "";
      const end = text.search(/\s/);
      const range = document.createRange();
      range.setStart(node, 0);
      range.setEnd(node, end);
      const selection = document.getSelection()!;
      selection.removeAllRanges();
      selection.addRange(range);
      return selection.toString();
    });
    await page.waitForTimeout(1500);
    log("AT-29", `The selection of the first whole word of [data-stable-id="blurb-1jo5mqe"] of /midseason/2026/, made with a DOM range: "${word}".`);
    log("AT-29", `Checks sent: ${checks.length}`);
    checks.forEach((body) => log("AT-29", `body: ${body}`));
    await close();
  }
  {
    const { page, checks, close } = await open(browser, 1280, "light");
    await page.goto(`${CPC}/midseason/2026/`);
    await page.getByRole("link", { name: /^Egg board/ }).first().waitFor({ timeout: 30000 });
    await page.getByRole("button", { name: "Sim the season" }).click();
    const row = page.locator('[data-stable-id="sim-row-3"]');
    await row.first().waitFor();
    await row.first().scrollIntoViewIfNeeded();
    await page.waitForTimeout(1500);
    const frame = () => page.evaluate(() => {
      const live = document.querySelector('[aria-label="The replay"] [aria-live]')?.textContent ?? "";
      const element = document.querySelector('[data-stable-id="sim-row-3"]') as HTMLElement & { eeNode?: number };
      const node = element?.eeNode ?? ((element.eeNode = Math.random()), element.eeNode);
      const rows = [...document.querySelectorAll('[data-stable-id^="sim-row-"]')].map((each) => each.getAttribute("data-stable-id"));
      return { live, node, place: rows.indexOf("sim-row-3") + 1, text: element.textContent?.slice(0, 40) };
    });
    const frames = [await frame()];
    for (let i = 0; i < 2; i += 1) {
      await row.first().click({ force: true });
      frames.push(await frame());
      await page.waitForTimeout(250);
      frames.push(await frame());
    }
    await page.waitForTimeout(1000);
    log("AT-30", "The replay runs. Two taps on [data-stable-id=\"sim-row-3\"], 250 ms apart, and the frame read before and after each tap.");
    log("AT-30", "Each line: the live line of the replay, a mark of the DOM node (a new number is a new node), the place of the row, and its text.");
    frames.forEach((each, index) => log("AT-30", `read ${index}: ${JSON.stringify(each)}`));
    log("AT-30", `Checks sent: ${checks.length}`);
    checks.forEach((body) => log("AT-30", `body: ${body}`));
    await close();
  }
  {
    const { page, close } = await open(browser, 1280, "light");
    await page.goto(`${CPC}/midseason/2026/`);
    const styles = await page.evaluate(() => {
      const callout = (element: Element | null) => element ? (getComputedStyle(element) as unknown as Record<string, string>)["webkitTouchCallout"] ?? getComputedStyle(element).getPropertyValue("-webkit-touch-callout") : "none found";
      const link = document.querySelector("main a[href]");
      const image = document.querySelector("main img");
      return {
        luck: { selector: '[data-stable-id="luck-3"]', callout: callout(document.querySelector('[data-stable-id="luck-3"]')) },
        link: { selector: `main a[href] (${link?.getAttribute("href")})`, callout: callout(link) },
        image: { selector: `main img (${image?.getAttribute("src")?.slice(0, 60)})`, callout: callout(image) },
      };
    });
    log("AT-31", "The computed -webkit-touch-callout of each element on /midseason/2026/ in Chromium:");
    for (const [name, each] of Object.entries(styles)) log("AT-31", `${name}: ${each.selector} -> ${each.callout}`);
    await close();
  }

  // AT-40: the top band of three pages with the badge, then the tap on the egg button.
  for (const [name, route] of [["home", "/"], ["week-08", "/2026/week-08/"], ["midseason", "/midseason/2026/"]] as const) {
    api("A");
    for (const width of WIDTHS) for (const theme of THEMES) {
      const { page, close } = await open(browser, width, theme);
      await page.goto(`${CPC}${route}`);
      const button = page.locator('header a[href$="/eggs/"]').first();
      await expect(button).toBeVisible();
      // The first board read after a start of the API reads the live rosters, so the badge waits for it.
      await expect(button).toHaveAttribute("aria-label", /6 eggs left/, { timeout: 30000 });
      await page.waitForTimeout(1200);
      await page.screenshot({ path: join(folder("AT-40"), `${name}-${width}-${theme}.png`), clip: { x: 0, y: 0, width, height: 200 } });
      log("AT-40", `${name} ${width}-${theme}: egg button "${(await button.innerText()).replace(/\n/g, " ")}", aria-label "${await button.getAttribute("aria-label")}"`);
      if (theme === "light") {
        await button.click();
        await page.waitForURL(/\/eggs\/$/);
        log("AT-40", `${name} ${width}-${theme}: the tap opens ${new URL(page.url()).pathname}`);
      }
      await close();
    }
  }

  // AT-41, Tuesday: the drop time moves to the real Tuesday of the week 9 drop, and the browser clock reads that day.
  execFileSync("sqlite3", [storeFile("A"), "UPDATE eggs SET dropped_at = '2026-11-10T09:00:00-05:00' WHERE week = 9"]);
  log("AT-41", "The setup: sqlite3 <store> \"UPDATE eggs SET dropped_at = '2026-11-10T09:00:00-05:00' WHERE week = 9\". The browser clock is fixed with page.clock.setFixedTime.");
  api("A");
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { page, close } = await open(browser, width, theme, { clock: "2026-11-10T12:00:00-05:00" });
    await page.goto(`${CPC}/`);
    const banner = page.getByRole("region", { name: "Egg drop" });
    await expect(banner).toBeVisible();
    await page.waitForTimeout(1200);
    await shot(page, "AT-41", "tuesday", width, theme);
    log("AT-41", `tuesday ${width}-${theme} (clock 2026-11-10 12:00 ET): ${await bannerLine(page)}; link ${await banner.getByRole("link").getAttribute("href")}`);
    await close();
  }

  // AT-50: the floor scans of ADR 0025 on the egg board, the claim sheet, and the banner, at 390 and 1280 px in each theme.
  api("A");
  for (const width of [340, 390, 1280]) for (const theme of THEMES) {
    for (const part of ["board", "sheet", "banner"] as const) {
      const { page, close } = await open(browser, width, theme, { clock: "2026-11-10T12:00:00-05:00" });
      let scope: string | undefined;
      if (part === "board") {
        await page.goto(`${CPC}/eggs/`);
        await expect(page.getByText("Latest claims").first()).toBeVisible();
      } else if (part === "banner") {
        await page.goto(`${CPC}/`);
        await expect(page.getByRole("region", { name: "Egg drop" })).toBeVisible();
        scope = 'section[aria-label="Egg drop"]';
      } else {
        await findT1(page);
        await crack(page);
        if (theme === "dark") await setTheme(page, "dark");
        await page.getByRole("button", { name: /^Claim / }).click();
        await expect(page.getByRole("group", { name: "Your team" })).toBeVisible();
        scope = '[aria-labelledby="egg-claim-title"]';
      }
      await page.emulateMedia({ reducedMotion: "reduce" });
      await page.waitForTimeout(1500);
      const text = await scanText(page);
      const contrast = await scanContrast(page, scope);
      const targets = await scanTargets(page);
      const scroll = await scanScroll(page);
      const fails = [...text.failures, ...contrast, ...targets.failures, ...scroll];
      // The raw axe result of the same rule and scope as scanContrast: the count of nodes of each kind.
      const builder = new AxeBuilder({ page }).withRules(["color-contrast"]);
      const axe = await (scope === undefined ? builder : builder.include(scope)).analyze();
      const nodes = (items: typeof axe.violations) => items.reduce((sum, rule) => sum + rule.nodes.length, 0);
      const incomplete = axe.incomplete.flatMap((rule) => rule.nodes.map((node) => `${node.target.join(" ")}: ${(node.failureSummary ?? rule.help).replace(/\s+/g, " ")}`));
      const counts = `axe color-contrast nodes: violations ${nodes(axe.violations)}, incomplete ${nodes(axe.incomplete)}, passes ${nodes(axe.passes)}; ${incomplete.length ? `incomplete: ${incomplete.join(" ; ")}` : "incomplete: none"}`;
      log("AT-50", `${part} ${width}px ${theme}${scope ? ` (contrast scope ${scope})` : ""}: text prose ${text.prose}, other ${text.other}, text failures ${text.failures.length}; contrast failures ${contrast.length}; target failures ${targets.failures.length} (exempt ${targets.exempt.length}); scroll failures ${scroll.length}; ${counts}${fails.length ? ` :: ${fails.join(" ; ")}` : ""}`);
      await close();
    }
  }

  // AT-32, AT-33, and AT-36: the find, the sheet, and the passphrase field.
  api("A");
  for (const width of WIDTHS) for (const theme of THEMES) {
    for (const pass of [false, true]) {
      const { page, close } = await open(browser, width, theme, { pass });
      await findT1(page);
      await expect(page.getByRole("heading", { name: "You found an egg" })).toBeVisible();
      if (theme === "dark") await setTheme(page, "dark");
      await page.waitForTimeout(1200);
      if (!pass) await shot(page, "AT-32", "egg", width, theme);
      await crack(page);
      await page.waitForTimeout(1600);
      if (!pass) {
        await shot(page, "AT-32", "tile", width, theme);
        log("AT-32", `${width}-${theme}: letter tile "${await page.getByTestId("egg-letter").innerText()}"`);
      }
      await page.getByRole("button", { name: "Claim C" }).click();
      const team = page.getByRole("group", { name: "Your team" });
      await expect(team).toBeVisible();
      await page.waitForTimeout(800);
      if (!pass) {
        await shot(page, "AT-33", "", width, theme);
        const pills = await team.getByRole("button").allInnerTexts();
        log("AT-33", `${width}-${theme}: ${pills.length} team pills: ${pills.join(", ")}; Bo Girds is a pill: ${pills.includes("Bo Girds")}`);
      }
      await team.getByRole("button", { name: "Lil Fridge" }).click();
      await page.getByRole("button", { name: "CORNERSTONE", exact: true }).click();
      await page.waitForTimeout(600);
      const field = await page.getByLabel("Passphrase").count();
      const submit = page.locator('[aria-labelledby="egg-claim-title"] button[type="submit"], [aria-labelledby="egg-claim-title"] button:has-text("Claim C"), [aria-labelledby="egg-claim-title"] button:has-text("Enter the passphrase")').last();
      await page.getByLabel("Passphrase").scrollIntoViewIfNeeded().catch(() => {});
      await shot(page, "AT-36", pass ? "with-passphrase" : "no-passphrase", width, theme);
      log("AT-36", `${pass ? "with" : "no"} passphrase ${width}-${theme}: passphrase fields ${field}; claim button "${(await submit.innerText().catch(() => "?")).trim()}"`);
      await close();
    }
  }

  // AT-49: reduced motion on.
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { page, close } = await open(browser, width, theme, { reduced: true });
    await findT1(page);
    await expect(page.getByRole("heading", { name: "You found an egg" })).toBeVisible();
    if (theme === "dark") await setTheme(page, "dark");
    await crack(page);
    await page.waitForTimeout(100);
    await shot(page, "AT-49", "", width, theme);
    const motion = await page.getByTestId("egg-letter").evaluate((element) => {
      const all = [element, ...element.querySelectorAll("*"), ...(element.parentElement ? [element.parentElement] : [])];
      return all.map((each) => getComputedStyle(each).animationName + "/" + getComputedStyle(each).transitionDuration).join(" ");
    });
    log("AT-49", `${width}-${theme}: 100 ms after the tap: tile "${await page.getByTestId("egg-letter").innerText()}"; running animations ${(await page.evaluate(() => document.getAnimations().length))}; animation name and transition of the tile and its parent: ${motion}`);
    await close();
  }
});

test("phase A2: the claim cards, the end to end flow, and the later states", async ({ browser }) => {
  PHASE = "A2";
  api("A");
  const eggs: { id: number; target: string; letter: string }[] = (await drop(9, [])).body.eggs;
  const id = (target: string) => eggs.find((egg) => egg.target === target)!.id;
  // AT-37: the claim hero card. Each width and theme claims, then the API undoes the claim.
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { page, close } = await open(browser, width, theme, { pass: true });
    const before = (await board()).counts;
    await findT1(page);
    await crack(page);
    if (theme === "dark") await setTheme(page, "dark");
    await page.getByRole("button", { name: "Claim C" }).click();
    await page.getByRole("group", { name: "Your team" }).getByRole("button", { name: "Lil Fridge" }).click();
    await page.getByRole("button", { name: "CORNERSTONE", exact: true }).click();
    await page.getByRole("button", { name: "Claim C for CORNERSTONE" }).click();
    const card = page.getByRole("dialog", { name: "C goes to CORNERSTONE." });
    await expect(card).toBeVisible();
    await page.waitForTimeout(1800);
    await shot(page, "AT-37", "claim", width, theme);
    log("AT-37", `claim ${width}-${theme}: board found before ${before.found}; card text: ${(await card.innerText()).replace(/\n+/g, " | ")}`);
    await undo(id("luck-3"));
    await close();
  }
  // AT-51: the whole flow at 375 and 1280 px, with a shot of each step.
  for (const width of [375, 1280]) for (const theme of THEMES) {
    const { page, close } = await open(browser, width, theme, { pass: true });
    const step = (name: string, full = false) => shot(page, "AT-51", name, width, theme, full);
    await findT1(page);
    await expect(page.getByRole("heading", { name: "You found an egg" })).toBeVisible();
    if (theme === "dark") await setTheme(page, "dark");
    await page.waitForTimeout(1200);
    await step("1-egg");
    await crack(page);
    await page.waitForTimeout(1600);
    await step("2-tile");
    await page.getByRole("button", { name: "Claim C" }).click();
    await page.getByRole("group", { name: "Your team" }).getByRole("button", { name: "Lil Fridge" }).click();
    await page.getByRole("button", { name: "CORNERSTONE", exact: true }).click();
    await step("3-sheet");
    await page.getByRole("button", { name: "Claim C for CORNERSTONE" }).click();
    await expect(page.getByRole("dialog", { name: "C goes to CORNERSTONE." })).toBeVisible();
    await page.waitForTimeout(1800);
    await step("4-claimed");
    await page.getByRole("link", { name: "See the egg board" }).click();
    await expect(page).toHaveURL(/\/eggs\/$/);
    const cornerstone = page.getByRole("region", { name: /CORNERSTONE/ });
    await expect(cornerstone.getByRole("listitem").filter({ hasText: "Lil Fridge" })).toContainText("C");
    const feed = page.getByRole("region", { name: "Latest claims" });
    await expect(feed).toContainText("Lil Fridge claimed a C for CORNERSTONE.");
    await settle(page);
    await step("5-board", true);
    log("AT-51", `${width}-${theme}: CORNERSTONE row of Lil Fridge: "${(await cornerstone.getByRole("listitem").filter({ hasText: "Lil Fridge" }).first().innerText()).replace(/\n+/g, " ")}"; feed: "${(await feed.innerText()).replace(/\n+/g, " | ")}"`);
    await undo(id("luck-3"));
    await close();
  }

  // AT-41, Wednesday: one claim, then the hide and the reload.
  await claim(F1, TEEHEE, "LANSDALE");
  api("A");
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { page, close } = await open(browser, width, theme, { clock: "2026-11-11T12:00:00-05:00" });
    await page.goto(`${CPC}/`);
    const banner = page.getByRole("region", { name: "Egg drop" });
    await expect(banner).toBeVisible();
    await page.waitForTimeout(1200);
    await shot(page, "AT-41", "wednesday", width, theme);
    const line = await bannerLine(page);
    const href = await banner.getByRole("link").getAttribute("href");
    await page.getByRole("button", { name: "Hide the banner" }).click();
    await page.reload();
    await expect(page.locator('header a[href$="/eggs/"]').first()).toBeVisible();
    await page.waitForTimeout(1500);
    await shot(page, "AT-41", "hidden", width, theme);
    log("AT-41", `wednesday ${width}-${theme} (clock 2026-11-11 12:00 ET, one claim): ${line}; link ${href}; banners after the hide and the reload: ${await banner.count()}`);
    await close();
  }

  // AT-42: two of the six claimed.
  await claim(F5, LIL_FRIDGE, "EAGLES");
  api("A");
  const counts = (await board()).counts;
  log("AT-42", `The board counts: ${JSON.stringify(counts)}`);
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { page, close } = await open(browser, width, theme);
    await page.goto(`${CPC}/eggs/`);
    await expect(page.getByText("CORNERSTONE").first()).toBeVisible();
    await page.waitForTimeout(1500);
    await shot(page, "AT-42", "", width, theme);
    if (width === 1280 && theme === "light") {
      const grid = await page.evaluate(() => {
        const slots = [...document.querySelectorAll("[data-slot]")].map((each) => each.getAttribute("data-slot"));
        return slots.reduce<Record<string, number>>((all, each) => ({ ...all, [each ?? "?"]: (all[each ?? "?"] ?? 0) + 1 }), {});
      });
      log("AT-42", `The slots of the grid by their data-slot mark: ${JSON.stringify(grid)}`);
      log("AT-42", `The hero text: ${(await page.locator("main").innerText()).slice(0, 300).replace(/\n+/g, " | ")}`);
    }
    await close();
  }

  // AT-38: T1 claimed by Teehee, then found again.
  await claim(T1, TEEHEE, "CORNERSTONE");
  api("A");
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { page, close } = await open(browser, width, theme);
    await findT1(page);
    const card = page.getByRole("dialog", { name: "Another manager claimed first." });
    await expect(card).toBeVisible();
    if (theme === "dark") await setTheme(page, "dark");
    await page.waitForTimeout(1500);
    await shot(page, "AT-38", "", width, theme);
    log("AT-38", `${width}-${theme}: ${(await card.innerText()).replace(/\n+/g, " | ")}`);
    await close();
  }

  // AT-39: the limit of the egg check hit for 127.0.0.1, then three taps.
  api("A");
  let last = 0;
  for (let i = 0; i < 60; i += 1) last = (await post("/check", T2)).status;
  const over = await retry(`${API}/check`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(T2) });
  log("AT-39", `60 checks from 127.0.0.1: the 60th answered ${last}. The 61st answered ${over.status} with Retry-After ${over.headers.get("retry-after")}.`);
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { page, close } = await open(browser, width, theme);
    await findT1(page);
    const card = page.getByRole("dialog");
    await expect(card).toContainText("The eggs need a rest");
    if (theme === "dark") await setTheme(page, "dark");
    await page.waitForTimeout(1500);
    await shot(page, "AT-39", "", width, theme);
    log("AT-39", `${width}-${theme}: ${(await card.innerText()).replace(/\n+/g, " | ")}`);
    await close();
  }
});

test("phase B: Teehee holds the C of CORNERSTONE", async ({ browser }) => {
  PHASE = "B";
  api("B", true);
  const leaders = { page: "/2026/week-08/", target: "heading-leaders", action: "tap2", conditions: {} };
  const w9 = [F1, leaders, ...["heading-standings", "heading-next-week", "heading-trades", "heading-median"].map((target) => ({ page: "/2026/week-08/", target, action: "tap2", conditions: {} }))];
  const w10 = [{ page: "/midseason/2026/", target: "heading-arcs", action: "tap2", conditions: {} }, T1,
    ...["heading-draft", "heading-waivers", "heading-records", "heading-injuries"].map((target) => ({ page: "/midseason/2026/", target, action: "tap2", conditions: {} }))];
  const a = await drop(9, w9);
  const b = await drop(10, w10);
  log("AT-34", `The setup: the drop of week 9 ${JSON.stringify(a.body.eggs.map((egg: { target: string; letter: string }) => [egg.target, egg.letter]))}`);
  log("AT-34", `and of week 10 ${JSON.stringify(b.body.eggs.map((egg: { target: string; letter: string }) => [egg.target, egg.letter]))}.`);
  log("AT-34", `Teehee claims the C of heading-leaders into CORNERSTONE: ${JSON.stringify(await claim(leaders, TEEHEE, "CORNERSTONE"))}`);
  api("B");
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { page, close } = await open(browser, width, theme, { pass: true });
    await findT1(page);
    await crack(page);
    if (theme === "dark") await setTheme(page, "dark");
    await page.getByRole("button", { name: "Claim C" }).click();
    const team = page.getByRole("group", { name: "Your team" });
    await team.getByRole("button", { name: "Teehee" }).click();
    await page.waitForTimeout(900);
    const words = page.getByRole("group", { name: "Egg word" });
    await words.scrollIntoViewIfNeeded();
    await shot(page, "AT-34", "teehee", width, theme);
    const state = await words.evaluate((group) => [...group.querySelectorAll("button")].map((button) => `${button.innerText.split("\n")[0]} disabled=${button.disabled || button.getAttribute("aria-disabled") === "true"} ghost=${button.querySelectorAll("[data-ghost], .egg-ghost").length} background=${getComputedStyle(button).backgroundColor} border=${getComputedStyle(button).borderTopStyle} ${getComputedStyle(button).borderTopColor} text=${getComputedStyle(button.querySelector("span, p, div") ?? button).color}`));
    const notice = page.getByText("Claim it as a block.");
    if (await notice.count()) await notice.scrollIntoViewIfNeeded();
    await shot(page, "AT-35", "", width, theme);
    log("AT-34", `teehee ${width}-${theme}: ${state.join("; ")}`);
    log("AT-35", `teehee ${width}-${theme}: block notice shows ${await notice.count()}; its text: ${(await notice.count()) ? (await notice.locator("..").innerText()).replace(/\n+/g, " | ") : "none"}`);
    // A picked team folds the pills into one pill and "Change", so the change of team taps "Change" first.
    await page.getByRole("button", { name: "Change" }).click();
    await team.getByRole("button", { name: "Lil Fridge" }).click();
    await page.waitForTimeout(900);
    await words.scrollIntoViewIfNeeded();
    await shot(page, "AT-34", "lil-fridge", width, theme);
    const other = await words.evaluate((group) => [...group.querySelectorAll("button")].map((button) => `${button.innerText.split("\n")[0]} disabled=${button.disabled || button.getAttribute("aria-disabled") === "true"} ghost=${button.querySelectorAll("[data-ghost], .egg-ghost").length} background=${getComputedStyle(button).backgroundColor} border=${getComputedStyle(button).borderTopStyle} ${getComputedStyle(button).borderTopColor} text=${getComputedStyle(button.querySelector("span, p, div") ?? button).color}`));
    log("AT-34", `lil-fridge ${width}-${theme}: ${other.join("; ")}`);
    await close();
  }

  // AT-45: two claims and one block.
  log("AT-45", `Lil Fridge claims the A of week 9 into LANSDALE: ${JSON.stringify(await claim(F1, LIL_FRIDGE, "LANSDALE"))}`);
  log("AT-45", `Teehee claims T1, letter C, as a block: ${JSON.stringify(await claim(T1, TEEHEE, null))}`);
  const state = await board();
  log("AT-45", `The board: counts ${JSON.stringify(state.counts)}; latest ${JSON.stringify(state.latest)}`);
  api("B");
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { page, close } = await open(browser, width, theme);
    await page.goto(`${CPC}/eggs/`);
    const feed = page.getByRole("region", { name: "Latest claims" });
    await expect(feed).toBeVisible();
    await settle(page);
    await feed.scrollIntoViewIfNeeded();
    await feed.screenshot({ path: join(folder("AT-45"), `${width}-${theme}.png`) });
    if (width === 1280 && theme === "light") log("AT-45", `The feed text: ${(await feed.innerText()).replace(/\n+/g, " | ")}`);
    await close();
  }

  // AT-43: letters for seven managers, then "Show all 11" on the CORNERSTONE card.
  const heading = (target: string) => ({ page: "/2026/week-08/", target, action: "tap2", conditions: {} });
  const mid = (target: string) => ({ page: "/midseason/2026/", target, action: "tap2", conditions: {} });
  // The letters of the drops: week 9 standings D, next-week E, trades G, median L; week 10 waivers E.
  await claim(heading("heading-next-week"), 1, "CORNERSTONE");
  await claim(mid("heading-waivers"), 2, "CORNERSTONE");
  await claim(heading("heading-standings"), 4, "LANSDALE");
  await claim(heading("heading-trades"), 5, "EAGLES");
  await claim(heading("heading-median"), 7, "LANSDALE");
  const seven = await board();
  const holders = new Set<string>();
  for (const word of seven.words) for (const manager of word.managers) if (manager.letters.length) holders.add(manager.team);
  log("AT-43", `Managers with letters: ${holders.size}: ${[...holders].join(", ")}. Counts ${JSON.stringify(seven.counts)}.`);
  api("B");
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { page, close } = await open(browser, width, theme);
    await page.goto(`${CPC}/eggs/`);
    const card = page.getByRole("region", { name: /CORNERSTONE/ });
    await expect(card).toBeVisible();
    await settle(page);
    await page.waitForTimeout(600);
    const words = page.locator("main");
    await shot(page, "AT-43", "before", width, theme, true);
    const rows = await card.getByRole("listitem").count();
    const prizes = await words.evaluate((main) => (main.textContent?.match(/\$\d+/g) ?? []).join(" "));
    await card.getByRole("button", { name: /Show all 11/ }).click();
    await page.waitForTimeout(800);
    await card.scrollIntoViewIfNeeded();
    await card.screenshot({ path: join(folder("AT-43"), `after-${width}-${theme}.png`) });
    log("AT-43", `${width}-${theme}: CORNERSTONE rows before ${rows}, after the tap ${await card.getByRole("listitem").count()}; prizes on the page: ${prizes}`);
    await close();
  }
});

test("phase E: the EAGLES store", async ({ browser }) => {
  PHASE = "E";
  api("E");
  // AT-37, the second hero card: the claim that fills EAGLES. Each width and theme claims, then the API undoes the claim.
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { page, close } = await open(browser, width, theme, { pass: true });
    await page.goto(`${CPC}/midseason/2026/`);
    await page.getByRole("link", { name: /^Egg board/ }).first().waitFor({ timeout: 30000 });
    const cell = page.locator('[data-stable-id="luck-5"]');
    await cell.scrollIntoViewIfNeeded();
    await cell.click({ clickCount: 2 });
    await crack(page);
    if (theme === "dark") await setTheme(page, "dark");
    await page.getByRole("button", { name: "Claim E" }).click();
    await page.getByRole("group", { name: "Your team" }).getByRole("button", { name: "Lil Fridge" }).click();
    await page.getByRole("button", { name: "EAGLES", exact: true }).click();
    await page.getByRole("button", { name: "Claim E for EAGLES" }).click();
    const card = page.getByRole("dialog").last();
    await expect(card).toContainText(/EAGLES/);
    await page.waitForTimeout(1800);
    await shot(page, "AT-37", "won", width, theme);
    log("AT-37", `won ${width}-${theme}: card text: ${(await card.innerText()).replace(/\n+/g, " | ")}`);
    await undo(28);
    await close();
  }
  // AT-12 runs its claims with curl here, then AT-44 shows the won word.
  execFileSync("bash", [join(TOOLS, "api-store-e2.sh")], { env: { ...process.env, EV }, stdio: "pipe" });
  api("E");
  for (const width of WIDTHS) for (const theme of THEMES) {
    const { page, close } = await open(browser, width, theme);
    await page.goto(`${CPC}/eggs/`);
    const card = page.getByRole("region", { name: /EAGLES/ });
    await expect(card).toBeVisible();
    await settle(page);
    await card.scrollIntoViewIfNeeded();
    await page.waitForTimeout(600);
    await card.screenshot({ path: join(folder("AT-44"), `${width}-${theme}.png`) });
    if (width === 1280 && theme === "light") log("AT-44", `The EAGLES card text: ${(await card.innerText()).replace(/\n+/g, " | ")}`);
    await close();
  }
});

/* Tap the middle of the element with the mouse, with no wait for the checks of a Playwright click, so a gap stays short. */
async function tapAt(page: Page, selector: string) {
  const box = (await page.locator(selector).first().boundingBox())!;
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
}

test("phase L: the double-tap and the sim frames", async ({ browser }) => {
  PHASE = "L";
  api("A");
  {
    const { page, checks, close } = await open(browser, 1280, "light");
    await page.goto(`${CPC}/midseason/2026/`);
    await page.getByRole("link", { name: /^Egg board/ }).first().waitFor({ timeout: 30000 });
    await page.locator('[data-stable-id="luck-3"]').scrollIntoViewIfNeeded();
    await page.waitForTimeout(500);
    const at = await page.evaluate(() => {
      const times: number[] = [];
      window.addEventListener("pointerup", () => times.push(Math.round(performance.now())), true);
      (window as unknown as { eeTimes: number[] }).eeTimes = times;
      return 0;
    });
    void at;
    for (let i = 0; i < 2; i += 1) {
      await tapAt(page, '[data-stable-id="luck-3"]');
      if (i < 1) await page.waitForTimeout(150);
    }
    await page.waitForTimeout(1200);
    const times = await page.evaluate(() => (window as unknown as { eeTimes: number[] }).eeTimes);
    log("AT-26", `Two mouse taps on [data-stable-id="luck-3"] of /midseason/2026/ in the light theme. The pointerup times of the page, in ms from the first: ${times.map((t) => t - times[0]).join(", ")}.`);
    log("AT-26", `Checks sent: ${checks.length}`);
    checks.forEach((body) => log("AT-26", `body: ${body}`));
    log("AT-26", `The card after the answer (store A holds a claim of T1 by Teehee from AT-38, so the card is the claimed-first card): ${(await page.getByRole("dialog").allInnerTexts()).join(" ").replace(/\n+/g, " | ")}`);
    await close();
  }
  {
    const { page, checks, close } = await open(browser, 1280, "light");
    await page.goto(`${CPC}/midseason/2026/`);
    await page.getByRole("link", { name: /^Egg board/ }).first().waitFor({ timeout: 30000 });
    await page.getByRole("button", { name: "Sim the season" }).scrollIntoViewIfNeeded();
    // A watch in the page marks the time of each change of the frame: the text of the standings row of roster 3.
    await page.evaluate(() => {
      const w = window as unknown as { eeChanges: { t: number; text: string }[] };
      w.eeChanges = [];
      let last = "";
      const tick = () => {
        const text = document.querySelector('[data-stable-id="sim-row-3"]')?.textContent ?? "";
        if (text !== last) { w.eeChanges.push({ t: Math.round(performance.now()), text: text.slice(0, 40) }); last = text; }
        requestAnimationFrame(tick);
      };
      tick();
      window.addEventListener("pointerup", () => w.eeChanges.push({ t: Math.round(performance.now()), text: "TAP" }), true);
    });
    await page.getByRole("button", { name: "Sim the season" }).click();
    await page.locator('[data-stable-id="sim-row-3"]').first().scrollIntoViewIfNeeded();
    const changes = () => page.evaluate(() => (window as unknown as { eeChanges: { t: number; text: string }[] }).eeChanges.filter((c) => c.text !== "TAP"));
    // Wait for three changes of the frame, to learn the time of one frame.
    while ((await changes()).length < 4) await page.waitForTimeout(20);
    const seen = await changes();
    const period = seen.at(-1)!.t - seen.at(-2)!.t;
    const now = await page.evaluate(() => performance.now());
    const next = seen.at(-1)!.t + period;
    // The first tap lands 150 ms before the next frame, and the second tap 200 ms later, so a frame changes between taps.
    await page.waitForTimeout(Math.max(0, next - 150 - now));
    for (let i = 0; i < 2; i += 1) {
      await tapAt(page, '[data-stable-id="sim-row-3"]');
      if (i < 1) await page.waitForTimeout(200);
    }
    await page.waitForTimeout(1200);
    const all = await page.evaluate(() => (window as unknown as { eeChanges: { t: number; text: string }[] }).eeChanges);
    // The first pointerup is the press of "Sim the season", so the two taps on the row are the last two.
    const first = all.filter((c) => c.text === "TAP").at(-2)!.t;
    log("AT-30", `The replay runs. One frame lasts about ${period} ms. The taps and the frame changes of [data-stable-id="sim-row-3"] near the taps, in ms from the first tap:`);
    log("AT-30", `Pointerups seen by the page: ${all.filter((c) => c.text === "TAP").length}.`);
    all.filter((c) => c.t - first > -1600 && c.t - first < 2000).forEach((c) => log("AT-30", `${c.t - first}: ${c.text === "TAP" ? "TAP" : `frame: ${c.text}`}`));
    log("AT-30", `Checks sent: ${checks.length}`);
    checks.forEach((body) => log("AT-30", `body: ${body}`));
    await close();
  }
});

test("phase P47: the hunt hides before the first drop", async ({ browser }) => {
  PHASE = "P47";
  api("P47", true);
  const answer = await board();
  writeFileSync(join(folder("AT-47"), "board.json"), JSON.stringify(answer, null, 2));
  log("AT-47", `The board answer of the empty store: counts ${JSON.stringify(answer.counts)}, last_drop ${JSON.stringify(answer.last_drop)}.`);
  for (const [name, route] of [["home", "/"], ["week-08", "/2026/week-08/"], ["eggs", "/eggs/"]] as const) {
    for (const width of WIDTHS) for (const theme of THEMES) {
      const { page, close } = await open(browser, width, theme);
      const response = await page.goto(`${CPC}${route}`);
      // The board read decides the hunt, so the shot waits for that answer and a settle.
      await page.waitForResponse((r) => r.url().includes("/eggs/board"), { timeout: 10000 }).catch(() => {});
      await settle(page);
      await shot(page, "AT-47", name, width, theme, true);
      const button = await page.getByRole("link", { name: /^Egg board/ }).count();
      const banner = await page.locator('section[aria-label="Egg drop"]').count();
      let extra = "";
      if (name === "eggs") {
        const hero = await page.locator('[data-not-found], [data-stable-id="not-found-hero"]').count();
        const main = await page.locator("main").innerText().catch(() => "");
        const copy = (main.match(/Egg Board|egg word|CORNERSTONE|LANSDALE|EAGLES|LEFT TO FIND|How the hunt works/gi) ?? []).length;
        extra = `; HTTP status ${response?.status()}; 404 hero marks ${hero}; text "${main.replace(/\s+/g, " ").slice(0, 80)}"; egg copy matches in main ${copy}`;
      }
      log("AT-47", `${name} ${width}-${theme}: egg buttons ${button}, egg banners ${banner}${extra}`);
      await close();
    }
  }
  for (const theme of THEMES) {
    const { page, checks, close } = await open(browser, 1280, theme);
    await page.goto(`${CPC}/midseason/2026/`);
    await page.waitForTimeout(1500);
    if (theme === "light") await setTheme(page, "light");
    await page.locator('[data-stable-id="luck-3"]').scrollIntoViewIfNeeded();
    await page.evaluate(() => {
      const w = window as unknown as { eeTimes: number[] };
      w.eeTimes = [];
      window.addEventListener("pointerup", () => w.eeTimes.push(Math.round(performance.now())), true);
    });
    for (let i = 0; i < 2; i += 1) {
      await tapAt(page, '[data-stable-id="luck-3"]');
      if (i < 1) await page.waitForTimeout(150);
    }
    await page.waitForTimeout(1500);
    const times = await page.evaluate(() => (window as unknown as { eeTimes: number[] }).eeTimes);
    log("AT-47", `Two mouse taps on [data-stable-id="luck-3"] of /midseason/2026/ at 1280 px, ${theme} theme, pointerups at ${times.map((t) => t - times[0]).join(", ")} ms. Requests to /eggs/check: ${checks.length}${checks.length ? ` ${JSON.stringify(checks)}` : ""}. Dialogs: ${await page.getByRole("dialog").count()}.`);
    await close();
  }
  execFileSync("bash", [join(TOOLS, "stop-api.sh")], { env: { ...process.env }, stdio: "pipe" });
});

/* Install a sampler in the page: snap(label) records, in ms from window.eeT0, each part of the find with its computed
   style and each running animation (name, play state, duration, current time). */
async function installSampler(page: Page) {
  await page.evaluate(() => {
    const w = window as unknown as { eeT0: number; eeSnaps: unknown[]; eeSnap: (label: string) => void };
    w.eeSnaps = [];
    const parts: [string, string][] = [
      ["scrim", ".egg-scrim"], ["ring", ".egg-ripple"], ["halo", ".egg-halo"], ["egg", 'button[aria-label="Crack the egg"] svg'],
      ["half", ".egg-half"], ["crack", ".egg-crack"], ["burst", ".egg-burst"], ["tile", '[data-testid="egg-letter"]'],
    ];
    w.eeSnap = (label: string) => {
      const t = Math.round(performance.now() - w.eeT0);
      const found = parts.flatMap(([name, selector]) => [...document.querySelectorAll(selector)].map((element, index) => {
        const style = getComputedStyle(element);
        const animations = element.getAnimations().map((a) => {
          const css = a as CSSAnimation;
          const timing = a.effect?.getComputedTiming();
          return `${css.animationName ?? "?"} ${a.playState} dur ${Math.round(Number(timing?.duration ?? 0))}ms delay ${Math.round(Number(timing?.delay ?? 0))}ms iter ${timing?.iterations} at ${Math.round(Number(a.currentTime ?? 0))}ms`;
        });
        const extra = name === "scrim" ? ` backdrop-filter ${style.backdropFilter || (style as unknown as Record<string, string>).webkitBackdropFilter}` : name === "crack" ? ` stroke-dashoffset ${style.strokeDashoffset}` : "";
        return `${name}${index ? index + 1 : ""}: opacity ${Number(style.opacity).toFixed(2)} transform ${style.transform}${extra} | ${animations.join("; ") || "no animation"}`;
      }));
      w.eeSnaps.push(`[${t} ms] ${label}: ${found.join(" || ") || "no part of the find"}`);
    };
  });
}
const snaps = (page: Page) => page.evaluate(() => (window as unknown as { eeSnaps: string[] }).eeSnaps);

test("phase M32: the motion of the find", async ({ browser }) => {
  PHASE = "M32";
  api("M32", true);
  await drop(9, [F1, T1, T2, T3, F5, F6]);
  for (const width of [375, 1280]) for (const theme of THEMES) {
    const dir = join(SCRATCH, `video-${width}-${theme}`);
    execFileSync("rm", ["-rf", dir]);
    const context = await browser.newContext({ viewport: { width, height: 900 }, reducedMotion: "no-preference", recordVideo: { dir, size: { width, height: 900 } } });
    await context.addInitScript(() => { try { if (!sessionStorage.getItem("ee")) { localStorage.setItem("cpc.theme", "light"); sessionStorage.setItem("ee", "1"); } } catch {} });
    const page = await context.newPage();
    await page.goto(`${CPC}/midseason/2026/`);
    const cell = page.locator('[data-stable-id="luck-3"]');
    await cell.scrollIntoViewIfNeeded();
    await page.waitForTimeout(800);
    await installSampler(page);
    const name = (n: string) => join(folder("AT-32"), `motion-${width}-${theme}-${n}.png`);
    // The double-tap: window.eeT0 is the time of the first tap. The listener mounts after the board names a drop.
    await page.getByRole("link", { name: /^Egg board/ }).first().waitFor({ timeout: 30000 });
    await page.evaluate(() => { (window as unknown as { eeT0: number }).eeT0 = performance.now(); });
    const t0 = Date.now();
    await cell.click({ clickCount: 2 });
    await page.getByRole("heading", { name: "You found an egg" }).waitFor();
    if (theme === "dark") await page.evaluate(() => { document.documentElement.classList.add("dark"); localStorage.setItem("cpc.theme", "dark"); });
    await page.evaluate(() => (window as unknown as { eeSnap: (l: string) => void }).eeSnap("the find card shows"));
    await page.screenshot({ path: name(`find-${Date.now() - t0}ms`) });
    await page.waitForTimeout(250);
    await page.evaluate(() => (window as unknown as { eeSnap: (l: string) => void }).eeSnap("the ring grows"));
    await page.screenshot({ path: name(`find-${Date.now() - t0}ms`) });
    await page.waitForTimeout(1500);
    await page.evaluate(() => (window as unknown as { eeSnap: (l: string) => void }).eeSnap("the egg bobs, the ring is done"));
    await page.screenshot({ path: name(`find-${Date.now() - t0}ms`) });
    // The tap on the egg: window.eeT0 restarts, and the sampler runs every 75 ms inside the page.
    await page.evaluate(() => {
      const w = window as unknown as { eeT0: number; eeSnap: (l: string) => void };
      w.eeT0 = performance.now();
      document.querySelector<HTMLButtonElement>('button[aria-label="Crack the egg"]')!.click();
      for (let at = 0; at <= 1500; at += 75) setTimeout(() => w.eeSnap(`after the tap on the egg`), at);
    });
    const t1 = Date.now();
    for (const target of [0, 150, 300, 450, 600, 900, 1200, 1600]) {
      const wait = t1 + target - Date.now();
      if (wait > 0) await page.waitForTimeout(wait);
      await page.screenshot({ path: name(`crack-${String(Date.now() - t1).padStart(4, "0")}ms`) });
    }
    await page.waitForTimeout(400);
    log("AT-32", `=== ${width} px, ${theme} theme. The find in the light theme${theme === "dark" ? ", then the switch to the dark theme as the card shows" : ""}. Times in ms from the first tap, then from the tap on the egg.`);
    for (const line of await snaps(page)) log("AT-32", line);
    await context.close();
    const video = (await import("node:fs")).readdirSync(dir).find((file) => file.endsWith(".webm"));
    if (video) execFileSync("cp", [join(dir, video), join(folder("AT-32"), `motion-${width}-${theme}.webm`)]);
  }
  execFileSync("bash", [join(TOOLS, "stop-api.sh")], { env: { ...process.env }, stdio: "pipe" });
});

test("phase M34: the pulse of the ghost tile", async ({ browser }) => {
  PHASE = "M34";
  api("M34", true);
  const leaders = { page: "/2026/week-08/", target: "heading-leaders", action: "tap2", conditions: {} };
  await drop(9, [F1, leaders, ...["heading-standings", "heading-next-week", "heading-trades", "heading-median"].map((target) => ({ page: "/2026/week-08/", target, action: "tap2", conditions: {} }))]);
  await drop(10, [{ page: "/midseason/2026/", target: "heading-arcs", action: "tap2", conditions: {} }, T1,
    ...["heading-draft", "heading-waivers", "heading-records", "heading-injuries"].map((target) => ({ page: "/midseason/2026/", target, action: "tap2", conditions: {} }))]);
  log("AT-34", `The setup, as phase B: Teehee claims the C of heading-leaders into CORNERSTONE: ${JSON.stringify(await claim(leaders, TEEHEE, "CORNERSTONE"))}`);
  api("M34");
  for (const width of [375, 1280]) for (const theme of THEMES) {
    const { page, close } = await open(browser, width, theme, { pass: true });
    await findT1(page);
    await crack(page);
    if (theme === "dark") await setTheme(page, "dark");
    await page.getByRole("button", { name: "Claim C" }).click();
    await page.getByRole("group", { name: "Your team" }).getByRole("button", { name: "Lil Fridge" }).click();
    const ghost = page.locator('[role="group"][aria-label="Egg word"] button').filter({ hasText: "CORNERSTONE" }).locator(".egg-ghost").first();
    await ghost.scrollIntoViewIfNeeded();
    await page.waitForTimeout(500);
    const read = () => ghost.evaluate((element) => {
      const style = getComputedStyle(element);
      const a = element.getAnimations()[0] as CSSAnimation | undefined;
      const timing = a?.effect?.getComputedTiming();
      return `opacity ${Number(style.opacity).toFixed(3)} | ${a ? `${a.animationName} ${a.playState} dur ${Math.round(Number(timing?.duration))}ms iter ${timing?.iterations} at ${Math.round(Number(a.currentTime))}ms` : "no animation"}`;
    });
    const start = Date.now();
    for (let i = 0; i < 4; i += 1) {
      const wait = start + i * 400 - Date.now();
      if (wait > 0) await page.waitForTimeout(wait);
      const line = await read();
      log("AT-34", `ghost ${width}-${theme} at +${Date.now() - start} ms: ${line}`);
      if (i < 3) {
        const box = (await ghost.boundingBox())!;
        await page.screenshot({ path: join(folder("AT-34"), `ghost-${width}-${theme}-${i + 1}.png`), clip: { x: Math.max(0, box.x - 24), y: Math.max(0, box.y - 24), width: box.width + 48, height: box.height + 48 } });
      }
    }
    await close();
  }
  execFileSync("bash", [join(TOOLS, "stop-api.sh")], { env: { ...process.env }, stdio: "pipe" });
});

/* Install a log of the pointer events and of the menu events in the page. The log of a menu event runs on the window
   in the bubble phase, after the listener of the hunt on the document, so it reads the blocked state that the hunt set. */
async function installEventLog(page: Page) {
  await page.evaluate(() => {
    const w = window as unknown as { eeT0: number; eeEvents: string[]; eeLog?: boolean };
    w.eeT0 = performance.now();
    w.eeEvents = [];
    // A second call only clears the log, so each event shows one time.
    if (w.eeLog) return;
    w.eeLog = true;
    const at = () => Math.round(performance.now() - w.eeT0);
    const where = (event: Event) => {
      const element = event.target instanceof Element ? event.target : null;
      const id = element?.closest("[data-stable-id]")?.getAttribute("data-stable-id") ?? "none";
      return `${element?.tagName.toLowerCase() ?? "?"} in ${id}`;
    };
    for (const name of ["pointerdown", "pointerup", "pointercancel"]) {
      window.addEventListener(name, (event) => w.eeEvents.push(`${at()} ms ${name} ${(event as PointerEvent).pointerType} on ${where(event)}`), true);
    }
    window.addEventListener("contextmenu", (event) => w.eeEvents.push(`${at()} ms contextmenu on ${where(event)}: blocked (defaultPrevented) ${event.defaultPrevented}`));
  });
}
const events = (page: Page) => page.evaluate(() => (window as unknown as { eeEvents: string[] }).eeEvents);

/* The middle of the first element that matches. */
async function middle(page: Page, selector: string) {
  const box = (await page.locator(selector).first().boundingBox())!;
  return { x: Math.round(box.x + box.width / 2), y: Math.round(box.y + box.height / 2) };
}

test("phase N: the touch hold, the burst, the blurb, and the analyzer", async ({ browser }) => {
  PHASE = "N";
  api("N", true);
  const analyzer = { page: "/analyze/", target: "verdict-word", action: "tap2", conditions: { trade_teams: [1, 3] } };
  const dropped = await drop(9, [T1, analyzer, F5]);
  for (const at of ["AT-52", "AT-54", "AT-55", "AT-56"]) {
    log(at, `The setup: a fresh store and the drop of week 9, so the hunt mounts its listener: ${JSON.stringify(dropped.body.eggs.map((egg: { id: number; page: string; target: string; action: string; conditions: unknown }) => [egg.id, egg.page, egg.target, egg.action, egg.conditions]))}`);
  }

  // AT-52: a touch press of 2.2 s with a menu event during the press, then the menu events that keep their menu.
  {
    const context = await browser.newContext({ viewport: { width: 375, height: 900 }, hasTouch: true, isMobile: true });
    await context.addInitScript(() => { try { localStorage.setItem("cpc.theme", "light"); } catch {} });
    const page = await context.newPage();
    const checks: string[] = [];
    page.on("request", (request) => { if (request.url().includes("/eggs/check")) checks.push(request.postData() ?? ""); });
    await page.goto(`${CPC}/midseason/2026/`);
    await page.getByRole("link", { name: /^Egg board/ }).first().waitFor({ timeout: 30000 });
    const cdp = await context.newCDPSession(page);
    const link = "main a[href]";
    const image = "main img";
    log("AT-52", `375 px, light, a touch context (hasTouch, isMobile) of Chromium ${browser.version()}. The touch press runs with Input.dispatchTouchEvent of the DevTools protocol.`);
    log("AT-52", "During each touch press the spec fires a cancelable contextmenu MouseEvent on the element under the press, as Android Chrome does. The event log shows each pointer event and each menu event that the page saw.");
    const press = async (name: string, selector: string, ms: number) => {
      await page.locator(selector).first().scrollIntoViewIfNeeded();
      await page.waitForTimeout(400);
      const point = await middle(page, selector);
      await installEventLog(page);
      const before = checks.length;
      const start = Date.now();
      await cdp.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x: point.x, y: point.y }] });
      await page.waitForTimeout(700);
      // dispatchEvent answers false when a listener called preventDefault.
      const kept = await page.evaluate(({ x, y }) => document.elementFromPoint(x, y)!.dispatchEvent(new MouseEvent("contextmenu", { bubbles: true, cancelable: true, clientX: x, clientY: y })), point);
      await page.waitForTimeout(Math.max(0, ms - (Date.now() - start)));
      await cdp.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
      const held = Date.now() - start;
      await page.waitForTimeout(1200);
      log("AT-52", `${name}: a touch press of ${held} ms at (${point.x}, ${point.y}) on ${selector}, with a contextmenu event at about 700 ms. dispatchEvent answered ${kept}, so the menu was ${kept ? "kept" : "blocked"}.`);
      (await events(page)).forEach((line) => log("AT-52", `  ${line}`));
      log("AT-52", `  checks sent by this press: ${checks.length - before}`);
      checks.slice(before).forEach((body) => log("AT-52", `  body: ${body}`));
      await page.keyboard.press("Escape");
      await page.waitForTimeout(600);
    };
    const rightClick = async (name: string, selector: string) => {
      await page.locator(selector).first().scrollIntoViewIfNeeded();
      await page.waitForTimeout(400);
      const point = await middle(page, selector);
      await installEventLog(page);
      const before = checks.length;
      await page.mouse.click(point.x, point.y, { button: "right" });
      await page.waitForTimeout(1200);
      log("AT-52", `${name}: a mouse right-click at (${point.x}, ${point.y}) on ${selector}.`);
      (await events(page)).forEach((line) => log("AT-52", `  ${line}`));
      log("AT-52", `  checks sent by this right-click: ${checks.length - before}`);
      await page.keyboard.press("Escape");
    };
    log("AT-52", `The link: ${await page.locator(link).first().evaluate((a) => `${a.getAttribute("href")} in ${a.closest("[data-stable-id]")?.getAttribute("data-stable-id") ?? "no stable id"}`)}. The image: ${await page.locator(image).first().evaluate((i) => `${(i.getAttribute("src") ?? "").slice(0, 50)} in ${i.closest("[data-stable-id]")?.getAttribute("data-stable-id") ?? "no stable id"}`)}.`);
    await press("1. the Luck cell of Lil Fridge", '[data-stable-id="luck-3"]', 2200);
    await rightClick("2. the Luck cell of Lil Fridge", '[data-stable-id="luck-3"]');
    await rightClick("3. a link", link);
    await rightClick("4. an image", image);
    await press("5. a link", link, 2200);
    await press("6. an image", image, 2200);
    log("AT-52", `Checks sent in all: ${checks.length}`);
    await context.close();
  }

  // AT-55: three fast taps on the Luck cell of Lil Fridge, then five fast taps on another cell.
  {
    const { page, checks, close } = await open(browser, 1280, "light");
    await page.goto(`${CPC}/midseason/2026/`);
    await page.getByRole("link", { name: /^Egg board/ }).first().waitFor({ timeout: 30000 });
    await page.locator('[data-stable-id="luck-3"]').scrollIntoViewIfNeeded();
    await page.waitForTimeout(500);
    for (const [target, count] of [["luck-3", 3], ["luck-5", 5]] as const) {
      await installEventLog(page);
      const before = checks.length;
      for (let i = 0; i < count; i += 1) {
        await tapAt(page, `[data-stable-id="${target}"]`);
        if (i < count - 1) await page.waitForTimeout(150);
      }
      await page.waitForTimeout(1500);
      const ups = (await events(page)).filter((line) => line.includes("pointerup"));
      log("AT-55", `${count} mouse taps on [data-stable-id="${target}"] of /midseason/2026/ at 1280 px, light. The pointerups: ${ups.join("; ")}.`);
      log("AT-55", `  checks sent by these taps: ${checks.length - before}${checks.length - before ? ` ${JSON.stringify(checks.slice(before))}` : ""}; dialogs open: ${await page.getByRole("dialog").count()}`);
    }
    log("AT-55", `Checks sent in all: ${checks.length}`);
    await close();
  }

  // AT-56: a double-tap at two places of one blurb, by touch at 375 px and by mouse at 1280 px.
  for (const [width, touch] of [[375, true], [1280, false]] as const) {
    const context = await browser.newContext({ viewport: { width, height: 900 }, hasTouch: touch, isMobile: touch });
    await context.addInitScript(() => { try { localStorage.setItem("cpc.theme", "light"); } catch {} });
    const page = await context.newPage();
    const checks: string[] = [];
    page.on("request", (request) => { if (request.url().includes("/eggs/check")) checks.push(request.postData() ?? ""); });
    await page.goto(`${CPC}/midseason/2026/`);
    await page.getByRole("link", { name: /^Egg board/ }).first().waitFor({ timeout: 30000 });
    // The first blurb of the page. The site makes each blurb id from its text, so the spec names it blurb-luck, the id of the test.
    const blurb = page.locator('[data-stable-id^="blurb-"]').first();
    const real = await blurb.getAttribute("data-stable-id");
    await blurb.evaluate((element) => element.setAttribute("data-stable-id", "blurb-luck"));
    const target = page.locator('[data-stable-id="blurb-luck"]');
    await target.scrollIntoViewIfNeeded();
    await page.waitForTimeout(500);
    const box = (await target.boundingBox())!;
    log("AT-56", `${width} px, light, ${touch ? "touch taps (page.touchscreen.tap)" : "mouse taps (page.mouse.click)"}. The first blurb of /midseason/2026/ has the real id ${real}. The spec set its data-stable-id to blurb-luck. Its box: ${Math.round(box.width)} x ${Math.round(box.height)} px.`);
    const places = [{ name: "near the start", x: box.x + 12, y: box.y + 10 }, { name: "near the end", x: box.x + box.width - 24, y: box.y + box.height - 10 }];
    for (const place of places) {
      await installEventLog(page);
      const before = checks.length;
      for (let i = 0; i < 2; i += 1) {
        if (touch) await page.touchscreen.tap(place.x, place.y);
        else await page.mouse.click(place.x, place.y);
        if (i < 1) await page.waitForTimeout(150);
      }
      await page.waitForTimeout(1500);
      const ups = (await events(page)).filter((line) => line.includes("pointerup"));
      log("AT-56", `  a double-tap ${place.name} of the blurb at (${Math.round(place.x)}, ${Math.round(place.y)}). The pointerups: ${ups.join("; ")}. The selection after: "${await page.evaluate(() => document.getSelection()?.toString() ?? "")}".`);
      log("AT-56", `  checks sent by this double-tap: ${checks.length - before}`);
      checks.slice(before).forEach((body) => log("AT-56", `  body: ${body}`));
      await page.evaluate(() => document.getSelection()?.removeAllRanges());
      await page.keyboard.press("Escape");
      await page.waitForTimeout(800);
    }
    await context.close();
  }

  // AT-54: a graded trade of The Blue Tent (1) and Lil Fridge (3), then a double-tap on the verdict word.
  {
    const { page, checks, close } = await open(browser, 1280, "light");
    await page.goto(`${CPC}/analyze/`);
    await page.locator("input[type=password]").fill("localtest");
    await page.locator("button[type=submit]").click();
    await page.getByRole("button", { name: "Pick Your Team" }).click();
    await page.getByRole("list", { name: "Teams" }).getByRole("button", { name: /The Blue Tent/ }).click();
    await page.getByRole("button", { name: "Pick Team Two" }).click();
    await page.getByRole("list", { name: "Teams" }).getByRole("button", { name: /Lil Fridge/ }).click();
    const pick = async (side: string) => {
      await page.getByRole("button", { name: `Add a player ${side} gets` }).click();
      const player = page.getByRole("dialog").last().getByRole("checkbox").first();
      const name = (await player.innerText()).split("\n")[0];
      await player.click();
      await page.getByRole("button", { name: "Done" }).click();
      await page.waitForTimeout(500);
      return name;
    };
    const gets = [await pick("Your Team"), await pick("Team Two")];
    log("AT-54", `1280 px, light. /analyze/: Your Team The Blue Tent (1) gets ${gets[0]} from Lil Fridge. Team Two Lil Fridge (3) gets ${gets[1]} from The Blue Tent. The grade is a real call of the local API, with real Sleeper data and a real Claude call.`);
    const started = Date.now();
    await page.getByRole("button", { name: "Grade the Trade" }).click();
    const word = page.locator('[data-stable-id="verdict-word"]');
    await word.waitFor({ timeout: 240000 });
    await page.getByRole("link", { name: /^Egg board/ }).first().waitFor({ timeout: 30000 });
    await word.scrollIntoViewIfNeeded();
    await page.waitForTimeout(1500);
    const marks = await page.evaluate(() => ({ key: document.querySelector("[data-trade-key]")?.getAttribute("data-trade-key"), answer: document.querySelector("[data-trade-answer]")?.getAttribute("data-trade-answer") }));
    log("AT-54", `The grade took ${Math.round((Date.now() - started) / 1000)} s. The verdict word reads "${await word.innerText()}". The marks of the result: data-trade-key "${marks.key}", data-trade-answer "${marks.answer}".`);
    await installEventLog(page);
    const before = checks.length;
    for (let i = 0; i < 2; i += 1) {
      await tapAt(page, '[data-stable-id="verdict-word"]');
      if (i < 1) await page.waitForTimeout(150);
    }
    await page.waitForTimeout(2000);
    log("AT-54", `A double-tap on [data-stable-id="verdict-word"]. The pointerups: ${(await events(page)).filter((line) => line.includes("pointerup")).join("; ")}.`);
    log("AT-54", `Checks sent by the double-tap: ${checks.length - before}`);
    checks.slice(before).forEach((body) => log("AT-54", `body: ${body}`));
    const dialog = page.getByRole("dialog");
    log("AT-54", `The dialog after the answer: ${(await dialog.count()) ? (await dialog.first().innerText()).replace(/\n+/g, " | ") : "none"}`);
    await shot(page, "AT-54", "find", 1280, "light");
    await close();
  }
  execFileSync("bash", [join(TOOLS, "stop-api.sh")], { env: { ...process.env }, stdio: "pipe" });
});
