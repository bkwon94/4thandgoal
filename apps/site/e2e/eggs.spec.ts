/**
 * The end-to-end run of the egg hunt: it builds the CPC site against the local API, drops one test egg, then finds it,
 * cracks it, tears the stub of the claim ticket, and sees the claim on the egg board. Run the API first with
 * make -C apps/api api-evidence. The floor of the find card, the claim sheet, and the egg board runs here too,
 * because the three parts show only with the API.
 */
import { expect, test, type Page } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { join } from "node:path";
import { buildEnv, EVIDENCE_PORT, LOCAL_API } from "./evidence";
import { openPage, scanAxe, scanScroll, scanTargets, scanText } from "./floor";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");
// The test passphrase and the test commissioner key of make -C apps/api api-evidence.
const PASSPHRASE = "localtest";
const COMMISSIONER_KEY = "localkey";
// The test egg T1 of the acceptance tests: a double-tap on the Luck cell of Lil Fridge, roster 3, in the light theme.
const T1 = { page: "/midseason/2026/", target: "luck-3", action: "tap2", conditions: { theme: "light" } };
// The egg words of the hunt, in the order of the values file. The claim goes into the first word that holds the letter.
const EGG_WORDS = ["CORNERSTONE", "LANSDALE", "EAGLES"];
const WIDTHS = [375, 1280];
// The phone width of the readability floor.
const FLOOR_PHONE = { width: 390, height: 844 };
// The port of the served export. The API answers only the origins it allows, so EGGS_PORT moves the run off
// EVIDENCE_PORT only together with CORNERSTONE_ALLOWED_ORIGINS of the API.
const PORT = Number(process.env.EGGS_PORT ?? EVIDENCE_PORT);

let server: { url: string; close: () => Promise<void> };
// The letter that the letter rule gives to T1, and the egg word that holds it. Both come from the answer of the drop.
let letter: string;
let word: string;

test.beforeAll(async () => {
  test.setTimeout(600_000);
  execFileSync("pnpm", ["build"], { env: buildEnv("cpc"), encoding: "utf8", stdio: "pipe" });
  server = await serveDir(OUT, PORT);
  const drop = await fetch(`${LOCAL_API}/clients/cpc/eggs/drop`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Commissioner-Key": COMMISSIONER_KEY },
    body: JSON.stringify({ week: 9, eggs: [T1] }),
  });
  expect(drop.status).toBe(200);
  letter = (await dropAnswer()).eggs[0].letter;
  word = EGG_WORDS.find((each) => each.includes(letter)) ?? "";
  expect(word).not.toBe("");
});

// Each test claims the test egg, so the API undoes the claim after each one, also after a failure.
test.afterEach(async () => {
  await undoClaim();
});

test.afterAll(async () => {
  await server?.close();
});

/*
 * The path of a manager runs with motion on, so the crack plays from the tap point and the stub tears by a drag.
 * The floor below runs with reduced motion, as the floor project does, so each part is at rest when axe reads it.
 */
test.describe("with motion", () => {
  test.use({ reducedMotion: "no-preference" });

  for (const width of WIDTHS) {
    test(`a manager finds the test egg, cracks it, tears the stub, and sees the claim on the egg board at ${width} px`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      await openPage(page, `${server.url}${T1.page}`, "light");
      await findEgg(page);
      await page.screenshot({ path: `test-results/eggs/egg-${width}.png` });
      // A tap off the middle of the egg, so the crack starts at a point of its own.
      const egg = page.getByRole("button", { name: "Crack the egg" });
      const box = (await egg.boundingBox())!;
      await egg.click({ position: { x: box.width * 0.35, y: box.height * 0.4 } });
      await expect(page.getByTestId("egg-letter")).toHaveText(letter);
      await page.getByRole("button", { name: `Claim ${letter}` }).click();
      await page.screenshot({ path: `test-results/eggs/find-${width}.png` });
      await fillSheet(page);
      await page.screenshot({ path: `test-results/eggs/sheet-${width}.png` });
      await tearStub(page);
      await expect(page.getByRole("dialog", { name: `${letter} goes to ${word}.` })).toBeVisible();
      await page.getByRole("link", { name: "See the egg board" }).click();
      await expect(page).toHaveURL(/\/eggs\/$/);
      await page.getByRole("tab", { name: new RegExp(word) }).click();
      const slide = page.getByRole("tabpanel", { name: new RegExp(word) });
      await expect(slide.getByRole("listitem").filter({ hasText: "Lil Fridge" })).toContainText(letter);
      await expect(page.getByRole("region", { name: "Latest claims" })).toContainText(new RegExp(`Lil Fridge claimed an? ${letter} for ${word}\\.`));
      await expectNoHint(page, `${width} px`);
      await page.screenshot({ path: `test-results/eggs/board-${width}.png`, fullPage: true });
      await expectOneFound();
    });
  }
});

/*
 * The readability floor of the three parts at 390px: the find card before and after the crack, the claim sheet with
 * each step filled, and the egg board on each slide of the slider in both themes. Axe runs each WCAG A and AA rule,
 * and the log prints the count of violations and the count of incomplete items apart. Both must be 0.
 */
