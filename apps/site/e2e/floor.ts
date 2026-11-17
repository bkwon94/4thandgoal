/**
 * The scans of the readability floor: text size, tap targets, sideways scroll, words split over two lines, and contrast with axe and by pixels.
 * Each scan reads one loaded page and returns its failures as lines that name the element and the measure.
 *
 * A hero is a `section` that carries the hero texture. HeroFrame renders a section whose art layer, a direct child
 * with aria-hidden, holds `[data-hero-art="texture"]`. The egg banner is a `section.hero-texture` itself. HERO_SELECTOR
 * names both. A text of a hero is each element of the hero that holds a visible text node of its own, outside an
 * SVG. An aria-hidden text counts, because a sighted reader still reads it. Its box is the box of each line of its text, not the box of the element.
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

/* The two forms of a hero. See the comment at the top of the file. */
export const HERO_SELECTOR = 'section:has(> [aria-hidden="true"] > [data-hero-art="texture"]), section.hero-texture';
/* Every hero text reaches 4.5 to 1, large or not (ADR 0036), so a glow that grows can never pass a title at 3 to 1. */
export const HERO_MIN_RATIO = 4.5;
/* The reasons of an axe incomplete result that the pixel scan of a hero can judge: art under the text, and a text so
   short, such as one digit, that axe does not rate it. axe names them with these message keys. An incomplete result with any other reason, or outside a hero, still fails. */
const PIXEL_REASONS = ["bgImage", "bgGradient", "bgOverlap", "shortTextContent"];

export type TextScan = { failures: string[]; prose: number; other: number };
export type TargetScan = { failures: string[]; exempt: string[] };

const LIMITS = {
  proseSelector: PROSE_SELECTOR,
  proseMin: PROSE_MIN_PX,
  otherMin: OTHER_MIN_PX,
  targetSelector: TARGET_SELECTOR,
  targetMin: TARGET_MIN_PX,
  heroSelector: HERO_SELECTOR,
};

/*
 * The one function that runs in the page. Playwright sends it to the browser as source, so it cannot call a helper
 * outside itself. It holds all the scans, and each one shares the same label of an element.
 */
type InPage = { scan: "text" | "targets" | "scroll" | "words" | "heroes"; limits: typeof LIMITS; scope?: string };

