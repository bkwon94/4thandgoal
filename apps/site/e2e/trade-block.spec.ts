/**
 * The Trade block strip of Find mode in WebKit, as Safari runs, on the phone, the iPad, and the desktop: the move of a
 * pick to the front with motion on and off, the keyboard, the accessibility tree, and the fit of the strip in the hero.
 */
import { type Locator, type Page, devices, expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { Theme } from "@cpc/design/lib/theme";
import { LOCAL_API } from "./evidence";
import { openPage } from "./floor";
import { serveDir } from "./serve";
import { findOverlap } from "./smoke";

const OUT = join(process.cwd(), "out");
// Run it on the export of NorCal built against the local API URL, as the grade-bar project does:
// CLIENT=norcal NEXT_PUBLIC_API_URL=http://localhost:8080 pnpm build
// The roster of Bo Girds in cpc, as the teams route sends it, and the teams of a real find for him as the partners.
const FIXTURES = join(process.cwd(), "..", "..", "packages", "analyzer", "site", "lib", "fixtures");
const BO_GIRDS = JSON.parse(readFileSync(join(FIXTURES, "team-bo-girds.json"), "utf8")) as {
  roster_id: number;
};
const FIND = JSON.parse(readFileSync(join(FIXTURES, "find-response-bo-girds-rb.json"), "utf8")) as {
  trades: { sides: { roster_id: number; team: string }[] }[];
};
const PARTNERS = [
  ...new Map(
    FIND.trades
      .flatMap((trade) => trade.sides)
      .filter((side) => side.roster_id !== BO_GIRDS.roster_id)
      .map((side) => [side.roster_id, side]),
  ).values(),
].map((side) => ({
  roster_id: side.roster_id,
  team: side.team,
  manager: side.team,
  avatar: null,
  players: [],
}));
const TEAMS = JSON.stringify({ teams: [BO_GIRDS, ...PARTNERS] });
const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-headers": "*",
  "access-control-allow-methods": "GET, POST",
};

const WALKER = "Kenneth Walker III, RB";
const FLOWERS = "Zay Flowers, WR";

// The browser of a file is set at its top, because a group cannot pick the browser. Safari runs on WebKit.
test.use({ browserName: "webkit", reducedMotion: "reduce" });

/* The iPhone 15 and the iPad Pro 11 with no browser of their own, because a group cannot pick the browser. */
const { defaultBrowserType: _phone, ...IPHONE } = devices["iPhone 15"];
const { defaultBrowserType: _tablet, ...IPAD } = devices["iPad Pro 11"];

/* The iPhone 15 at 390 by 660, the screen that Safari leaves under its bars, then the iPad upright and on its side, then the desktop. */
const VIEWPORTS = [
  { name: "iPhone 15 390x660", use: { ...IPHONE, viewport: { width: 390, height: 660 } } },
  { name: "iPad 810x980", use: { ...IPAD, viewport: { width: 810, height: 980 } } },
  { name: "iPad 1080x740", use: { ...IPAD, viewport: { width: 1080, height: 740 } } },
  { name: "desktop 1280x800", use: { viewport: { width: 1280, height: 800 } } },
] as const;

/* The sizes of the keyboard shots of AT-26: the iPhone, then 375, 768, and 1280 px wide. */
const KEY_VIEWPORTS = [
  VIEWPORTS[0],
  { name: "375x812", use: { viewport: { width: 375, height: 812 } } },
  { name: "768x1024", use: { viewport: { width: 768, height: 1024 } } },
  VIEWPORTS[3],
] as const;

let server: { url: string; close: () => Promise<void> };
test.beforeAll(async () => {
  server = await serveDir(OUT);
});
test.afterAll(async () => {
  await server?.close();
});

