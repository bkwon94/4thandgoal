/**
 * The site evidence of playoff-paths, round b: AT-44, AT-46, AT-47, AT-48, AT-49, AT-50, AT-51, and AT-54, in Playwright
 * WebKit at four sizes and two themes. Run: node run.mjs [AT-44 ...], with serve.mjs on 4291 (cpc) and 4292 (playoffs).
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { EV, SITE, PLAYOFFS, SIZES, THEMES, BASE_STORAGE, browser, context, sleeper, shot, overlapCheck, line, save, netText, counts, waitLive } from "./lib.mjs";

const want = process.argv.slice(2);
const run = (id) => want.length === 0 || want.includes(id);
const NAMES = ["Teez Nuts", "Puka Deez"];
const dir = (id) => join(EV, id);
const settle = async (page) => { await page.waitForLoadState("networkidle").catch(() => {}); await page.waitForTimeout(800); };

/* AT-44, AT-47, and AT-54: the week page, The Race, then the rankings page in the same tab, with the real Sleeper answer. */
if (run("AT-44") || run("AT-47") || run("AT-54")) {
  const r44 = [], o44 = [], n44 = [], r47 = [], o47 = [], n47 = [], all = [];
  for (const size of SIZES) for (const theme of THEMES) {
    const tag = size.name + "-" + theme;
    const { ctx, net, errors } = await context(size, theme);
    const page = await ctx.newPage();
    await page.goto(SITE + "/2026/week-11/");
    const live = await waitLive(page);
    await settle(page);
    const week = await counts(page, NAMES);
    const cache = await page.evaluate(() => { const k = Object.keys(sessionStorage).find((x) => x.startsWith("live-names:")); return k ? k + " roster 5 = " + JSON.stringify(JSON.parse(sessionStorage.getItem(k)).teams["5"]) : "none"; });
    await shot(page, dir("AT-44"), "week-" + tag);
    o44.push(line("week-" + tag, await overlapCheck(page)));
    const beforeRace = sleeper(net).length;
    // The Race: the tap on the link of the Sim tile, as a reader opens it from the week page.
    await page.locator('#sim a[href="/sim/2026/"]').first().scrollIntoViewIfNeeded();
    await page.locator('#sim a[href="/sim/2026/"]').first().click();
    await page.waitForURL((u) => u.pathname.startsWith("/sim/2026"));
    await settle(page);
    await page.waitForTimeout(1500);
    const race = await counts(page, NAMES);
    await shot(page, dir("AT-44"), "race-" + tag);
    o44.push(line("race-" + tag, await overlapCheck(page)));
    const raceCalls = sleeper(net).length - beforeRace;
    r44.push(tag + ": live cache after " + live + " ms (" + cache + "); week-11 page " + JSON.stringify(week) + "; The Race " + JSON.stringify(race) + "; Sleeper requests on the week page " + beforeRace + ", on The Race " + raceCalls);
    // AT-47: the rankings page in the same tab, within 5 minutes of the first call.
    const sinceFirst = Date.now();
    const before47 = sleeper(net).length;
    await page.goto(SITE + "/rankings/", { waitUntil: "load" });
    const atLoad = await counts(page, NAMES);
    await settle(page);
    await page.waitForTimeout(1500);
    const after = await counts(page, NAMES);
    const calls47 = sleeper(net).slice(before47);
    await shot(page, dir("AT-47"), tag);
    o47.push(line(tag, await overlapCheck(page)));
    r47.push(tag + ": rankings at the load event " + JSON.stringify(atLoad) + ", after 2.3 s " + JSON.stringify(after) + "; new Sleeper requests on the rankings page " + calls47.length + "; the cache key holds from the week page");
    n44.push("== " + tag + " ==\n" + netText(net) + (errors.length ? "\nerrors:\n" + errors.join("\n") : "\nerrors: none"));
    n47.push("== " + tag + " (rankings page only) ==\n" + (calls47.length ? netText(calls47) : "(no Sleeper request)") );
    all.push(...net);
    await ctx.close();
  }
  save(dir("AT-44"), "readings.txt", r44.join("\n"));
  save(dir("AT-44"), "overlap.txt", o44.join("\n"));
  save(dir("AT-44"), "network.txt", "Each request of the week page and The Race to a host other than the local export, per size and theme. One fresh context each.\n\n" + n44.join("\n\n"));
  save(dir("AT-47"), "readings.txt", r47.join("\n"));
  save(dir("AT-47"), "overlap.txt", o47.join("\n"));
  save(dir("AT-47"), "network.txt", n47.join("\n\n"));
  // AT-54: each distinct Sleeper URL and each outside host of the AT-44 log.
  const urls = [...new Set(all.filter((e) => e.event === "request").map((e) => e.url))].sort();
  const hosts = [...new Set(urls.map((u) => new URL(u).host))].sort();
  const sl = urls.filter((u) => u.includes("api.sleeper.app"));
  save(dir("AT-54"), "network.txt", "From the network log of AT-44 (evidence/AT-44/network.txt), 8 contexts.\n\nEach distinct Sleeper API URL:\n" + sl.join("\n") +
    "\n\nSleeper API URLs with matchups, projections, players, stats, or state: " + sl.filter((u) => /matchup|projection|player|stats|state/.test(u)).length +
    "\n\nEach outside host of the log:\n" + hosts.join("\n") + "\n\nEach distinct outside URL:\n" + urls.join("\n"));
}

