/**
 * The reduced-motion samples of AT-61 on the cpc export of the Spec head: at 390x660 in WebKit, in both themes, it reads the
 * odds, the rows, and the aria-pressed value of the What-if chip at 0, 1, 3, and 5 s after the sheet shows, with a shot each.
 */
import { createRequire } from "node:module";
import { appendFileSync, writeFileSync } from "node:fs";

const require = createRequire("/private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/7169efb8-161d-49b8-b8f0-64097daad76e/scratchpad/season-sim-ev3/apps/site/package.json");
const { webkit, devices } = require("@playwright/test");

const BASE = "http://127.0.0.1:4173";
const DIR = "/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/season-sim/.scratch/season-sim/evidence/AT-61";
const OUT = `${DIR}/samples.txt`;
const TIMES = [0, 1000, 3000, 5000];
const log = (line) => { console.log(line); appendFileSync(OUT, line + "\n"); };

writeFileSync(OUT, `# $ node at61.mjs   (WebKit, iPhone 15 at 390x660, reducedMotion "reduce", cpc export of 49404be3 on ${BASE}, Your team 6)\n`);
const browser = await webkit.launch();
for (const theme of ["light", "dark"]) {
  const ctx = await browser.newContext({ ...devices["iPhone 15"], viewport: { width: 390, height: 660 }, reducedMotion: "reduce" });
  await ctx.addInitScript(({ theme }) => {
    if (sessionStorage.getItem("check-init")) return;
    sessionStorage.setItem("check-init", "1");
    localStorage.setItem("cpc.your-team", "6");
    localStorage.setItem("cpc.theme", theme);
  }, { theme });
  const page = await ctx.newPage();
  await page.goto(`${BASE}/`, { waitUntil: "networkidle" });
  const reduce = await page.evaluate(() => matchMedia("(prefers-reduced-motion: reduce)").matches);
  const dialog = page.getByRole("dialog", { name: "See your path to the playoffs" });
  await dialog.waitFor({ state: "visible", timeout: 15000 });
  const t0 = Date.now();
  log(`${theme}: prefers-reduced-motion reduce matches: ${reduce}; the sheet shows; t = 0 from here`);
  for (const at of TIMES) {
    const wait = at - (Date.now() - t0);
    if (wait > 0) await page.waitForTimeout(wait);
    const s = await page.evaluate(() => {
      const d = document.querySelector('[role="dialog"]');
      const chip = [...d.querySelectorAll("button")].find((b) => /^What-if:/.test(b.textContent.trim()));
      const status = d.querySelector('[role="status"]')?.textContent;
      // The big number of Your team: the aria-hidden line in the header that ends with %.
      const shown = (el) => { let o = 1; for (let e = el; e; e = e.parentElement) o *= Number(getComputedStyle(e).opacity); return o; };
      const rows = [...d.querySelectorAll("ol > li")].map((li) => `${li.textContent.replace(/\s+/g, " ").trim()} [opacity ${shown(li).toFixed(2)}]`);
      const bigEl = [...d.querySelectorAll("span[aria-hidden]")].find((e) => /\d+%$/.test(e.textContent.trim()));
      // Each text node of that line with the opacity it shows at, so a part at opacity 0 reads as not shown.
      const parts = [];
      const w = document.createTreeWalker(bigEl, NodeFilter.SHOW_TEXT);
      for (let n = w.nextNode(); n; n = w.nextNode()) if (n.textContent.trim()) parts.push(`"${n.textContent.trim()}" opacity ${shown(n.parentElement).toFixed(2)}`);
      const big = parts.join(", ");
      return { pressed: chip?.getAttribute("aria-pressed"), chip: chip?.textContent.trim(), status, big, rows };
    });
    const t = ((Date.now() - t0) / 1000).toFixed(2);
    const shot = `sample-${at / 1000}s-390x660-${theme}.png`;
    await page.screenshot({ path: `${DIR}/${shot}` });
    log(`  t=${t}s  chip aria-pressed=${s.pressed}  chip text "${s.chip}"  odds line: ${s.big}  status "${s.status}"  shot ${shot}`);
    log(`    rows (${s.rows.length}): ${s.rows.join(" | ")}`);
  }
  await ctx.close();
}
await browser.close();