/* Opens the analyzer in Find mode with Bo Girds as Your team. The teams route sends his roster; no other request leaves the page. */
async function openFind(page: Page, theme: Theme) {
  await page.route(
    (url) => !["127.0.0.1", "localhost"].includes(url.hostname),
    (route) => route.abort(),
  );
  await page.route(`${LOCAL_API}/**`, (route) => {
    const request = route.request();
    if (request.method() === "OPTIONS") return route.fulfill({ status: 204, headers: CORS });
    if (request.url().includes("/teams"))
      return route.fulfill({
        status: 200,
        headers: CORS,
        contentType: "application/json",
        body: TEAMS,
      });
    return route.abort();
  });
  await page.addInitScript((asker) => {
    localStorage.setItem("cpc.passphrase", "test");
    localStorage.setItem("cpc.your-team", String(asker));
  }, BO_GIRDS.roster_id);
  await openPage(page, `${server.url}/analyze/?mode=find`, theme);
  await expect(strip(page)).toBeVisible();
}

const strip = (page: Page) => page.getByRole("group", { name: "Trade block" });
const toggle = (page: Page, name: string) => strip(page).getByRole("button", { name, exact: true });

/*
 * The glide runs on the clock of the page, and the samples read that clock too. A loaded runner drops
 * frames, so a sample by the wall clock can miss the glide. This init script gives the page a clock of frames:
 * `performance.now` and the time of each frame move by exactly `ms` per frame, whatever the real time between frames.
 * So the test sees the same frames on a fast Mac and on a loaded runner. The callbacks of one frame share one
 * timestamp, so the clock moves once per frame. It is the clock of `front-door-tour-motion.spec.ts`.
 */
async function frameClock(page: Page, ms = 1000 / 60) {
  await page.addInitScript((step) => {
    const raf = window.requestAnimationFrame.bind(window);
    const start = performance.now();
    let frames = 0;
    let last = -1;
    Object.defineProperty(performance, "now", {
      configurable: true,
      value: () => start + frames * step,
    });
    window.requestAnimationFrame = (callback) =>
      raf((time) => {
        if (time !== last) {
          last = time;
          frames += 1;
        }
        callback(performance.now());
      });
  }, ms);
}

/*
 * Keeps each Web Animation that the page starts through `Element.animate` in `window.recorded`. Framer Motion runs the
 * shake of the reason line as a Web Animation, so the test can find it and set its time.
 */
async function recordAnimations(page: Page) {
  await page.addInitScript(() => {
    const recorded: Animation[] = [];
    (window as unknown as { recorded: Animation[] }).recorded = recorded;
    const animate = Element.prototype.animate;
    Element.prototype.animate = function (this: Element, ...args: Parameters<Element["animate"]>) {
      const animation = animate.apply(this, args);
      recorded.push(animation);
      return animation;
    };
  });
}

/*
 * Taps a player of the strip in the page, then reads the left edge of his toggle and of the first place of the strip on
 * each frame after the tap, for `ms`. The click runs in the page, so the first sample is the first frame after the tap.
 */
async function framesAfterTap(page: Page, name: string, ms: number) {
  return page.evaluate(
    ([label, span]) =>
      new Promise<{ t: number; x: number; front: number }[]>((done) => {
        const group = document.querySelector(
          '[role="group"][aria-label="Trade block"]',
        ) as HTMLElement;
        const button = group.querySelector(`[aria-label="${label}"]`) as HTMLElement;
        // The first place of the strip: the left edge of the group plus its left padding.
        const front = () =>
          group.getBoundingClientRect().left + parseFloat(getComputedStyle(group).paddingLeft);
        const samples: { t: number; x: number; front: number }[] = [];
        const start = performance.now();
        button.click();
        const read = () => {
          const t = Math.round(performance.now() - start);
          samples.push({
            t,
            x: Math.round(button.getBoundingClientRect().left * 10) / 10,
            front: Math.round(front() * 10) / 10,
          });
          if (t < span) requestAnimationFrame(read);
          else done(samples);
        };
        requestAnimationFrame(read);
      }),
    [name, ms] as const,
  );
}

/* No text of the page overlaps another, and the page never scrolls sideways. The fixed and sticky parts sit over
   content that the reader scrolls past, so the scan hides each one for its run. */
