// The banned-word check of AT-62: the rendered text of the sim page, its replay, the Sim tile, and the Announcement.
import { webkit } from "/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/season-sim/apps/site/node_modules/@playwright/test/index.mjs";
const WORDS = ["rival", "brian", "jev", "advisor", "finder", "front door"];
const [slug, base] = [process.argv[2], process.argv[3]];
const browser = await webkit.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 660 } });
await ctx.addInitScript(() => { localStorage.setItem("cpc.passphrase", "x"); localStorage.setItem("cpc.your-team", "6"); });
const page = await ctx.newPage();
const parts = {};
await page.goto(`${base}/sim/2026/`, { waitUntil: "networkidle" });
parts["sim page"] = await page.locator("main").innerText();
const btn = page.getByRole("button", { name: /Sim the season/ });
if (await btn.count()) { await btn.first().click(); await page.waitForTimeout(4000); parts["replay"] = await page.locator("body").innerText(); }
await page.goto(`${base}/2026/week-10/`, { waitUntil: "networkidle" });
parts["sim tile"] = await page.locator("#sim").innerText().catch(() => "MISSING");
await page.goto(`${base}/`, { waitUntil: "networkidle" });
await page.waitForTimeout(2000);
const sheet = page.locator('[aria-modal="true"]');
parts["announcement"] = (await sheet.count()) ? await sheet.first().innerText() : "MISSING";
for (const [name, text] of Object.entries(parts)) {
  const hits = WORDS.filter((w) => new RegExp(`\\b${w}\\b`, "i").test(text));
  console.log(`${slug} ${name}: ${text.length} chars, hits ${hits.length ? hits.join(",") : "none"}`);
  console.log(`  text: ${text.replace(/\s+/g, " ").slice(0, 160)}`);
}
await browser.close();
