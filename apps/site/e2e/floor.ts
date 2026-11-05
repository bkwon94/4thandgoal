/**
 * The scans of the readability floor: text size, tap targets, sideways scroll, and contrast with axe.
 * Each scan reads one loaded page and returns its failures as lines that name the element and the measure.
 */
import { DARK_CLASS, THEME_KEY, type Theme } from "@cpc/design/lib/theme";
import AxeBuilder from "@axe-core/playwright";
import { expect, type Page } from "@playwright/test";

/* Prose is a <p> or an element with data-prose. Prose is 16px or more, and all other text is 11px or more. */
export const PROSE_SELECTOR = "p, [data-prose]";
export const PROSE_MIN_PX = 16;
export const OTHER_MIN_PX = 11;
/* Each link and button is 44px or more on each side, the WCAG 2.5.5 size. A link inside prose is exempt, as 2.5.5 allows. */
export const TARGET_MIN_PX = 44;
const TARGET_SELECTOR =
  "a[href], button, input:not([type=hidden]), select, textarea, summary, label[for], [role=button], [role=link], [role=tab]";

export type TextScan = { failures: string[]; prose: number; other: number };
export type TargetScan = { failures: string[]; exempt: string[] };

const LIMITS = {
  proseSelector: PROSE_SELECTOR,
  proseMin: PROSE_MIN_PX,
  otherMin: OTHER_MIN_PX,
  targetSelector: TARGET_SELECTOR,
  targetMin: TARGET_MIN_PX,
};

/*
 * The one function that runs in the page. Playwright sends it to the browser as source, so it cannot call a helper
 * outside itself. It holds all the scans, and each one shares the same label of an element.
 */
type InPage = { scan: "text" | "targets" | "scroll"; limits: typeof LIMITS };

function inPage({ scan, limits }: InPage): unknown {
  const describe = (el: Element) => {
    const cls = typeof el.className === "string" && el.className.trim() ? `.${el.className.trim().split(/\s+/)[0]}` : "";
    const text = (el.textContent ?? "").trim().replace(/\s+/g, " ").slice(0, 40);
    return `${el.tagName.toLowerCase()}${cls} "${text}"`;
  };
  const visible = (el: Element) => {
    const box = el.getBoundingClientRect();
    return getComputedStyle(el).visibility !== "hidden" && box.width > 0 && box.height > 0;
  };

  if (scan === "scroll") {
    const root = document.documentElement;
    if (root.scrollWidth <= root.clientWidth) return [];
    // Name the element that reaches furthest right. An element inside a box that clips or scrolls on its own is skipped,
    // because that box, not the element, sets the width of the page. A tie goes to the later, deeper element.
    const clipped = (el: Element) => {
      for (let up = el.parentElement; up && up !== document.body; up = up.parentElement) {
        if (getComputedStyle(up).overflowX !== "visible") return true;
      }
      return false;
    };
    let widest: Element | null = null;
    let right = 0;
    for (const el of document.body.querySelectorAll("*")) {
      const edge = el.getBoundingClientRect().right;
      if (edge >= right && !clipped(el)) {
        widest = el;
        right = edge;
      }
    }
    const culprit = widest ? `, widest is ${describe(widest)} at ${Math.round(right)}px` : "";
    return [`the page scrolls sideways: ${root.scrollWidth}px wide in ${root.clientWidth}px${culprit}`];
  }

  if (scan === "targets") {
    const failures: string[] = [];
    const exempt: string[] = [];
    for (const el of document.querySelectorAll(limits.targetSelector)) {
      if (!visible(el)) continue;
      if (el.tagName === "A" && el.closest(limits.proseSelector)) {
        exempt.push(describe(el));
        continue;
      }
      const box = el.getBoundingClientRect();
      if (box.width < limits.targetMin || box.height < limits.targetMin) {
        const size = `${Math.round(box.width)}x${Math.round(box.height)}px`;
        failures.push(`${describe(el)} is ${size}, under the tap floor of ${limits.targetMin}px`);
      }
    }
    return { failures, exempt };
  }

  // The count of each tier counts elements, not text nodes, so a paragraph with a link counts once, and its link once.
  const failures: string[] = [];
  const seen = new Map<Element, boolean>();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    const el = node.parentElement;
    if (!el || seen.has(el) || !node.textContent?.trim() || !visible(el)) continue;
    const prose = el.closest(limits.proseSelector) !== null;
    seen.set(el, prose);
    const size = parseFloat(getComputedStyle(el).fontSize);
    const min = prose ? limits.proseMin : limits.otherMin;
    if (size < min) {
      failures.push(`${describe(el)} is ${size}px, under the ${prose ? "prose" : "other text"} floor of ${min}px`);
    }
  }
  const tiers = [...seen.values()];
  return { failures, prose: tiers.filter(Boolean).length, other: tiers.filter((p) => !p).length };
}

/* Reads the computed font size of each visible text node, as prose or as other text. */
export async function scanText(page: Page): Promise<TextScan> {
  return (await page.evaluate<unknown, InPage>(inPage, { scan: "text", limits: LIMITS })) as TextScan;
}

/* Reads the box of each visible link, button, and form control. */
export async function scanTargets(page: Page): Promise<TargetScan> {
  return (await page.evaluate<unknown, InPage>(inPage, { scan: "targets", limits: LIMITS })) as TargetScan;
}

/* Fails when the page is wider than the viewport, and names the element that reaches furthest right. */
export async function scanScroll(page: Page): Promise<string[]> {
  return (await page.evaluate<unknown, InPage>(inPage, { scan: "scroll", limits: LIMITS })) as string[];
}

/*
 * Runs axe with the one rule color-contrast, at the WCAG AA split of 4.5 to 1 and 3 to 1 for large text.
 * An incomplete result fails too: axe gives no verdict on text over an image, a gradient, alpha, or an overlap,
 * and a check that read only the violations would pass that text with no test.
 */
export async function scanContrast(page: Page): Promise<string[]> {
  const result = await new AxeBuilder({ page }).withRules(["color-contrast"]).analyze();
  const lines = (kind: string, items: typeof result.violations) =>
    items.flatMap((rule) =>
      rule.nodes.map((node) => `${kind}: ${node.target.join(" ")} ${node.failureSummary ?? rule.help}`.replace(/\s+/g, " ")),
    );
  return [...lines("violation", result.violations), ...lines("incomplete", result.incomplete)];
}

/*
 * Opens a page in one theme. The init script stores the choice before any script of the page runs, so the boot script
 * reads it on the first paint, as for a reader. The assert on <html> then fails loud if the key or the boot script
 * changes, so the floor never checks the wrong theme.
 */
export async function openPage(page: Page, url: string, theme: Theme): Promise<void> {
  await page.addInitScript(([key, value]) => localStorage.setItem(key, value), [THEME_KEY, theme] as const);
  await page.goto(url);
  const html = page.locator("html");
  const dark = new RegExp(`(^|\\s)${DARK_CLASS}(\\s|$)`);
  await (theme === "dark" ? expect(html).toHaveClass(dark) : expect(html).not.toHaveClass(dark));
}
