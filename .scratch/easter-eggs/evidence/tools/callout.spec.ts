/**
 * AT-31 of easter-eggs: the -webkit-touch-callout of a Luck cell, a link, and an image on the built midseason page.
 * Only iOS Safari computes the property, so the spec reads the rules of the built CSS that set it and matches each one.
 */
import { test, webkit } from "../../../../apps/site/node_modules/@playwright/test/index.js";
import { writeFileSync } from "node:fs";
import { join } from "node:path";

test("the callout of each element", async () => {
  const browser = await webkit.launch();
  const page = await browser.newPage({ viewport: { width: 375, height: 900 } });
  await page.goto("http://127.0.0.1:4174/midseason/2026/");
  const lines = await page.evaluate(async () => {
    // Each rule of the built CSS that sets the callout, with its selector list.
    const sheets = [...document.querySelectorAll('link[rel="stylesheet"]')].map((link) => (link as HTMLLinkElement).href);
    const rules: { selector: string; value: string }[] = [];
    for (const href of sheets) {
      const text = await (await fetch(href)).text();
      for (const match of text.matchAll(/([^{}]+)\{([^{}]*-webkit-touch-callout:\s*([a-z]+)[^{}]*)\}/g)) {
        rules.push({ selector: match[1].trim(), value: match[3] });
      }
    }
    // The specificity of one selector: ids, then attributes and classes, then element names.
    const weight = (selector: string) => {
      const ids = (selector.match(/#[\w-]+/g) ?? []).length;
      const attrs = (selector.match(/\[[^\]]+\]|\.[\w-]+|:(?!:)[\w-]+/g) ?? []).length;
      const tags = (selector.replace(/\[[^\]]+\]/g, "").match(/(^|[\s>+~])[a-z][\w-]*/g) ?? []).length;
      return ids * 10000 + attrs * 100 + tags;
    };
    const callout = (element: Element | null) => {
      if (!element) return "no element";
      const hits: { selector: string; value: string; weight: number; order: number }[] = [];
      rules.forEach((rule, order) => {
        for (const one of rule.selector.split(",").map((part) => part.trim())) {
          if (element.matches(one)) hits.push({ selector: one, value: rule.value, weight: weight(one), order });
        }
      });
      if (hits.length === 0) return "no rule matches, so the browser default holds (the callout is on)";
      const win = [...hits].sort((a, b) => a.weight - b.weight || a.order - b.order).at(-1)!;
      return `${win.value} (the winning rule "${win.selector}"; matched rules: ${hits.map((hit) => `"${hit.selector}" -> ${hit.value}`).join("; ")})`;
    };
    const items: [string, Element | null][] = [
      ['[data-stable-id="luck-3"], the Luck cell of Lil Fridge', document.querySelector('[data-stable-id="luck-3"]')],
      ["a link inside an element with a stable id", document.querySelector("main [data-stable-id] a[href]")],
      ["the first link of the page, main a[href]", document.querySelector("main a[href]")],
      ["an image inside an element with a stable id", document.querySelector("main [data-stable-id] img")],
      ["the first image of the page, main img", document.querySelector("main img")],
    ];
    return [
      `data-eggs on the root element: ${document.documentElement.hasAttribute("data-eggs")}`,
      `The rules of the built CSS that set -webkit-touch-callout: ${rules.map((rule) => `"${rule.selector}" -> ${rule.value}`).join(" | ")}`,
      `The computed value in this WebKit: "${getComputedStyle(document.querySelector('[data-stable-id="luck-3"]')!).getPropertyValue("-webkit-touch-callout")}" (desktop WebKit does not compute the property; iOS Safari does)`,
      ...items.map(([name, element]) => `${name}: ${callout(element)}`),
    ];
  });
  writeFileSync(join(__dirname, "..", "AT-31", "output.txt"), [`WebKit ${browser.version()}, http://127.0.0.1:4174/midseason/2026/ at 375 px:`, ...lines].join("\n") + "\n");
  await browser.close();
});