/* AT-44, the week 10 page: its published files hold "Puka Deez...". The real Sleeper answer, with no route. */
if (want.includes("AT-44-week10")) {
  const r = [], o = [], n = [];
  for (const size of SIZES) for (const theme of THEMES) {
    const tag = size.name + "-" + theme;
    const { ctx, net, errors } = await context(size, theme);
    const page = await ctx.newPage();
    await page.goto(SITE + "/2026/week-10/");
    const live = await waitLive(page);
    await settle(page);
    await page.waitForTimeout(1500);
    const week10 = await counts(page, NAMES);
    await shot(page, dir("AT-44"), "week10-" + tag);
    o.push(line("week10-" + tag, await overlapCheck(page)));
    r.push(tag + ": live cache after " + live + " ms; week-10 page " + JSON.stringify(week10) + "; Sleeper requests " + sleeper(net).length + "; errors: " + (errors.length ? errors.join(" | ") : "none"));
    n.push("== " + tag + " ==\n" + netText(sleeper(net).length ? net.filter((e) => e.url.includes("api.sleeper.app")) : []));
    await ctx.close();
  }
  save(dir("AT-44"), "week10-readings.txt", "The week 10 page /2026/week-10/ with the real Sleeper answer, one fresh context per size and theme.\n" + r.join("\n"));
  save(dir("AT-44"), "week10-overlap.txt", o.join("\n"));
  save(dir("AT-44"), "week10-network.txt", "Each Sleeper request, response, and failed request of the week 10 page, per size and theme.\n\n" + n.join("\n\n"));
}

/* AT-46: both Sleeper calls blocked. The week 11 page, then the week 10 page, whose published files hold the old name. */
if (run("AT-46")) {
  const r = [], o = [], n = [];
  for (const size of SIZES) for (const theme of THEMES) {
    const tag = size.name + "-" + theme;
    const { ctx, net, errors } = await context(size, theme);
    await ctx.route("https://api.sleeper.app/**", (route) => route.abort("blockedbyclient"));
    const page = await ctx.newPage();
    const lines = [];
    for (const [name, path] of [["week-11", "/2026/week-11/"], ["week-10", "/2026/week-10/"]]) {
      await page.goto(SITE + path);
      await settle(page);
      await page.waitForTimeout(3500);
      const c = await counts(page, [...NAMES, "error", "Error", "went wrong", "try again"]);
      await shot(page, dir("AT-46"), name + "-" + tag);
      o.push(line(name + "-" + tag, await overlapCheck(page)));
      lines.push(name + " " + JSON.stringify(c));
    }
    r.push(tag + ": " + lines.join("; ") + "; page errors and console errors: " + (errors.length ? errors.join(" | ") : "none"));
    n.push("== " + tag + " ==\n" + netText(net));
    await ctx.close();
  }
  save(dir("AT-46"), "readings.txt", r.join("\n"));
  save(dir("AT-46"), "overlap.txt", o.join("\n"));
  save(dir("AT-46"), "network.txt", "Each request to a host other than the local export. The route aborts each request to https://api.sleeper.app/.\n\n" + n.join("\n\n"));
}