async function expectNoOverlap(page: Page, name: string) {
  const hidden = await page.evaluate(() => {
    const bars = [...document.querySelectorAll<HTMLElement>("body *")].filter((el) =>
      ["fixed", "sticky"].includes(getComputedStyle(el).position),
    );
    for (const bar of bars) bar.style.visibility = "hidden";
    return bars.length;
  });
  const overlap = await findOverlap(page);
  console.log(
    `${name}: the text scan hides ${hidden} fixed or sticky parts; overlap: ${overlap ?? "none"}`,
  );
  expect(overlap).toBeNull();
  await page.evaluate(() => {
    for (const el of document.querySelectorAll<HTMLElement>("body *"))
      if (el.style.visibility === "hidden") el.style.visibility = "";
  });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  );
}

/* The fixed and sticky parts of the page that show and cover a part of the screen. */
async function fixedBars(page: Page) {
  return page.evaluate(() =>
    [...document.querySelectorAll<HTMLElement>("body *")]
      .filter(
        (el) =>
          ["fixed", "sticky"].includes(getComputedStyle(el).position) &&
          el.checkVisibility({ opacityProperty: true, visibilityProperty: true }),
      )
      .map((el) => ({
        name: el.getAttribute("aria-label") ?? el.tagName.toLowerCase(),
        ...el.getBoundingClientRect().toJSON(),
      }))
      .filter(
        (box) => box.width > 0 && box.height > 0 && box.bottom > 0 && box.top < window.innerHeight,
      ),
  );
}

/* True when the fixed bar covers a part of the box that shows on the screen. A bar at the top of the screen sits over
   content that scrolled up past it, which the reader can scroll back. */
async function covers(
  bar: { top: number; bottom: number; left: number; right: number },
  part: Locator,
  height: number,
) {
  const box = (await part.boundingBox())!;
  const top = Math.max(box.y, 0);
  const bottom = Math.min(box.y + box.height, height);
  if (bottom <= top || bar.top < 1) return false;
  const across = Math.min(box.x + box.width, bar.right) - Math.max(box.x, bar.left);
  const down = Math.min(bottom, bar.bottom) - Math.max(top, bar.top);
  return across > 0 && down > 0;
}

