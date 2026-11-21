/**
 * The rendered-text search of AT-30: it opens Find mode as Bo Girds on the local site, reads the page text before and
 * after a press with Skattebo and Flowers on the block, and prints each match of "anchor".
 */
import { createRequire } from "node:module";
const require = createRequire("/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/trade-block/apps/site/package.json");
const { chromium } = require("@playwright/test");
const SITE = "http://127.0.0.1:18432";
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
const scan = async (when) => {
  const text = await p.evaluate(() => document.body.innerText);
  const labels = await p.evaluate(() => [...document.querySelectorAll("[aria-label],[title],[placeholder],[alt]")].map((el) => ["aria-label", "title", "placeholder", "alt"].map((a) => el.getAttribute(a) ?? "").join(" ")).join("\n"));
  const hits = (text + "\n" + labels).split("\n").filter((line) => /anchor/i.test(line));
  console.log(`${when}: ${text.length} characters of page text and ${labels.split("\n").length} label lines; lines with "anchor": ${hits.length ? hits.join(" | ") : "none"}`);
};
await p.goto(`${SITE}/analyze/`);
await p.locator("input[type=password]").fill("localtest");
await p.locator("button[type=submit]").click();
await p.locator('[role=radiogroup][aria-label="Mode"] button:text-is("Find a trade")').waitFor();
await p.waitForTimeout(800);
await p.locator('[role=radiogroup][aria-label="Mode"] button:text-is("Find a trade")').click();
await p.locator('section[aria-label="Trade Ideas"] button:has-text("Pick a team")').click();
await p.locator('ul[aria-label="Teams"] button:has-text("Bo Girds")').waitFor();
await p.waitForTimeout(1000);
await p.locator('ul[aria-label="Teams"] button:has-text("Bo Girds")').click();
await p.waitForTimeout(1000);
await p.locator('[role="group"][aria-label="Trade block"] button[aria-label="Cam Skattebo, RB"]').click();
await p.locator('[role="group"][aria-label="Trade block"] button[aria-label="Zay Flowers, WR"]').click();
await scan("Find mode with Skattebo and Flowers on the block");
await p.locator('button:text-is("Find a Trade")').click();
await p.waitForTimeout(2000);
await p.locator('button:text-is("Find a Trade")').waitFor({ timeout: 300000 });
await p.waitForTimeout(3000);
await scan("after the press, with the cards");
await b.close();
