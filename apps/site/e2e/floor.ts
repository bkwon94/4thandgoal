/**
 * The scans of the readability floor: text size, tap targets, sideways scroll, words split over two lines, and contrast with axe.
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
type InPage = { scan: "text" | "targets" | "scroll" | "words"; limits: typeof LIMITS };

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

  if (scan === "words") {
    // A word may wrap to the next line whole, but never split inside itself, such as "UNDERPERF" over "ORMER".
    // A range over one word gives one box per line it sits on, so two distinct tops mean a split word.
    // A hyphen ends a word, because a wrap after the hyphen of "5-game" is a normal break.
    const failures: string[] = [];
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      const el = node.parentElement;
      const text = node.textContent ?? "";
      if (!el || !text.trim() || !visible(el)) continue;
      for (const match of text.matchAll(/[^\s-]+-*/g)) {
        const range = document.createRange();
        range.setStart(node, match.index);
        range.setEnd(node, match.index + match[0].length);
        const tops = [...range.getClientRects()].filter((box) => box.width > 0).map((box) => Math.round(box.top));
        const lines = new Set(tops).size;
        if (lines > 1) failures.push(`${describe(el)}: the word "${match[0]}" breaks over ${lines} lines`);
      }
    }
    return failures;
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

/* Fails for each word that the layout splits over two lines or more. A wrap between words passes. */
export async function scanWords(page: Page): Promise<string[]> {
  return (await page.evaluate<unknown, InPage>(inPage, { scan: "words", limits: LIMITS })) as string[];
}

/*
 * Runs axe with the one rule color-contrast, at the WCAG AA split of 4.5 to 1 and 3 to 1 for large text.
 * An incomplete result fails too: axe gives no verdict on text over an image, a gradient, alpha, or an overlap,
 * and a check that read only the violations would pass that text with no test.
 * A scope, a CSS selector, limits the scan to one part of the page, such as an open strip that covers the page under it.
 */
export async function scanContrast(page: Page, scope?: string): Promise<string[]> {
  const builder = new AxeBuilder({ page }).withRules(["color-contrast"]);
  const result = await (scope === undefined ? builder : builder.include(scope)).analyze();
  const lines = (kind: string, items: typeof result.violations) =>
    items.flatMap((rule) =>
      rule.nodes.map((node) => `${kind}: ${node.target.join(" ")} ${node.failureSummary ?? rule.help}`.replace(/\s+/g, " ")),
    );
  return [...lines("violation", result.violations), ...lines("incomplete", result.incomplete)];
}

/*
 * The contrast scan of a page with a list that scrolls inside a box, such as the team list of the sheet of Your team.
 * Axe cannot judge a row that the box clips, and it reports the row as incomplete. An incomplete item fails the floor,
 * so the list scrolls in steps and the page is scanned at each step. A row passes when it sits in full view at one step
 * and axe reports nothing for it at that step. A violation of a row fails at any step. An incomplete item of a row fails
 * when no step clears the row. A line of any other part of the page fails as it does in a plain scan.
 * A page with no such list gets one plain scan.
 */
export async function scanContrastInSteps(page: Page, scope?: string): Promise<string[]> {
  const listSelector = '[role="dialog"] ul';
  const metrics = await page.evaluate(
    ([selector]) => {
      const list = document.querySelector(selector);
      return list ? { overflow: list.scrollHeight > list.clientHeight, height: list.clientHeight, max: list.scrollHeight - list.clientHeight, rows: list.children.length } : null;
    },
    [listSelector],
  );
  if (metrics === null || !metrics.overflow) return scanContrast(page, scope);

  const failures = new Set<string>();
  const incomplete = new Map<number, string[]>();
  const cleared = new Set<number>();
  // Half a box per step, so a row that sits at the edge of one step sits in full view at the next.
  const step = Math.max(1, Math.floor(metrics.height / 2));
  for (let top = 0; ; top = Math.min(top + step, metrics.max)) {
    const inView = await page.evaluate(
      ([selector, scrollTop]) => {
        const list = document.querySelector(selector) as HTMLElement;
        list.scrollTop = scrollTop;
        const box = list.getBoundingClientRect();
        return ([...list.children] as HTMLElement[]).flatMap((row, index) => {
          const rect = row.getBoundingClientRect();
          return rect.top >= box.top && rect.bottom <= box.bottom ? [index + 1] : [];
        });
      },
      [listSelector, top] as const,
    );
    const reported = new Set<number>();
    for (const line of await scanContrast(page, scope)) {
      const row = /^(violation|incomplete): li:nth-child\((\d+)\) > /.exec(line);
      if (row === null || row[1] === "violation") failures.add(line);
      if (row === null) continue;
      reported.add(Number(row[2]));
      if (row[1] === "incomplete") incomplete.set(Number(row[2]), [...(incomplete.get(Number(row[2])) ?? []), line]);
    }
    for (const row of inView) if (!reported.has(row)) cleared.add(row);
    if (top >= metrics.max) break;
  }
  await page.evaluate(([selector]) => ((document.querySelector(selector) as HTMLElement).scrollTop = 0), [listSelector]);
  for (const [row, lines] of incomplete) if (!cleared.has(row)) for (const line of lines) failures.add(line);
  for (let row = 1; row <= metrics.rows; row++) if (!cleared.has(row)) failures.add(`row ${row} of the scrolled list was never judged in full view`);
  return [...failures];
}

/* The axe tags of the full scan: each rule of WCAG 2.2 at the levels A and AA. */
const WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];

export type AxeScan = { violations: string[]; incomplete: string[] };

/*
 * Runs each WCAG A and AA rule of axe, and keeps the violations and the incomplete items apart, so a log can print
 * the two counts. An incomplete item fails as a violation does, for the reason of scanContrast. Each line names the rule.
 * A scope, a CSS selector, limits the scan to one part, such as the open claim sheet.
 */
export async function scanAxe(page: Page, scope?: string): Promise<AxeScan> {
  const builder = new AxeBuilder({ page }).withTags(WCAG_TAGS);
  const result = await (scope === undefined ? builder : builder.include(scope)).analyze();
  const lines = (kind: string, items: typeof result.violations) =>
    items.flatMap((rule) =>
      rule.nodes.map((node) => `${kind}: ${node.target.join(" ")} ${rule.id}: ${node.failureSummary ?? rule.help}`.replace(/\s+/g, " ")),
    );
  return { violations: lines("violation", result.violations), incomplete: lines("incomplete", result.incomplete) };
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