test("floor: the find card, the claim sheet, and the egg board at 390px", async ({ page }) => {
  await page.setViewportSize(FLOOR_PHONE);
  await openPage(page, `${server.url}${T1.page}`, "light");
  await findEgg(page);
  const failures = await partFloor(page, "find card, egg", '[aria-labelledby="egg-find-title"]');
  await page.getByRole("button", { name: "Crack the egg" }).click();
  await expect(page.getByTestId("egg-letter")).toHaveText(letter);
  failures.push(...(await partFloor(page, "find card, letter", '[aria-labelledby="egg-find-title"]')));
  await page.getByRole("button", { name: `Claim ${letter}` }).click();
  await expect(page.getByRole("dialog", { name: `Put ${letter} in an egg word.` })).toBeVisible();
  failures.push(...(await partFloor(page, "claim sheet, empty", '[aria-labelledby="egg-claim-title"]')));
  await fillSheet(page);
  failures.push(...(await partFloor(page, "claim sheet, filled", '[aria-labelledby="egg-claim-title"]')));
  await tearStub(page);
  await expect(page.getByRole("dialog", { name: `${letter} goes to ${word}.` })).toBeVisible();
  for (const theme of ["light", "dark"] as const) {
    await openPage(page, `${server.url}/eggs/`, theme);
    const tabs = page.getByRole("tab");
    await expect(tabs).toHaveCount(EGG_WORDS.length);
    for (const each of EGG_WORDS) {
      await page.getByRole("tab", { name: new RegExp(each) }).click();
      await expect(page.getByRole("tab", { name: new RegExp(each) })).toHaveAttribute("aria-selected", "true");
      failures.push(...(await partFloor(page, `egg board, ${each}, ${theme}`)));
    }
  }
  expect(failures, "a part of the egg hunt breaks the readability floor").toEqual([]);
  await expectOneFound();
});

/* Double-taps the Luck cell of Lil Fridge, the target of T1, and waits for the find card. */
async function findEgg(page: Page) {
  const cell = page.locator(`[data-stable-id="${T1.target}"]`);
  await cell.scrollIntoViewIfNeeded();
  await cell.click({ clickCount: 2 });
  await expect(page.getByRole("heading", { name: "You found an egg" })).toBeVisible();
}

/* Fills the three steps of the claim sheet: the team, the egg word, and the passphrase. */
async function fillSheet(page: Page) {
  await page.getByRole("group", { name: "Your team" }).getByRole("button", { name: "Lil Fridge" }).click();
  // The name of the card of an egg word starts with the word, then the gift card, the count, and the note.
  await page.getByRole("button", { name: new RegExp(`^${word} `) }).click();
  await page.getByLabel("League passphrase").fill(PASSPHRASE);
}

/*
 * Tears the stub with a drag to the right, as a finger does. The drag runs past the tear length of the ticket in small
 * steps, and the capture of the stub keeps each move on it.
 */
async function tearStub(page: Page) {
  const stub = page.getByRole("group", { name: "Claim ticket" }).getByRole("button", { name: `Tear to claim ${letter} for ${word}` });
  await stub.scrollIntoViewIfNeeded();
  const box = (await stub.boundingBox())!;
  const x = box.x + 4;
  const y = box.y + box.height / 2;
  await page.mouse.move(x, y);
  await page.mouse.down();
  await page.mouse.move(x + 130, y, { steps: 13 });
  await page.mouse.up();
}

/*
 * The page script of AT-32: it searches the HTML of the egg board for each page and each target of the test egg,
 * and prints the count of matches. A board that names one gives a hint to the egg spot.
 */
async function expectNoHint(page: Page, label: string) {
  const html = await page.content();
  // The API names the page with no slash at the end, so the search holds both spellings.
  const names = [T1.page, T1.page.replace(/\/$/, ""), T1.target];
  const matches = names.filter((name) => html.includes(name));
  console.log(`egg board ${label}: ${matches.length} matches of ${names.join(", ")}`);
  expect(matches).toEqual([]);
}

/*
 * The floor of one part: text, tap targets, sideways scroll, and the full axe scan. The scope names the open dialog,
 * which covers the page under it. With no scope the scan reads the whole page.
 */
async function partFloor(page: Page, label: string, scope?: string): Promise<string[]> {
  const text = await scanText(page);
  const targets = await scanTargets(page);
  const scroll = await scanScroll(page);
  const axe = await scanAxe(page, scope);
  console.log(`${label}: axe violations ${axe.violations.length}, axe incomplete ${axe.incomplete.length}`);
  console.log(`${label}: tap targets under 44px ${targets.failures.length}, sideways scroll ${scroll.length}, small text ${text.failures.length}`);
  return [...axe.violations, ...axe.incomplete, ...targets.failures, ...scroll, ...text.failures].map((line) => `${label}: ${line}`);
}

/* The claim of the test reached the API: the board counts the one test egg as found. */
async function expectOneFound() {
  const board = await (await fetch(`${LOCAL_API}/clients/cpc/eggs/board`)).json();
  expect(board.counts.found).toBe(1);
}

/* Undoes the claim of the test egg, when a test claimed it, so the next test finds it again. */
async function undoClaim() {
  const board = await (await fetch(`${LOCAL_API}/clients/cpc/eggs/board`)).json();
  if (board.counts.found === 0) return;
  await fetch(`${LOCAL_API}/clients/cpc/eggs/undo`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Commissioner-Key": COMMISSIONER_KEY },
    body: JSON.stringify({ egg_id: (await dropAnswer()).eggs[0].id }),
  });
}

/* The answer of a second drop of week 9, which adds nothing and names the egg that dropped. */
async function dropAnswer(): Promise<{ eggs: { id: number; letter: string }[] }> {
  const response = await fetch(`${LOCAL_API}/clients/cpc/eggs/drop`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Commissioner-Key": COMMISSIONER_KEY },
    body: JSON.stringify({ week: 9, eggs: [T1] }),
  });
  return response.json();
}
