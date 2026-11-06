/**
 * Tests for the chapters of Act II on the real build of CPC 2026 week 8 in the package fixture.
 * They read what a manager sees: the steals and busts, the waivers, the trade cards, the lineups, and the record book.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { midseason } from "../fixtures/midseason";
import { MidseasonScreen } from "../report/midseason-screen";
import type { MidseasonChapter, QuickHitsChapter } from "../schema/midseason-types";

afterEach(cleanup);

const SHELL = {
  title: "CPC Fantasy Football",
  brand: { home: "/", logo: null },
  menu: { items: [{ kind: "home" as const, label: "Home", short: "Home", href: "/" }], weeks: [] },
};

const renderReport = () =>
  render(<MidseasonScreen report={midseason} shell={SHELL} pageHref="/midseason/2026/" />);

/* A chapter with its own prose: each chapter of an act but Quick hits, and each part of Quick hits. */
type ProseChapter = Exclude<MidseasonChapter, { key: "quick-hits" }> | QuickHitsChapter["chapters"][number];

const proseChapters = (): ProseChapter[] =>
  midseason.acts
    .flatMap((act) => act.chapters)
    .flatMap((chapter): ProseChapter[] => (chapter.key === "quick-hits" ? chapter.chapters : [chapter]));

/* The chapter of the fixture with the key `key`, or a part of Quick hits. */
function chapterOf<K extends ProseChapter["key"]>(key: K): Extract<ProseChapter, { key: K }> {
  const found = proseChapters().find((chapter) => chapter.key === key);
  if (found === undefined) throw new Error(`The fixture has no ${key} chapter`);
  return found as Extract<ProseChapter, { key: K }>;
}

const chapterEl = (key: string) => within(document.getElementById(key)!);

describe("draft steals and busts", () => {
  it("lists the top 5 steals with the auction price", () => {
    renderReport();
    const { steals } = chapterOf("draft").facts;
    const rows = chapterEl("draft").getByRole("list", { name: "Steals" }).children;
    expect(rows).toHaveLength(steals.length);
    expect(rows[0].textContent).toContain(steals[0].name);
    expect(rows[0].textContent).toContain(`$${steals[0].cost}`);
    expect(document.getElementById("draft")!.textContent).not.toMatch(/one that got away/i);
  });

  it("tags each bust hurt or just bad", () => {
    renderReport();
    const { busts } = chapterOf("draft").facts;
    const rows = chapterEl("draft").getByRole("list", { name: "Busts" }).children;
    expect(rows).toHaveLength(busts.length);
    for (const [index, bust] of busts.entries()) {
      expect(rows[index].textContent).toContain(bust.name);
      if (bust.tag !== null) expect(rows[index].textContent).toContain(bust.tag === "hurt" ? "Hurt" : "Just bad");
    }
  });
});

describe("waiver hits and misses", () => {
  it("lists the hits by Points over the line and the misses with their bids", () => {
    renderReport();
    const { hits, misses } = chapterOf("waivers").facts;
    const chapter = chapterEl("waivers");
    const hitRows = chapter.getByRole("list", { name: "Hits" }).children;
    expect(hitRows).toHaveLength(hits.length);
    expect(hitRows[0].textContent).toContain(hits[0].player);
    expect(hitRows[0].textContent).toContain(`+${hits[0].points_over_line!.toFixed(1)}`);
    const missRows = chapter.getByRole("list", { name: "Misses" }).children;
    expect(missRows).toHaveLength(misses.length);
    expect(missRows[0].textContent).toContain(`$${misses[0].bid}`);
  });

  it("has no one that got away line on a hit", () => {
    renderReport();
    expect(document.getElementById("waivers")!.textContent).not.toMatch(/one that got away/i);
  });

  it("names the outbid claims with the margin, and the streaming king first", () => {
    renderReport();
    const { outbid, streamers } = chapterOf("waivers").facts;
    const chapter = chapterEl("waivers");
    const rows = chapter.getByRole("list", { name: "Outbid" }).children;
    expect(rows).toHaveLength(outbid.length);
    expect(rows[0].textContent).toContain(`by $${outbid[0].margin}`);
    const streams = chapter.getByRole("list", { name: "Streamers" });
    expect(streams.children).toHaveLength(Math.min(5, streamers.length));
    expect(streams.firstElementChild!.textContent).toContain(streamers[0].team);
    expect(streams.firstElementChild!.textContent).toContain("Streaming king");
  });
});