for (const viewport of VIEWPORTS) {
  test.describe(viewport.name, () => {
    test.use(viewport.use);

    // With motion off, a pick lands at the front on the first frame after the tap, with no frame between.
    test("motion off: a pick is at the front one frame after the tap (AT-24)", async ({ page }) => {
      await openFind(page, "light");
      const frames = await framesAfterTap(page, WALKER, 100);
      const first = frames[0];
      console.log(
        `${viewport.name} motion off: one frame after the tap (${first.t} ms), Walker x=${first.x}, the front x=${first.front}`,
      );
      expect(Math.abs(first.x - first.front)).toBeLessThanOrEqual(1);
      for (const frame of frames) expect(Math.abs(frame.x - frame.front)).toBeLessThanOrEqual(1);
      await expect(toggle(page, WALKER)).toHaveAttribute("aria-pressed", "true");
    });

    // With motion on, a pick glides to the front with a spring of 0.4 s and no bounce: it starts where it was, never
    // passes the front, and rests there by the end of the spring.
    test.describe("motion on", () => {
      test.use({ reducedMotion: "no-preference" });
      test("a pick moves to the front with a spring of 0.4 s and no bounce", async ({ page }) => {
        await frameClock(page);
        await openFind(page, "light");
        const before = (await toggle(page, WALKER).boundingBox())!.x;
        const frames = await framesAfterTap(page, WALKER, 800);
        const front = frames.at(-1)!.front;
        console.log(
          `${viewport.name} motion on: Walker x=${before} before the tap, the front x=${front}`,
        );
        console.log(frames.map((f) => `${f.t}ms x=${f.x}`).join(", "));
        // The first frame after the tap still shows Walker near his old place, so the move is a glide and not a jump.
        expect(frames[0].x - front).toBeGreaterThan((before - front) / 2);
        // No bounce: each frame is at or right of the front, and each frame is at or left of the frame before.
        for (const [i, frame] of frames.entries()) {
          expect(frame.x).toBeGreaterThanOrEqual(front - 1);
          if (i > 0) expect(frame.x).toBeLessThanOrEqual(frames[i - 1].x + 1);
        }
        // The spring of 0.4 s brings him within a px of the front by 500 ms, which allows one frame of lag.
        const rest = frames.find((frame) => Math.abs(frame.x - front) <= 1)!;
        console.log(`${viewport.name} motion on: Walker rests at the front at ${rest.t} ms`);
        expect(rest.t).toBeGreaterThan(200);
        expect(rest.t).toBeLessThanOrEqual(500);
      });

      // The reader has scrolled the strip to its end. The strip scrolls back as the pick glides, so he leaves the
      // place under the thumb with no jump and lands at the front.
      test("a pick from the scrolled end glides back to the front with no jump", async ({
        page,
      }) => {
        await openFind(page, "light");
        const tight = await page.evaluate(() => {
          const area = document
            .querySelector('[role="group"][aria-label="Trade block"]')!
            .closest("[data-slot=scroll-area-viewport]") as HTMLElement;
          area.style.scrollBehavior = "auto";
          area.scrollLeft = area.scrollWidth;
          area.style.scrollBehavior = "";
          return area.scrollLeft;
        });
        const name = "Parker Washington, WR";
        const before = (await toggle(page, name).boundingBox())!.x;
        const frames = await framesAfterTap(page, name, 900);
        const front = frames.at(-1)!.front;
        console.log(
          `${viewport.name} scrolled ${tight} px: Parker Washington x=${before} before the tap, the front x=${front}`,
        );
        console.log(frames.map((f) => `${f.t}ms x=${f.x}`).join(", "));
        // No jump on the first frame: he is still within 40 px of his old place.
        expect(Math.abs(frames[0].x - before)).toBeLessThanOrEqual(40);
        for (const [i, frame] of frames.entries())
          if (i > 0) expect(frame.x).toBeLessThanOrEqual(frames[i - 1].x + 1);
        expect(Math.abs(frames.at(-1)!.x - front)).toBeLessThanOrEqual(1);
      });
    });

    // A refused 4th tap shakes the reason line with motion on, and each refused tap shakes it again. With motion off,
    // the line shows at once and holds still.
    for (const motion of ["no-preference", "reduce"] as const) {
      test.describe(`reason line, motion ${motion}`, () => {
        test.use({ reducedMotion: motion });
        test(`a refused 4th tap ${motion === "reduce" ? "shows the reason with no shake" : "shakes the reason line each time"}`, async ({
          page,
        }) => {
          await recordAnimations(page);
          await openFind(page, "light");
          for (const name of [WALKER, FLOWERS, "Blake Corum, RB"]) await toggle(page, name).click();
          const reason = page.getByText(/^Your block holds 3 players/);
          // The animations of the reason line that started after the mark `from`, as an index of the record.
          const shakesSince = (from: number) =>
            page.evaluate(
              (first) =>
                (window as unknown as { recorded: Animation[] }).recorded
                  .slice(first)
                  .filter((animation) =>
                    (
                      (animation.effect as KeyframeEffect).target as Element | null
                    )?.textContent?.startsWith("Your block holds 3 players"),
                  ).length,
              from,
            );
          for (const tap of [1, 2]) {
            const from = await page.evaluate(
              () => (window as unknown as { recorded: Animation[] }).recorded.length,
            );
            await toggle(page, "Lamar Jackson, QB").click();
            await expect(reason).toBeVisible();
            let seen: number[];
            if (motion === "reduce") {
              // With motion off the line holds still on each frame for 600 ms, and no animation starts on it.
              seen = await page.evaluate(
                () =>
                  new Promise<number[]>((done) => {
                    const line = [...document.querySelectorAll("p")].find((p) =>
                      p.textContent?.startsWith("Your block holds 3 players"),
                    )!;
                    const seen: number[] = [];
                    const start = performance.now();
                    const read = () => {
                      seen.push(Math.round(line.getBoundingClientRect().left * 10) / 10);
                      if (performance.now() - start < 600) requestAnimationFrame(read);
                      else done(seen);
                    };
                    requestAnimationFrame(read);
                  }),
              );
              expect(await shakesSince(from)).toBe(0);
            } else {
              /* The shake is a Web Animation that Framer Motion starts on the line. The test pauses each animation that
                 started on the line after the tap, sets its time frame by frame, every 1000/60 ms from the start to the
                 end, and reads the place of the line at each time. Framer Motion can start more than one, so the test
                 keeps the samples of the animation that moves the line the most. So the samples do not hang on the
                 speed of the machine, and each tap must start its own shake. */
              await expect.poll(() => shakesSince(from)).toBeGreaterThanOrEqual(1);
              seen = await page.evaluate((first) => {
                const shakes = (window as unknown as { recorded: Animation[] }).recorded
                  .slice(first)
                  .filter((animation) =>
                    (
                      (animation.effect as KeyframeEffect).target as Element | null
                    )?.textContent?.startsWith("Your block holds 3 players"),
                  );
                const runs = shakes.map((shake) => {
                  const line = (shake.effect as KeyframeEffect).target as Element;
                  const end = Number(shake.effect!.getComputedTiming().endTime);
                  const run: number[] = [];
                  shake.pause();
                  for (let t = 0; t <= end; t += 1000 / 60) {
                    shake.currentTime = t;
                    run.push(Math.round(line.getBoundingClientRect().left * 10) / 10);
                  }
                  shake.finish();
                  return run;
                });
                const spread = (run: number[]) => Math.max(...run) - Math.min(...run);
                return runs.reduce((best, run) => (spread(run) > spread(best) ? run : best));
              }, from);
            }
            const spread = Math.max(...seen) - Math.min(...seen);
            console.log(
              `${viewport.name} motion ${motion}: refused tap ${tap}, the reason line moves ${spread} px across ${seen.length} frames`,
            );
            expect(seen.length).toBeGreaterThan(0);
            if (motion === "reduce") expect(spread).toBe(0);
            else expect(spread).toBeGreaterThanOrEqual(6);
          }
        });
      });
    }

    // A pointer that rests on a player lifts his name to the full ink of a pick. A touch screen has no hover.
    if (viewport.name.startsWith("desktop"))
      test("a pointer on a player lifts his name to full ink", async ({ page }) => {
        await openFind(page, "light");
        await toggle(page, WALKER).click();
        const ink = (name: string) =>
          toggle(page, name)
            .locator("span")
            .nth(-2)
            .evaluate((el) => getComputedStyle(el).color);
        const rest = await ink("Aaron Rodgers, QB");
        await toggle(page, "Aaron Rodgers, QB").hover();
        await expect.poll(() => ink("Aaron Rodgers, QB")).toBe(await ink(WALKER));
        console.log(
          `${viewport.name}: Rodgers name ${rest} at rest, ${await ink("Aaron Rodgers, QB")} under the pointer`,
        );
      });

    // Each item reads as a toggle with the name and the position, and only a pick has the pressed state.
    test("each item reads as a toggle with the name, the position, and the state (AT-25)", async ({
      page,
    }) => {
      await openFind(page, "light");
      await toggle(page, WALKER).click();
      const tree = await strip(page).ariaSnapshot();
      console.log(`${viewport.name} accessibility tree of the strip:\n${tree}`);
      const buttons = await strip(page).getByRole("button").all();
      expect(buttons).toHaveLength(14);
      for (const button of buttons) {
        const name = (await button.getAttribute("aria-label"))!;
        expect(name).toMatch(/^.+, (QB|RB|WR|TE)$/);
        await expect(button).toHaveAttribute("aria-pressed", name === WALKER ? "true" : "false");
      }
    });

    // The strip fills the width of the hero, and with two picks no text overlaps and no fixed bar covers the controls.
    for (const theme of ["light", "dark"] as const) {
      test(`the strip fits the hero with two picks, ${theme} (AT-27)`, async ({ page }, info) => {
        await openFind(page, theme);
        await toggle(page, WALKER).click();
        await toggle(page, FLOWERS).click();
        await expect(page.getByText("2 of 3")).toBeVisible();
        await page.screenshot({
          path: info.outputPath(`trade-block-${theme}.png`),
          fullPage: true,
        });

        // The scroll area of the strip runs from the inner left edge of the hero to its inner right edge.
        const fit = await page.evaluate(() => {
          const hero = document.querySelector(
            'section[aria-label="Trade Ideas"] section[aria-label="Trade Ideas"]',
          ) as HTMLElement;
          const area = document
            .querySelector('[role="group"][aria-label="Trade block"]')!
            .closest("[data-slot=scroll-area-viewport]") as HTMLElement;
          const h = hero.getBoundingClientRect();
          const a = area.getBoundingClientRect();
          const border = parseFloat(getComputedStyle(hero).borderLeftWidth);
          return {
            heroLeft: h.left + border,
            heroRight: h.right - border,
            stripLeft: a.left,
            stripRight: a.right,
          };
        });
        console.log(
          `${viewport.name} ${theme}: hero inner ${fit.heroLeft} to ${fit.heroRight}, strip ${fit.stripLeft} to ${fit.stripRight}`,
        );
        expect(Math.abs(fit.stripLeft - fit.heroLeft)).toBeLessThanOrEqual(1);
        expect(Math.abs(fit.stripRight - fit.heroRight)).toBeLessThanOrEqual(1);

        await expectNoOverlap(page, `${viewport.name} ${theme}`);

        // No fixed bar covers the strip, the chips, or the find button, at the top of the page or scrolled to them.
        const parts = [
          strip(page),
          page.getByRole("radiogroup", { name: "Position" }),
          page.getByRole("button", { name: "Find a Trade" }),
        ];
        for (const part of parts) {
          await part.scrollIntoViewIfNeeded();
          const bars = await fixedBars(page);
          for (const bar of bars)
            expect(
              await covers(bar, part, viewport.use.viewport.height),
              `the fixed part ${bar.name} covers a control`,
            ).toBe(false);
        }
        console.log(
          `${viewport.name} ${theme}: no fixed bar covers the strip, the chips, or the find button`,
        );
      });
    }
  });
}

