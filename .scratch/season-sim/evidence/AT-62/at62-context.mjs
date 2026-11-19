/**
 * The context check of AT-62: for each hit of a banned word in the rendered text of a page, it prints the text around the hit,
 * the section of the page that holds it, and whether the hit sits inside the Sim tile (#sim). Usage: node at62-context.mjs
 */
import { createRequire } from "node:module";
const require = createRequire("/private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/7169efb8-161d-49b8-b8f0-64097daad76e/scratchpad/season-sim-ev3/apps/site/package.json");
const { webkit } = require("@playwright/test");

const WORDS = ["rival", "brian", "jev", "advisor", "finder", "front door"];
const SITES = { cpc: "http://127.0.0.1:4173", norcal: "http://127.0.0.1:4174" };
const ROUTES = ["/sim/2026/", "/2026/week-10/", "/"];

const browser = await webkit.launch();
for (const [slug, base] of Object.entries(SITES)) {
  for (const route of ROUTES) {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 660 } });
    await ctx.addInitScript(() => {
      if (sessionStorage.getItem("ev-init")) return;
      sessionStorage.setItem("ev-init", "1");
      localStorage.setItem("cpc.passphrase", "localtest");
      localStorage.setItem("cpc.your-team", "6");
    });
    const page = await ctx.newPage();
    await page.goto(base + route, { waitUntil: "networkidle" });
    await page.waitForTimeout(1500);
    const result = await page.evaluate((words) => {
      const hits = [];
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      const hasSim = !!document.querySelector("#sim");
      for (let node = walker.nextNode(); node; node = walker.nextNode()) {
        const text = node.textContent || "";
        for (const word of words) {
          const re = new RegExp(`\\b${word}\\b`, "gi");
          for (let m = re.exec(text); m; m = re.exec(text)) {
            const el = node.parentElement;
            const block = el.closest("li, p, div") || el;
            const section = el.closest("section[id]");
            const heading = section?.querySelector("h1, h2, h3");
            hits.push({
              word,
              match: m[0],
              around: (block.textContent || "").replace(/\s+/g, " ").trim().slice(0, 200),
              window: text.slice(Math.max(0, m.index - 100), m.index + 100).replace(/\s+/g, " "),
              tag: el.tagName,
              section: section ? `section#${section.id}` : "no section with an id",
              heading: heading ? heading.textContent.trim() : "none",
              inSim: !!el.closest("#sim"),
            });
          }
        }
      }
      const order = [...document.querySelectorAll("section[id]")].map((s) => s.id);
      return { hits, hasSim, order };
    }, WORDS);
    console.log(`${slug} ${route}: ${result.hits.length} hits; #sim on page: ${result.hasSim}; sections in order: ${result.order.join(" > ") || "none"}`);
    for (const h of result.hits) {
      console.log(`  hit "${h.match}" (word ${h.word}) in ${h.tag}, ${h.section}, heading "${h.heading}", inside #sim: ${h.inSim}`);
      if (h.tag === "SCRIPT") console.log(`    script text, 100 chars each side: ${h.window}`);
      else console.log(`    text around: "${h.around}"`);
    }
    await ctx.close();
  }
}
await browser.close();