describe("the trade report card", () => {
  it("shows the top 3 trades as full cards, each with the record of each team since the trade", () => {
    renderReport();
    const trades = chapterOf("trades").facts.trades;
    const cards = chapterEl("trades").getAllByRole("article");
    expect(cards).toHaveLength(3);
    for (const [index, card] of cards.entries()) {
      const trade = trades[index];
      expect(card.textContent).toContain(trade.result);
      for (const side of trade.sides) {
        const since = within(card).getByText(`${side.team}`, { selector: "[data-team]" }).closest("[data-side]")!;
        const { wins, losses, ties } = side.since;
        const text = ties > 0 ? `${wins}-${losses}-${ties} since` : `${wins}-${losses} since`;
        expect(since.textContent).toContain(text);
      }
    }
  });

  it("tags each player who was out in the first week after his trade as hurt on arrival", () => {
    renderReport();
    const trades = chapterOf("trades").facts.trades;
    const hurt = trades.flatMap((trade) => trade.sides.flatMap((side) => side.got.filter((p) => p.hurt_on_arrival)));
    expect(hurt.length).toBeGreaterThan(0);
    const chapter = chapterEl("trades");
    fireEvent.click(chapter.getByRole("button", { name: /^Show all/ }));
    const tags = chapter.getAllByText("Hurt on arrival");
    expect(tags).toHaveLength(hurt.length);
    expect(tags.map((tag) => tag.parentElement!.textContent)).toEqual(
      hurt.map((player) => expect.stringContaining(player.player)),
    );
  });

  it("sits third of the five chapters of Act II", () => {
    renderReport();
    const act = within(document.getElementById("the-moves")!);
    expect(act.getAllByRole("heading", { level: 3 }).map((heading) => heading.textContent)).toEqual([
      "Draft Steals and Busts",
      "Waiver Hits and Misses",
      "The Trade Report Card",
      "The Record Book",
      "Quick Hits",
    ]);
  });

  it("shows 5 of the other trades, and the rest after Show all", () => {
    renderReport();
    const rest = chapterOf("trades").facts.trades.length - 3;
    expect(rest).toBeGreaterThan(5);
    const chapter = chapterEl("trades");
    const list = chapter.getByRole("list", { name: "Every other trade" });
    expect(list.children).toHaveLength(5);
    const button = chapter.getByRole("button", { name: `Show all ${rest}` });
    expect(button.getAttribute("aria-expanded")).toBe("false");
    fireEvent.click(button);
    expect(list.children).toHaveLength(rest);
    expect(chapter.getByRole("button", { name: "Show fewer" }).getAttribute("aria-expanded")).toBe("true");
  });
});

describe("lineup choices", () => {
  it("shows 5 teams by Bench points, then all of them after Show all", () => {
    renderReport();
    const { teams } = chapterOf("lineup").facts;
    const chapter = chapterEl("lineup");
    const list = chapter.getByRole("list", { name: "Bench points" });
    expect(list.children).toHaveLength(5);
    expect(list.firstElementChild!.textContent).toContain(teams[0].name);
    fireEvent.click(chapter.getByRole("button", { name: `Show all ${teams.length}` }));
    expect(list.children).toHaveLength(teams.length);
  });

  it("names the week 2 loss of London Cooking by 1.67 that its best lineup would have won", () => {
    renderReport();
    const chapter = chapterEl("lineup");
    fireEvent.click(chapter.getByRole("button", { name: /^Show all/ }));
    const row = [...chapter.getByRole("list", { name: "Bench points" }).children].find((item) =>
      item.textContent!.includes("London Cooking"),
    )!;
    expect(row.textContent).toMatch(/Week 2: lost to .+ by 1\.67/);
  });
});

describe("the record book", () => {
  it("shows the high, the low, the biggest margin, and the closest game", () => {
    renderReport();
    const { high, low, biggest_margin, closest } = chapterOf("records").facts;
    const items = [...chapterEl("records").getByRole("list", { name: "Records" }).children].map((item) => item.textContent);
    expect(items).toHaveLength(4);
    expect(items[0]).toContain(high.team);
    expect(items[1]).toContain(low.team);
    expect(items[2]).toContain(biggest_margin.winner);
    expect(items[3]).toContain(closest.loser);
  });

  it("shows Heartbreak and Beatdown once each, on their game inside the record book", () => {
    renderReport();
    const { awards } = chapterOf("records").facts;
    const book = within(chapterEl("records").getByRole("list", { name: "Records" }));
    for (const title of ["Heartbreak of the year", "Beatdown of the year"]) {
      expect(screen.getAllByText(title)).toHaveLength(1);
      expect(book.getByText(title)).toBeTruthy();
    }
    const listed = within(chapterEl("records").getByRole("list", { name: "Awards" })).getAllByRole("listitem");
    expect(listed.map((item) => item.querySelector("h5")!.textContent)).toEqual(
      awards.filter((award) => !award.in_record_book).map((award) => award.title),
    );
    for (const award of awards) expect(screen.getAllByText(award.fact)).toHaveLength(1);
  });
});
