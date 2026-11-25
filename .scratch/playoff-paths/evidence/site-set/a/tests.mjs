/**
 * The steps of tests AT-26 to AT-43 of playoff-paths for run.mjs. Each test opens its route, runs its taps, and takes named shots.
 * The notes save what the page held, such as the board rows and the colors, beside the shots.
 */

/* The state of The Race page: the card, the Finish list, and the board rows with the color and width of each bar. */
const raceState = (page) => page.evaluate(() => {
  const clean = (s) => s.replace(/\s+/g, " ").trim();
  const card = [...document.querySelectorAll("button")].find((b) => /^YOUR TEAM/i.test(clean(b.innerText)));
  const finishes = [...document.querySelectorAll("button[aria-label]")].filter((b) => /^\d-\d, ends/.test(b.getAttribute("aria-label"))).map((b) => b.getAttribute("aria-label"));
  const rows = [...document.querySelectorAll("button[aria-label]")].filter((b) => /odds of (a playoff spot|a bye|the \d seed)\./.test(b.getAttribute("aria-label")) && !/^\d-\d, ends/.test(b.getAttribute("aria-label")));
  const board = rows.map((b) => {
    const bars = [...b.querySelectorAll("*")].filter((e) => { const r = e.getBoundingClientRect(); const bg = getComputedStyle(e).backgroundColor; return r.height > 0 && r.height <= 12 && r.width > 0 && bg !== "rgba(0, 0, 0, 0)" && bg !== "transparent"; });
    const fill = bars.sort((x, y) => x.getBoundingClientRect().width - y.getBoundingClientRect().width)[0];
    return { label: b.getAttribute("aria-label"), bar: fill ? { color: getComputedStyle(fill).backgroundColor, width: Math.round(fill.getBoundingClientRect().width) } : null };
  });
  return { card: card ? clean(card.innerText) : null, finishes, board };
});

/* The contrast of each pill of the board: the text color against the pill color composited over the colors behind it. */
const pillContrast = (page) => page.evaluate(() => {
  const canvas = document.createElement("canvas"); canvas.width = canvas.height = 1;
  const g = canvas.getContext("2d", { willReadFrequently: true });
  const rgba = (css) => { g.clearRect(0, 0, 1, 1); g.fillStyle = "#000"; g.fillStyle = css; g.fillRect(0, 0, 1, 1); return [...g.getImageData(0, 0, 1, 1).data]; };
  // The color behind el: each background from the root down, drawn over white, then read as one pixel.
  const behind = (el) => {
    const chain = []; for (let e = el; e; e = e.parentElement) chain.unshift(e);
    g.clearRect(0, 0, 1, 1); g.fillStyle = "#fff"; g.fillRect(0, 0, 1, 1);
    for (const e of chain) { const bg = getComputedStyle(e).backgroundColor; g.fillStyle = bg; g.fillRect(0, 0, 1, 1); }
    return [...g.getImageData(0, 0, 1, 1).data];
  };
  const lum = ([r, gg, b]) => { const f = (c) => { c /= 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(r) + 0.7152 * f(gg) + 0.0722 * f(b); };
  const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((m, n) => n - m); return (x + 0.05) / (y + 0.05); };
  const rows = [...document.querySelectorAll("button[aria-label]")].filter((b) => /odds of a playoff spot\./.test(b.getAttribute("aria-label")) && !/^\d-\d, ends/.test(b.getAttribute("aria-label")));
  const out = [];
  for (const row of rows) {
    for (const e of row.querySelectorAll("*")) {
      const cs = getComputedStyle(e);
      const t = e.innerText?.trim();
      if (!t || t.length > 30 || e.children.length > 1) continue;
      const bg = rgba(cs.backgroundColor);
      if (bg[3] === 0) continue;
      const back = behind(e), text = rgba(cs.color);
      // The text color, composited over the pill color, as the eye sees it.
      const a = text[3] / 255; const seen = [0, 1, 2].map((i) => Math.round(text[i] * a + back[i] * (1 - a)));
      out.push({ team: row.getAttribute("aria-label").split(":")[0], pill: t, text: cs.color, background: cs.backgroundColor, seenText: seen, seenBackground: back.slice(0, 3), contrast: Number(ratio(seen, back).toFixed(2)) });
    }
  }
  return out;
});