/* AT-48: the midseason report with the Sleeper calls open. */
if (run("AT-48")) {
  const sim = JSON.parse(readFileSync(new URL("../../../../clients/cpc/published/2026/week-11/sim.json", "file:///Users/brian.kwon/repos/4thandgoal/.claude/worktrees/playoff-paths/.scratch/playoff-paths/evidence/site-set-b/"), "utf8"));
  const teamNames = [...new Set([...Object.values(sim.names), "Puka Deez..."])];
  const html = readFileSync("/private/tmp/claude-503/-Users-brian-kwon-repos-4thandgoal/bbcae1c9-0e99-49c1-be38-1aefbd218ea6/scratchpad/out-cpc/midseason/2026/index.html", "utf8");
  const published = Object.fromEntries(teamNames.map((t) => [t, html.split(t.replace(/&/g, "&amp;").replace(/'/g, "&#x27;")).length - 1]));
  const r = ["The count of each team name in the exported HTML of /midseason/2026/: " + JSON.stringify(published)], o = [], n = [];
  for (const size of SIZES) for (const theme of THEMES) {
    const tag = size.name + "-" + theme;
    const { ctx, net, errors } = await context(size, theme);
    const page = await ctx.newPage();
    await page.goto(SITE + "/midseason/2026/");
    await settle(page);
    await page.waitForTimeout(4000);
    const shown = await counts(page, teamNames);
    const openText = await page.evaluate(() => document.body.innerText);
    await shot(page, dir("AT-48"), tag);
    o.push(line(tag, await overlapCheck(page)));
    // The same page in a second fresh context with each Sleeper request aborted, so the visible text with no live name
    // is beside the visible text with the Sleeper calls open.
    const blocked = await context(size, theme);
    await blocked.ctx.route("https://api.sleeper.app/**", (route) => route.abort("blockedbyclient"));
    const bpage = await blocked.ctx.newPage();
    await bpage.goto(SITE + "/midseason/2026/");
    await settle(bpage);
    await bpage.waitForTimeout(4000);
    const blockedShown = await counts(bpage, teamNames);
    const blockedText = await bpage.evaluate(() => document.body.innerText);
    await blocked.ctx.close();
    r.push(tag + ": Sleeper requests " + sleeper(net).length + "; visible count of each team name " + JSON.stringify(shown) + "; with Sleeper blocked " + JSON.stringify(blockedShown) + "; visible text equal with Sleeper open and blocked: " + (openText === blockedText) + " (" + openText.length + " chars); errors: " + (errors.length ? errors.join(" | ") : "none"));
    n.push("== " + tag + " ==\n" + netText(net));
    await ctx.close();
  }
  save(dir("AT-48"), "readings.txt", r.join("\n"));
  save(dir("AT-48"), "overlap.txt", o.join("\n"));
  save(dir("AT-48"), "network.txt", "Each request to a host other than the local export. No route blocks Sleeper.\n\n" + n.join("\n\n"));
}

/* AT-49: a fresh browser with Your team set. The Announcement of The Race is not seen yet. */
if (run("AT-49")) {
  const r = [], o = [];
  const storage = { "cpc.your-team": "6", "cpc.tour-seen": "1", "cpc.announcement.season-sim-2026": "seen" };
  for (const size of SIZES) for (const theme of THEMES) {
    const tag = size.name + "-" + theme;
    const { ctx, errors } = await context(size, theme, storage);
    const page = await ctx.newPage();
    await page.goto(SITE + "/");
    const opened = await page.getByText("The Race is on").first().waitFor({ state: "visible", timeout: 8000 }).then(() => true).catch(() => false);
    await page.waitForTimeout(1200);
    const vis = async (t) => page.getByText(t, { exact: true }).first().isVisible().catch(() => false);
    // The eyebrow shows in capitals by CSS, so the reading takes the text content of the open modal layer too.
    const layerText = await page.locator('[aria-modal="true"]').evaluateAll((ls) => ls.filter((l) => l.checkVisibility()).map((l) => l.textContent.replace(/\s+/g, " ").trim()).join(" | "));
    const first = { "New: The Race": layerText.includes("New: The Race"), "The Race is on": await vis("The Race is on"), "Open The Race": await vis("Open The Race"), "Not now": await vis("Not now"), layerText: layerText.slice(0, 400) };
    await page.screenshot({ path: join(dir("AT-49"), "first-" + tag + ".png"), fullPage: false });
    o.push(line("first-" + tag, await overlapCheck(page)));
    await page.getByRole("button", { name: "Not now" }).first().click();
    await page.waitForTimeout(1000);
    const key = await page.evaluate(() => localStorage.getItem("cpc.announcement.the-race-2026"));
    await page.reload();
    await settle(page);
    await page.waitForTimeout(2500);
    const second = { "New: The Race": (await page.evaluate(() => document.body.textContent)).includes("New: The Race") && await page.getByText("New: The Race").first().isVisible().catch(() => false), "The Race is on": await vis("The Race is on"), "Open The Race": await vis("Open The Race"), modalLayers: await page.locator('[aria-modal="true"]').evaluateAll((ls) => ls.filter((l) => l.checkVisibility()).length) };
    await shot(page, dir("AT-49"), "second-" + tag);
    o.push(line("second-" + tag, await overlapCheck(page)));
    r.push(tag + ": first load, Announcement visible " + opened + ", texts " + JSON.stringify(first) + "; after Not now the key cpc.announcement.the-race-2026 = " + key + "; second load " + JSON.stringify(second) + "; errors: " + (errors.length ? errors.join(" | ") : "none"));
    await ctx.close();
  }
  save(dir("AT-49"), "readings.txt", r.join("\n"));
  save(dir("AT-49"), "overlap.txt", o.join("\n"));
}

/* AT-50: the tile after Standings on the week 11 page. */
if (run("AT-50")) {
  const r = [], o = [];
  for (const size of SIZES) for (const theme of THEMES) {
    const tag = size.name + "-" + theme;
    const { ctx } = await context(size, theme);
    const page = await ctx.newPage();
    await page.goto(SITE + "/2026/week-11/");
    await settle(page);
    const tiles = await page.evaluate(() => {
      const heading = document.getElementById("standings-heading");
      let section = heading;
      while (section && section.parentElement && !section.parentElement.querySelector(":scope > #sim, :scope > [id=sim]")) section = section.parentElement;
      const list = section?.parentElement ? [...section.parentElement.children] : [];
      const order = list.map((el) => el.id || el.querySelector("[id]")?.id || el.tagName.toLowerCase());
      const i = list.indexOf(section);
      const next = list[i + 1];
      return { order, after: order[i], next: next ? { id: next.id, heading: next.querySelector("h2,h3")?.textContent?.trim(), text: next.innerText.trim().replace(/\s+/g, " ").slice(0, 160), links: [...next.querySelectorAll("a")].map((a) => a.getAttribute("href")) } : null };
    });
    await shot(page, dir("AT-50"), tag);
    o.push(line(tag, await overlapCheck(page)));
    r.push(tag + ": " + JSON.stringify(tiles));
    await ctx.close();
  }
  save(dir("AT-50"), "readings.txt", r.join("\n"));
  save(dir("AT-50"), "overlap.txt", o.join("\n"));
}

/* AT-51: the sim page of the playoff fixture, and the same counts on the week 11 export beside it. */
if (run("AT-51")) {
  const r = [], o = [];
  const probe = async (page) => ({
    bracketRegion: await page.getByRole("region", { name: "Bracket" }).count(),
    goalSwitch: await page.getByLabel("Goal", { exact: true }).count(),
    leagueBoard: await page.getByRole("group", { name: /^League board/ }).count(),
    heading: (await page.locator("h1").first().textContent().catch(() => ""))?.trim(),
  });
  for (const size of SIZES) for (const theme of THEMES) {
    const tag = size.name + "-" + theme;
    const { ctx } = await context(size, theme);
    const page = await ctx.newPage();
    await page.goto(PLAYOFFS + "/sim/2026/");
    await settle(page);
    const fixture = await probe(page);
    await shot(page, dir("AT-51"), tag);
    o.push(line(tag, await overlapCheck(page)));
    await page.goto(SITE + "/sim/2026/");
    await settle(page);
    const week11 = await probe(page);
    r.push(tag + ": playoff fixture export " + JSON.stringify(fixture) + "; week 11 export, for comparison " + JSON.stringify(week11));
    await ctx.close();
  }
  save(dir("AT-51"), "readings.txt", r.join("\n"));
  save(dir("AT-51"), "overlap.txt", o.join("\n"));
}

await browser.close();
console.log("done");