function inPage({ scan, limits, scope }: InPage): unknown {
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

  if (scan === "heroes") {
    // Marks each hero and each of its texts, and reads the color and the line boxes of each text, in page coordinates.
    // A line box is clipped by each box that clips or scrolls above it, so a cut or a screen reader only text, such as
    // a box of 1px, gives no box. A box under 2px on a side is too small to read and is dropped.
    const root = scope === undefined ? document.body : document.querySelector(scope);
    // A hero that the layout hides, such as the stage of the Index list under the desktop tier, is not on the page.
    const heroes = [...document.querySelectorAll(limits.heroSelector)].filter((hero) => root !== null && root.contains(hero) && visible(hero));
    const probe = document.createElement("canvas").getContext("2d")!;
    const rgba = (color: string) => {
      probe.clearRect(0, 0, 1, 1);
      probe.fillStyle = color;
      probe.fillRect(0, 0, 1, 1);
      const [r, g, b, a] = probe.getImageData(0, 0, 1, 1).data;
      return [r, g, b, a / 255];
    };
    return heroes.map((hero, h) => {
      (hero as HTMLElement).dataset.floorHero = String(h);
      const texts = new Map<Element, number[][]>();
      const walker = document.createTreeWalker(hero, NodeFilter.SHOW_TEXT);
      for (let node = walker.nextNode(); node; node = walker.nextNode()) {
        const el = node.parentElement;
        if (!el || !node.textContent?.trim() || el.closest("svg") || !visible(el)) continue;
        const clips: DOMRect[] = [];
        for (let up: Element | null = el; up && up !== hero.parentElement; up = up.parentElement) {
          const style = getComputedStyle(up);
          if (style.overflowX !== "visible" || style.overflowY !== "visible") clips.push(up.getBoundingClientRect());
        }
        const range = document.createRange();
        range.selectNodeContents(node);
        for (const line of range.getClientRects()) {
          let [left, top, right, bottom] = [line.left, line.top, line.right, line.bottom];
          for (const clip of clips) {
            [left, top] = [Math.max(left, clip.left), Math.max(top, clip.top)];
            [right, bottom] = [Math.min(right, clip.right), Math.min(bottom, clip.bottom)];
          }
          if (right - left < 2 || bottom - top < 2) continue;
          texts.set(el, [...(texts.get(el) ?? []), [left + scrollX, top + scrollY, right - left, bottom - top]]);
        }
      }
      const list = [...texts].flatMap(([el, boxes]) => {
        // The opacity of the text and of each box above it fades the text into the pixels under it.
        let opacity = 1;
        for (let up: Element | null = el; up && up !== document.documentElement; up = up.parentElement) opacity *= parseFloat(getComputedStyle(up).opacity);
        if (opacity === 0) return [];
        (el as HTMLElement).dataset.floorText = "";
        const [r, g, b, a] = rgba(getComputedStyle(el).color);
        return [{ label: describe(el), color: [r, g, b, a * opacity], boxes }];
      });
      const name = hero.getAttribute("aria-label") ?? describe(hero);
      return { name, texts: list };
    });
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

type HeroText = { label: string; color: number[]; boxes: number[][] };
type HeroScan = { name: string; texts: HeroText[] };

/*
 * Runs axe with the one rule color-contrast, at the WCAG AA split of 4.5 to 1 and 3 to 1 for large text.
 * An incomplete result fails too: axe gives no verdict on text over an image, a gradient, alpha, or an overlap,
 * and a check that read only the violations would pass that text with no test.
 * The one exception is art under the text of a hero: an incomplete result of a node inside a hero, for a reason of
 * PIXEL_REASONS, passes to scanHeroPixels, which reads the real pixels under the text.
 */
async function axeContrast(page: Page, scope?: string): Promise<string[]> {
  const builder = new AxeBuilder({ page }).withRules(["color-contrast"]);
  const result = await (scope === undefined ? builder : builder.include(scope)).analyze();
  const reason = (node: (typeof result.incomplete)[number]["nodes"][number]) =>
    [...node.any, ...node.all, ...node.none].map((check) => (check.data as { messageKey?: string } | null)?.messageKey).find(Boolean);
  const candidates = result.incomplete.flatMap((rule) => rule.nodes).filter((node) => PIXEL_REASONS.includes(reason(node) ?? ""));
  // A target of one selector names a node of the page itself. A longer target crosses a frame or a shadow root, and no hero sits there.
  // A node in an SVG keeps its line, because the pixel scan does not read that text. An aria-hidden text is read.
  const inHero = await page.evaluate(
    ([targets, selector]) =>
      targets.map((target) => {
        const node = target.length === 1 ? document.querySelector(target[0]) : null;
        return node !== null && node.closest(selector) !== null && node.closest("svg") === null;
      }),
    [candidates.map((node) => node.target.map(String)), HERO_SELECTOR] as const,
  );
  const handed = new Set(candidates.filter((_, i) => inHero[i]));
  const lines = (kind: string, items: typeof result.violations) =>
    items.flatMap((rule) =>
      rule.nodes
        .filter((node) => !handed.has(node))
        .map((node) => `${kind}: ${node.target.join(" ")} ${node.failureSummary ?? rule.help}`.replace(/\s+/g, " ")),
    );
  return [...lines("violation", result.violations), ...lines("incomplete", result.incomplete)];
}

/*
 * The pixel scan of hero text. axe cannot read the art of a hero, so this scan reads the pixels. It hides the text of
 * each hero, takes a screenshot of the page, and rates the color of each text against each pixel under its line boxes.
 * The worst pixel decides: for light text on the dark band, it is the brightest pixel. A text with alpha, or under a box
 * with opacity, blends into each pixel first, as the browser draws it. Each text reaches HERO_MIN_RATIO.
 * A hero where the scan finds no text fails, so a change to the markup cannot make the scan pass with no test.
 * A scope, a CSS selector, limits the scan to the heroes inside that part. The page is as it was after the scan.
 */
export async function scanHeroPixels(page: Page, scope?: string): Promise<string[]> {
  const heroes = (await page.evaluate<unknown, InPage>(inPage, { scan: "heroes", limits: LIMITS, scope })) as HeroScan[];
  if (heroes.length === 0) return [];
  const hide = await page.addStyleTag({
    content: "[data-floor-text] { color: transparent !important; -webkit-text-fill-color: transparent !important; text-shadow: none !important; }",
  });
  try {
    // Two frames, so the browser paints the hidden text before the screenshot.
    await page.evaluate(() => new Promise((done) => requestAnimationFrame(() => requestAnimationFrame(done))));
    // One shot of the full page. A shot of one element leaves the part of a tall hero under the viewport blank.
    const shot = await page.screenshot({ fullPage: true, caret: "hide" });
    const rated = await page.evaluate(rateHeroText, { png: shot.toString("base64"), heroes });
    const failures: string[] = [];
    for (const [h, hero] of heroes.entries()) {
      const read = rated[h].flatMap((text) => (text.ratio === null ? [] : [text.ratio]));
      if (read.length === 0) {
        failures.push(`pixel: hero "${hero.name}": the pixel scan finds no text`);
        continue;
      }
      // One line per hero, so the log of the floor shows that the scan ran on it and how close its worst text sits.
      console.log(`pixel scan: hero "${hero.name}": ${read.length} texts, worst ${Math.min(...read).toFixed(2)}:1`);
      for (const [t, text] of rated[h].entries()) {
        if (text.ratio === null || text.ratio >= HERO_MIN_RATIO) continue;
        failures.push(`pixel: hero "${hero.name}" ${hero.texts[t].label} is ${text.ratio.toFixed(2)}:1 on ${text.pixel}, under ${HERO_MIN_RATIO}:1`);
      }
    }
    return failures;
  } finally {
    await hide.evaluate((el) => (el as Element).remove());
    await page.evaluate(() => {
      for (const el of document.querySelectorAll<HTMLElement>("[data-floor-hero], [data-floor-text]")) {
        delete el.dataset.floorHero;
        delete el.dataset.floorText;
      }
    });
  }
}

/*
 * Runs in the page: decodes the full page shot and gives the worst ratio of each text of each hero, and the pixel of it.
 * The shot is in device pixels, so each box scales by the device pixel ratio. A text with no pixel in the shot gets null.
 */
async function rateHeroText({ png, heroes }: { png: string; heroes: HeroScan[] }) {
  const bytes = Uint8Array.from(atob(png), (ch) => ch.charCodeAt(0));
  const image = await createImageBitmap(new Blob([bytes], { type: "image/png" }));
  const canvas = new OffscreenCanvas(image.width, image.height);
  const ctx = canvas.getContext("2d")!;
  ctx.drawImage(image, 0, 0);
  const scale = devicePixelRatio;
  const channel = (c: number) => {
    const s = c / 255;
    return s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  };
  const luminance = (r: number, g: number, b: number) => 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
  const hex = (r: number, g: number, b: number) => "#" + [r, g, b].map((v) => Math.round(v).toString(16).padStart(2, "0")).join("");
  const rate = ({ color: [tr, tg, tb, alpha], boxes }: HeroText) => {
    let ratio: number | null = null;
    let pixel = "";
    for (const [x, y, w, h] of boxes) {
      const left = Math.max(0, Math.floor(x * scale));
      const top = Math.max(0, Math.floor(y * scale));
      const right = Math.min(image.width, Math.ceil((x + w) * scale));
      const bottom = Math.min(image.height, Math.ceil((y + h) * scale));
      if (right <= left || bottom <= top) continue;
      const data = ctx.getImageData(left, top, right - left, bottom - top).data;
      for (let k = 0; k < data.length; k += 4) {
        const [br, bg, bb] = [data[k], data[k + 1], data[k + 2]];
        const text = luminance(tr * alpha + br * (1 - alpha), tg * alpha + bg * (1 - alpha), tb * alpha + bb * (1 - alpha));
        const ground = luminance(br, bg, bb);
        const r = (Math.max(text, ground) + 0.05) / (Math.min(text, ground) + 0.05);
        if (ratio === null || r < ratio) {
          ratio = r;
          pixel = hex(br, bg, bb);
        }
      }
    }
    return { ratio, pixel };
  };
  return heroes.map((hero) => hero.texts.map(rate));
}

/*
 * The contrast scan of a page: axe, then the pixel scan of each hero.
 * A scope, a CSS selector, limits the scan to one part of the page, such as an open strip that covers the page under it.
 */
export async function scanContrast(page: Page, scope?: string): Promise<string[]> {
  return [...(await axeContrast(page, scope)), ...(await scanHeroPixels(page, scope))];
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
  // The steps scroll a list in a dialog, not a hero, so the pixel scan runs once, at the end.

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
    for (const line of await axeContrast(page, scope)) {
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
  for (const line of await scanHeroPixels(page, scope)) failures.add(line);
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
 * Last, it waits for each finite animation to end, so the scans read the page at rest. A part that fades in on the load,
 * such as the passphrase dialog of the analyzer, has a mixed color until its fade ends, so axe and the pixel scan
 * would read a color that the reader sees for a moment only. An endless animation never ends, so the wait skips it.
 */
export async function openPage(page: Page, url: string, theme: Theme): Promise<void> {
  await page.addInitScript(([key, value]) => localStorage.setItem(key, value), [THEME_KEY, theme] as const);
  await page.goto(url);
  const html = page.locator("html");
  const dark = new RegExp(`(^|\\s)${DARK_CLASS}(\\s|$)`);
  await (theme === "dark" ? expect(html).toHaveClass(dark) : expect(html).not.toHaveClass(dark));
  await page.evaluate(() =>
    Promise.all(
      document
        .getAnimations()
        .filter((animation) => animation.effect?.getComputedTiming().endTime !== Infinity)
        .map((animation) => animation.finished.catch(() => undefined)),
    ),
  );
}
