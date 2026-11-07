/**
 * The end-to-end run of the egg hunt: it builds the CPC site against the local API, drops one test egg, then finds it,
 * claims it, and sees the claim on the egg board. Run the API first with make -C apps/api api-evidence.
 */
import { expect, test } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { join } from "node:path";
import { buildEnv, EVIDENCE_PORT, LOCAL_API } from "./evidence";
import { serveDir } from "./serve";

const OUT = join(process.cwd(), "out");
// The test passphrase and the test commissioner key of make -C apps/api api-evidence.
const PASSPHRASE = "localtest";
const COMMISSIONER_KEY = "localkey";
// The test egg T1 of the acceptance tests: a 3-tap on the Luck cell of Lil Fridge, roster 3, in the light theme.
const T1 = { page: "/midseason/2026/", target: "luck-3", action: "tap3", conditions: { theme: "light" }, letter: "C" };
const WIDTHS = [375, 1280];
// The port of the served export. The API answers only the origins it allows, so EGGS_PORT moves the run off
// EVIDENCE_PORT only together with CORNERSTONE_ALLOWED_ORIGINS of the API.
const PORT = Number(process.env.EGGS_PORT ?? EVIDENCE_PORT);

let server: { url: string; close: () => Promise<void> };

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
});

test.afterAll(async () => {
  await server?.close();
});

for (const width of WIDTHS) {
  test(`a manager finds the test egg, claims C, and sees the claim on the egg board at ${width} px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 900 });
    // The light theme is a condition of the test egg, so the browser stores the light choice before the first paint.
    await page.addInitScript(() => localStorage.setItem("cpc.theme", "light"));
    await page.goto(`${server.url}/midseason/2026/`);
    const cell = page.locator('[data-stable-id="luck-3"]');
    await cell.scrollIntoViewIfNeeded();
    await cell.click({ clickCount: 3 });
    await expect(page.getByRole("heading", { name: "You found an egg" })).toBeVisible();
    await page.screenshot({ path: `test-results/eggs/egg-${width}.png` });
    await page.getByRole("button", { name: "Crack the egg" }).click();
    await expect(page.getByTestId("egg-letter")).toHaveText("C");
    await page.getByRole("button", { name: "Claim C" }).click();
    await page.screenshot({ path: `test-results/eggs/find-${width}.png` });
    await page.getByRole("group", { name: "Your team" }).getByRole("button", { name: "Lil Fridge" }).click();
    await page.getByRole("button", { name: "CORNERSTONE", exact: true }).click();
    await page.getByLabel("Passphrase").fill(PASSPHRASE);
    await page.screenshot({ path: `test-results/eggs/sheet-${width}.png` });
    await page.getByRole("button", { name: "Claim C for CORNERSTONE" }).click();
    await expect(page.getByRole("dialog", { name: "C goes to CORNERSTONE." })).toBeVisible();
    await page.getByRole("link", { name: "See the egg board" }).click();
    await expect(page).toHaveURL(/\/eggs\/$/);
    const cornerstone = page.getByRole("region", { name: /CORNERSTONE/ });
    await expect(cornerstone.getByRole("listitem").filter({ hasText: "Lil Fridge" })).toContainText("C");
    await expect(page.getByRole("region", { name: "Latest claims" })).toContainText("Lil Fridge · C · CORNERSTONE");
    await page.screenshot({ path: `test-results/eggs/board-${width}.png`, fullPage: true });
    // The claim of the first width takes the egg, so the API undoes it for the next width.
    const board = await (await fetch(`${LOCAL_API}/clients/cpc/eggs/board`)).json();
    expect(board.counts.found).toBe(1);
    await fetch(`${LOCAL_API}/clients/cpc/eggs/undo`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Commissioner-Key": COMMISSIONER_KEY },
      body: JSON.stringify({ egg_id: (await dropAnswer()).eggs[0].id }),
    });
  });
}

/* The answer of a second drop of week 9, which adds nothing and names the egg that dropped. */
async function dropAnswer(): Promise<{ eggs: { id: number }[] }> {
  const response = await fetch(`${LOCAL_API}/clients/cpc/eggs/drop`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Commissioner-Key": COMMISSIONER_KEY },
    body: JSON.stringify({ week: 9, eggs: [T1] }),
  });
  return response.json();
}