const RESULT_WAIT = 15000;
/* Taps a button and waits for the What-if answer of the API, or for the time limit. */
async function tapAndWaitApi(page, locator) {
  const answer = page.waitForResponse((r) => r.request().method() === "POST" && /what-if|whatif|sim/i.test(r.url()), { timeout: RESULT_WAIT }).catch(() => null);
  await locator.click();
  const res = await answer;
  await page.waitForTimeout(1500);
  return res;
}

const card = (page) => page.locator("button", { hasText: /^\s*YOUR TEAM/i }).first();

export default {
  "AT-26": {
    // PREFIX names a second recording beside the first, such as site-5f26bcb0-.
    prefix: process.env.PREFIX ?? "site-",
    route: "/",
    calls: true,
    async run({ page, shot, note, view, theme, folder, prefix }) {
      await page.locator("button", { hasText: "More" }).first().click();
      // The Suggestions list loads its order from the API, so the tap waits until the list is still.
      // The quick chip "Playoffs" in the row above carries the same aria-label, and its first tap only opens a strip with
      // "Open →" (suggestions.tsx). So the tap takes the Suggestion of the More list, whose text holds "Playoff race".
      const chip = page.locator("button[aria-label^='Playoff race']", { hasText: "Playoff race" }).first();
      await chip.waitFor({ state: "visible" });
      await page.waitForLoadState("networkidle");
      await page.waitForTimeout(800);
      const link = page.locator("a", { hasText: "Open The Race" }).first();
      await chip.click();
      const shownFirst = await link.waitFor({ state: "visible", timeout: 20000 }).then(() => true, () => false);
      const quickPlayoffs = await page.locator("button", { hasText: /^\s*Playoffs\s*$/ }).count();
      note("tries.txt", (shownFirst ? "the Answer showed after the first tap" : "the Answer did not show within 20 s of the first tap") + "; quick chip \"Playoffs\" in the row: " + (quickPlayoffs > 0 ? "yes" : "no"));
      await link.waitFor({ state: "visible", timeout: 5000 });
      await page.waitForTimeout(1500);
      await shot("answer");
      // The full-page shot draws the sticky Ask bar in the middle of the page, so viewport shots step through the Answer too.
      const top = await page.evaluate(() => { const b = [...document.querySelectorAll("*")].find((e) => e.children.length === 0 && e.textContent.trim() === "Playoff race"); return b ? b.getBoundingClientRect().top + scrollY - 80 : 0; });
      const stepPx = Math.max(200, view.h - 300);
      for (let i = 0, y = top; i < 6; i++, y += stepPx) {
        await page.evaluate((y) => window.scrollTo(0, y), y);
        await page.waitForTimeout(600);
        await page.screenshot({ path: `${folder}/${prefix}answer-view${i + 1}-${view.w}x${view.h}-${theme}.png` });
        const end = await page.evaluate(() => scrollY + innerHeight >= document.documentElement.scrollHeight - 2);
        if (end) break;
      }
      note("answer.txt", await page.evaluate(() => {
        const link = [...document.querySelectorAll("a")].find((a) => a.innerText.trim() === "Open The Race");
        const box = link?.closest("article, section, li, [data-entry], div[class*=answer]") ?? link?.parentElement?.parentElement;
        let el = link; for (let i = 0; i < 12 && el && !/Playoff race/.test(el.innerText); i++) el = el.parentElement;
        return { link: link && { text: link.innerText.trim(), href: link.getAttribute("href") }, answerText: el?.innerText ?? box?.innerText ?? null };
      }));
    },
  },
  "AT-27": {
    route: "/sim/2026/",
    async run({ page, shot, note }) {
      await shot("page");
      // At 1080 and 1280 the header shows the pill bar, and the menu button is hidden.
      const menu = page.locator("button[aria-label='Open the menu']").first();
      if (await menu.isVisible()) {
        await menu.click();
        await page.waitForTimeout(1000);
        await shot("menu", { sheetEnd: false });
      } else {
        note("labels.txt", "the menu button is hidden at this width; the header pill bar is the menu: " + JSON.stringify(await page.evaluate(() => [...document.querySelectorAll("header a, nav a")].map((a) => a.innerText.replace(/\s+/g, " ").trim()).filter(Boolean))));
        await page.evaluate(() => window.scrollTo(0, 0));
        await shot("menu", { viewport: true });
      }
      note("labels.txt", await page.evaluate(() => ({
        title: document.title,
        h1: document.querySelector("h1")?.innerText,
        menu: [...document.querySelectorAll("[role=dialog] a, nav a")].map((a) => ({ text: a.innerText.replace(/\s+/g, " ").trim(), aria: a.getAttribute("aria-label"), href: a.getAttribute("href") })).filter((a) => /sim/.test(a.href ?? "")),
      })));
    },
  },
  "AT-28": {
    route: "/sim/2026/",
    async run({ page, shot, note }) {
      note("state.txt", { when: "before the tap", ...(await raceState(page)) });
      await shot("before");
      await page.locator("button", { hasText: /^Bye$/ }).first().click();
      await page.waitForTimeout(1200);
      note("state.txt", { when: "after the tap on Bye", ...(await raceState(page)) });
      await shot("after");
    },
  },
  "AT-29": {
    route: "/sim/2026/",
    async run({ page, shot, note }) {
      await page.locator("button", { hasText: /^Seed$/ }).first().click();
      await page.waitForTimeout(800);
      await page.locator("button[aria-label='Seed 3']").first().click();
      await page.waitForTimeout(1200);
      note("state.txt", { when: "after Seed, then 3", ...(await raceState(page)), clinchLines: await page.evaluate(() => document.body.innerText.split("\n").filter((l) => /^(Clinches|Out with)/.test(l))) });
      await shot("seed-3");
    },
  },
  "AT-30": {
    route: "/sim/2026/",
    async run({ page, shot, note }) {
      const state = async (when) => note("state.txt", { when, expanded: await card(page).getAttribute("aria-expanded"), dialogs: await page.locator("[role=dialog]:visible").count(), order: await page.evaluate(() => { const t = document.body.innerText; return { finishList: t.indexOf("REST OF SEASON"), weekCard: t.indexOf("Week 12 vs") }; }) });
      await state("as loaded");
      await shot("loaded");
      await card(page).click();
      await page.waitForTimeout(1200);
      await state("after one tap on the card");
      await shot("tap-1");
      await card(page).click();
      await page.waitForTimeout(1200);
      await state("after a second tap on the card");
      await shot("tap-2");
    },
  },
  "AT-31": {
    route: "/sim/2026/",
    async run({ page, shot, note }) {
      await page.locator("button[aria-label^='4-2,']").first().click();
      await page.waitForTimeout(1200);
      note("paths.txt", await page.evaluate(() => { const t = document.body.innerText; const i = t.indexOf("4-2 · ends"); return t.slice(i, t.indexOf("3-3\nends", i)); }));
      await page.locator("button[aria-label^='4-2,']").first().scrollIntoViewIfNeeded();
      await shot("finish-4-2");
    },
  },
  "AT-32": {
    route: "/sim/2026/",
    async run({ page, shot, note }) {
      for (const rec of ["6-0", "0-6", "3-3"]) {
        await page.locator(`button[aria-label^='${rec},']`).first().click();
        await page.waitForTimeout(1200);
        note("finishes.txt", { tapped: rec, text: await page.evaluate(() => { const t = document.body.innerText; return t.slice(t.indexOf("REST OF SEASON"), t.indexOf("Week 12 vs")); }) });
        await shot(`finish-${rec}`);
      }
    },
  },
  "AT-33": {
    route: "/sim/2026/",
    async run({ page, shot, note }) {
      await page.locator("button[aria-label^='4-2,']").first().click();
      await page.waitForTimeout(1000);
      await page.locator("button[aria-label^='Week plan:']").first().click();
      await page.locator("[role=dialog]").first().waitFor({ state: "visible" });
      await page.waitForTimeout(1200);
      note("sheet.txt", await page.locator("[role=dialog]").last().innerText());
      await shot("plan");
    },
  },
  "AT-34": {
    route: "/sim/2026/",
    calls: true,
    async run({ page, shot, note }) {
      await page.locator("button[aria-label^='4-2,']").first().click();
      await page.waitForTimeout(1000);
      await page.locator("button[aria-label^='Week plan:']").first().click();
      await page.locator("[role=dialog]").first().waitFor({ state: "visible" });
      await page.waitForTimeout(1000);
      const header = await page.locator("[role=dialog]").last().innerText();
      await shot("plan", { sheetEnd: false });
      const res = await tapAndWaitApi(page, page.locator("button", { hasText: /^Try it/ }).first());
      await page.waitForTimeout(1500);
      note("state.txt", { planSheet: header.split("\n")[0], tryIt: header.split("\n").find((l) => /^Try it/.test(l)), answer: res ? { url: res.url(), status: res.status() } : "no POST answer within 15 s", dialogsOpen: await page.locator("[role=dialog]:visible").count(), card: (await raceState(page)).card, setLine: await page.evaluate(() => { const t = document.body.innerText; const i = t.search(/Reset/); return i < 0 ? null : t.slice(Math.max(0, i - 300), i + 20); }) });
      await page.evaluate(() => window.scrollTo(0, 0));
      await shot("after-try");
    },
  },
  "AT-35": {
    route: "/sim/2026/",
    async run({ page, shot, note }) {
      note("week-card.txt", await page.evaluate(() => { const t = document.body.innerText; const i = t.indexOf("Week 12 vs"); return t.slice(i, t.indexOf("Tap a result", i)); }));
      await page.locator("text=Week 12 vs Teez Nuts").first().scrollIntoViewIfNeeded();
      await shot("week-card");
    },
  },
  "AT-36": {
    route: "/sim/2026/",
    calls: true,
    async run({ page, shot, note }) {
      note("state.txt", { when: "before the tap", ...(await raceState(page)) });
      await shot("before");
      const res = await tapAndWaitApi(page, page.locator("button", { hasText: "Lose and miss the median" }).first());
      note("state.txt", { when: "after the tap on Lose and miss the median", answer: res ? { url: res.url(), status: res.status() } : "no POST answer within 15 s", setLine: await page.evaluate(() => { const t = document.body.innerText; const i = t.search(/Reset/); return i < 0 ? null : t.slice(Math.max(0, i - 300), i + 20); }), ...(await raceState(page)) });
      await shot("after");
    },
  },
  "AT-37": {
    route: "/sim/2026/",
    calls: true,
    async run({ page, shot, note }) {
      const res = await tapAndWaitApi(page, page.locator("button", { hasText: "Win and beat the median" }).first());
      note("root-for.txt", { answer: res ? { url: res.url(), status: res.status() } : "no POST answer within 15 s", text: await page.evaluate(() => { const t = document.body.innerText; const i = t.search(/Root for:/); return i < 0 ? null : t.slice(Math.max(0, i - 120), t.indexOf("Sim week", i)); }), doesntMatterTag: await page.evaluate(() => { const e = [...document.querySelectorAll("*")].find((x) => x.children.length === 0 && /doesn.t matter/i.test(x.textContent)); return e ? { text: e.textContent, color: getComputedStyle(e).color, background: getComputedStyle(e).backgroundColor } : null; }) });
      await page.locator("text=Root for").first().scrollIntoViewIfNeeded().catch(() => {});
      await shot("root-for");
    },
  },
  "AT-38": {
    route: "/sim/2026/",
    async run({ page, shot, note }) {
      note("board.txt", await raceState(page).then((s) => s.board));
      note("you-tag.txt", await page.evaluate(() => { const b = [...document.querySelectorAll("button[aria-label]")].find((x) => /your team: \d+% odds/.test(x.getAttribute("aria-label"))); return b ? b.innerText.replace(/\s+/g, " ") : null; }));
      await page.locator("text=League board").first().scrollIntoViewIfNeeded();
      await shot("board");
    },
  },
  "AT-39": {
    route: "/sim/2026/",
    async run({ page, shot, note }) {
      note("pill-contrast.txt", await pillContrast(page));
      await page.locator("text=League board").first().scrollIntoViewIfNeeded();
      await shot("board");
    },
  },
  "AT-40": {
    route: "/sim/2026/",
    async run({ page, shot, note }) {
      note("clinch-lines.txt", await page.evaluate(() => document.body.innerText.split("\n").filter((l) => /^(Clinches|Out with|In with)/.test(l))));
      await page.locator("text=League board").first().scrollIntoViewIfNeeded();
      await shot("board");
    },
  },
  "AT-41": {
    route: "/sim/2026/",
    async run({ page, shot, note }) {
      await page.locator("button[aria-label^='Lil Fridge:']").first().click();
      await page.locator("[role=dialog]").first().waitFor({ state: "visible" });
      await page.waitForTimeout(1200);
      note("sheet.txt", await page.locator("[role=dialog]").last().innerText());
      await shot("sheet");
    },
  },
  "AT-42": {
    route: "/sim/2026/",
    calls: true,
    async run({ page, shot, note }) {
      note("state.txt", { when: "as loaded, API stopped", ...(await raceState(page)) });
      await shot("loaded");
      await page.locator("button", { hasText: "Lose and miss the median" }).first().click();
      await page.waitForTimeout(4000);
      note("state.txt", { when: "after the tap on Lose and miss the median", ...(await raceState(page)), note: await page.evaluate(() => { const t = document.body.innerText; const i = t.indexOf("Lose and miss the median"); return t.slice(i, i + 600); }) });
      await shot("after-tap");
    },
  },
  "AT-43": {
    route: "/sim/2026/",
    async run({ page, shot, note }) {
      note("state.txt", { ...(await raceState(page)), weekCard: await page.evaluate(() => { const t = document.body.innerText; const i = t.search(/Week \d+ vs/); return i < 0 ? null : t.slice(i, t.indexOf("League board", i)); }) });
      await shot("page");
    },
  },
  // AT-37 on a changed copy of week-11/sim.json: one root-for game of "Win and beat the median" set 0 points apart.
  "AT-37-variant": {
    folder: "AT-37",
    prefix: "variant-under-1pt-zero-",
    route: "/sim/2026/",
    async run({ page, shot, note }) {
      note("root-for.txt", await page.evaluate(() => { const t = document.body.innerText; const i = t.search(/Root for:/); return i < 0 ? null : t.slice(Math.max(0, i - 120), t.indexOf("Sim week", i)); }));
      note("tags.txt", await page.evaluate(() => [...document.querySelectorAll("*")].filter((x) => x.children.length === 0 && /doesn.t matter/i.test(x.textContent)).map((e) => ({ row: e.closest("li")?.innerText.replace(/\s+/g, " "), color: getComputedStyle(e).color, background: getComputedStyle(e).backgroundColor }))));
      await page.locator("text=Root for").first().scrollIntoViewIfNeeded().catch(() => {});
      await shot("root-for");
    },
  },
  // AT-39 on a changed copy of week-11/sim.json: Lil Fridge spot "in"; Maye d'force B with U spot "in" and seed-1 "in".
  "AT-39-variant": {
    folder: "AT-39",
    prefix: "variant-clinched-",
    route: "/sim/2026/",
    async run({ page, shot, note }) {
      note("pill-contrast.txt", await pillContrast(page));
      await page.locator("text=League board").first().scrollIntoViewIfNeeded();
      await shot("board");
    },
  },
  // AT-34 again on 5f26bcb0, with a short reading of the request, the response, and the page, for a reader of text.
  "AT-34-reading": {
    folder: "AT-34",
    prefix: "5f26bcb0-",
    route: "/sim/2026/",
    async run({ page, shot, note }) {
      await page.locator("button[aria-label^='4-2,']").first().click();
      await page.waitForTimeout(1000);
      await page.locator("button[aria-label^='Week plan:']").first().click();
      const sheet = page.locator("[role=dialog]").last();
      await sheet.waitFor({ state: "visible" });
      await page.waitForTimeout(1000);
      const lines = (await sheet.innerText()).split("\n").filter(Boolean);
      await shot("plan", { sheetEnd: false });
      const answer = page.waitForResponse((r) => r.request().method() === "POST" && r.url().includes("/sim/what-if"), { timeout: 20000 });
      await page.locator("button", { hasText: /^Try it/ }).first().click();
      const res = await answer;
      const body = await res.json();
      await page.waitForTimeout(2000);
      const after = await page.evaluate(() => {
        const t = document.body.innerText;
        const card = [...document.querySelectorAll("button")].find((b) => /^YOUR TEAM/i.test(b.innerText.trim()));
        const i = t.indexOf("What-if:");
        return { card: card?.innerText.replace(/\s+/g, " ").trim(), setLine: i < 0 ? null : t.slice(i, t.indexOf("\n", t.indexOf("Reset", i)) + 1).replace(/\n+/g, " ").trim(), openDialogs: document.querySelectorAll("[role=dialog]").length };
      });
      note("reading.txt", [
        "sheet header: " + lines[0],
        "sheet button: " + lines.find((l) => /^Try it/.test(l)),
        "request: POST " + new URL(res.url()).pathname + " " + res.request().postData(),
        "response status: " + res.status(),
        "response page.playoff: " + body.page?.playoff + "; response set: " + JSON.stringify(body.set),
        "open dialogs after the tap: " + after.openDialogs,
        "card after the tap: " + after.card,
        "set line after the tap: " + after.setLine,
      ].join("\n"));
      await page.evaluate(() => window.scrollTo(0, 0));
      await shot("after-try");
    },
  },
  // AT-40 again on 5f26bcb0, with a reading that pairs each Clinch entry of the file with the row the board shows for its team.
  "AT-40-reading": {
    folder: "AT-40",
    prefix: "5f26bcb0-",
    route: "/sim/2026/",
    async run({ page, shot, note }) {
      const reading = await page.evaluate(async () => {
        const sim = await (await fetch("/2026/week-11/sim.json")).json();
        const name = (id) => sim.names[String(id)];
        const rows = [...document.querySelectorAll("button[aria-label]")].filter((b) => /odds of a playoff spot\./.test(b.getAttribute("aria-label")) && !/^\d-\d, ends/.test(b.getAttribute("aria-label")));
        const out = [];
        for (const entry of sim.board) {
          for (const c of entry.clinch.filter((c) => c.goal === "spot")) {
            const team = name(entry.roster_id);
            const row = rows.find((r) => r.getAttribute("aria-label").startsWith(team + ":") || r.getAttribute("aria-label").startsWith(team + ","));
            const shownLines = row ? row.innerText.split("\n").map((l) => l.trim()).filter((l) => /^(Clinches|Out with)/.test(l)) : [];
            const first = c.ways[0];
            out.push("file: " + team + ", goal " + c.goal + ", status " + c.status + ", " + c.ways.length + " ways; first way: own game " + first.game + ", own median " + first.median + ", " + first.others.length + " other results");
            out.push("board row of " + team + ": " + (row ? row.innerText.replace(/\n+/g, " | ") : "no row"));
            out.push("Clinch line under " + team + ": " + (shownLines[0] ?? "none"));
          }
        }
        const others = rows.filter((r) => /Clinches|Out with/.test(r.innerText)).length;
        out.push("rows on the spot Goal with a Clinch line: " + others);
        return out.join("\n");
      });
      note("reading.txt", reading);
      await page.locator("text=League board").first().scrollIntoViewIfNeeded();
      await shot("board");
    },
  },
};