// Tab reaches the strip, the arrow keys move to Flowers, and Space puts him on the block.
for (const viewport of KEY_VIEWPORTS) {
  test.describe(`keyboard ${viewport.name}`, () => {
    test.use(viewport.use);
    for (const theme of ["light", "dark"] as const) {
      test(`Tab, the arrow keys, and Space put Flowers on the block, ${theme} (AT-26)`, async ({
        page,
      }, info) => {
        await openFind(page, theme);
        // Tab from the Your team button, the control before the strip.
        await page.getByRole("button", { name: /Your team/ }).focus();
        await page.keyboard.press("Tab");
        const focused = () =>
          page.evaluate(
            () =>
              document.activeElement?.getAttribute("aria-label") ??
              document.activeElement?.tagName ??
              "",
          );
        const start = await focused();
        console.log(`${viewport.name} ${theme}: Tab lands on "${start}"`);
        expect(
          await page.evaluate(() =>
            document.activeElement?.closest('[role="group"]')?.getAttribute("aria-label"),
          ),
        ).toBe("Trade block");
        const path = [start];
        for (let i = 0; i < 20 && (await focused()) !== FLOWERS; i++) {
          await page.keyboard.press("ArrowRight");
          path.push(await focused());
        }
        console.log(`${viewport.name} ${theme}: the arrow keys move ${path.join(" > ")}`);
        expect(await focused()).toBe(FLOWERS);
        await page.keyboard.press("Space");
        await expect(toggle(page, FLOWERS)).toHaveAttribute("aria-pressed", "true");
        await expect(page.getByText("1 of 3")).toBeVisible();
        // The focus stays on Flowers at the front, with its ring in view, so the reader can press Space again to undo.
        const ring = await page.evaluate(() => {
          const el = document.activeElement as HTMLElement;
          const style = getComputedStyle(el);
          return {
            name: el.getAttribute("aria-label"),
            outline: `${style.outlineStyle} ${style.outlineWidth}`,
            visible: el.matches(":focus-visible"),
          };
        });
        console.log(
          `${viewport.name} ${theme}: after Space, Flowers is pressed, the counter reads 1 of 3, and the focus is on "${ring.name}" with the outline ${ring.outline}`,
        );
        expect(ring.name).toBe(FLOWERS);
        expect(ring.visible).toBe(true);
        expect(ring.outline).toBe("solid 2px");
        await page.screenshot({
          path: info.outputPath(`trade-block-keyboard-${theme}.png`),
          fullPage: true,
        });
      });
    }
  });
}
