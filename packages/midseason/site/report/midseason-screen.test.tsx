/**
 * Tests for the midseason report page on the real build of CPC 2026 week 8 in the package fixture.
 * They read what a manager sees: the opener, the three acts with their title pages, the rail, and the chapters of Act I.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { midseason } from "../fixtures/midseason";
import type { Blurb } from "../schema/midseason-types";
import { MidseasonScreen } from "./midseason-screen";

afterEach(cleanup);

const SHELL = {
  title: "CPC Fantasy Football",
  brand: { home: "/", logo: null },
  menu: { items: [{ kind: "home" as const, label: "Home", short: "Home", href: "/" }], weeks: [] },
};

const renderReport = (finale?: React.ReactNode) =>
  render(
    <MidseasonScreen report={midseason} shell={SHELL} pageHref="/midseason/2026/">
      {finale}
    </MidseasonScreen>,
  );

describe("MidseasonScreen", () => {
  it("opens on the title race with All You Need Is Love as the record leader at 11-5", () => {
    renderReport();
    const opener = within(screen.getByRole("region", { name: "The Title Race" }));
    expect(opener.getByRole("heading", { level: 1, name: "The Title Race" })).toBeTruthy();
    expect(opener.getAllByRole("listitem").map((item) => item.textContent)).toEqual([
      "Title odds16.8%London Cooking",
      "Title odds16.3%Bo Girds",
      "Title odds14.5%Maye d'force B with U",
    ]);
    expect(opener.getByText("All You Need Is Love, 11-5, 6th in title odds")).toBeTruthy();
  });

  it("renders the three acts in order, each opened by a title page on the dark hero surface", () => {
    renderReport();
    const titles = screen.getAllByRole("heading", { level: 2 }).map((heading) => heading.textContent);
    expect(titles).toEqual(["How We Got Here", "The Moves", "What Comes Next"]);
    for (const [index, name] of ["Act I: How We Got Here", "Act II: The Moves", "Act III: What Comes Next"].entries()) {
      const page = screen.getByRole("region", { name });
      // The hero sits on the band color in both themes, so the title page is dark in the light theme too.
      expect(page.className).toContain("bg-band");
      // The title page is the first part of its act.
      expect(page.parentElement?.firstElementChild).toBe(page);
      expect(page.parentElement?.id).toBe(midseason.acts[index].key);
    }
  });

  it("links each act from the chapter rail, and the rail sticks to the top", () => {
    renderReport();
    const rail = screen.getByRole("navigation", { name: "Chapters" });
    expect(rail.className).toContain("sticky");
    const links = within(rail).getAllByRole("link");
    expect(links.map((link) => [link.textContent, link.getAttribute("href")])).toEqual([
      ["How We Got Here", "#how-we-got-here"],
      ["The Moves", "#the-moves"],
      ["What Comes Next", "#what-comes-next"],
    ]);
    for (const link of links) expect(document.getElementById(link.getAttribute("href")!.slice(1))).not.toBeNull();
  });

  it("renders the chapters of Act I in order inside the first act", () => {
    renderReport();
    const act = within(document.getElementById("how-we-got-here")!);
    const chapters = act.getAllByRole("heading", { level: 3 }).map((heading) => heading.textContent);
    expect(chapters).toEqual(["The State of the League", "Arcs", "Schedule Luck", "Position Top 10"]);
  });

  it("ends Act II on Quick Hits, which holds the lineup choices and the injury toll", () => {
    // AT-53.
    renderReport();
    const act = document.getElementById("the-moves")!;
    const quick = document.getElementById("quick-hits")!;
    expect(act.lastElementChild).toBe(quick);
    const block = within(quick);
    expect(block.getByRole("heading", { level: 3 }).textContent).toBe("Quick Hits");
    expect(block.getAllByRole("heading", { level: 4 }).map((heading) => heading.textContent)).toEqual([
      "Lineup Choices",
      "The Injury Toll",
    ]);
    expect(block.getByRole("list", { name: "Bench points" })).toBeTruthy();
    expect(block.getByRole("list", { name: "Injury toll" }).firstElementChild!.textContent).toContain("The Blue Tent");
  });

  it("holds the look ahead, then the sim, in Act III", () => {
    // AT-53.
    renderReport(<div data-testid="finale">The sim</div>);
    const act = document.getElementById("what-comes-next")!;
    const look = document.getElementById("look-ahead")!;
    const sim = screen.getByTestId("finale");
    expect(act.contains(look) && act.contains(sim)).toBe(true);
    expect(look.compareDocumentPosition(sim) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("links the opener to the sim with See the sim", () => {
    // AT-54. A tap on the fragment link moves the page to the element with its id, the frame of the sim.
    renderReport(<div data-testid="finale">The sim</div>);
    const opener = within(screen.getByRole("region", { name: "The Title Race" }));
    const link = opener.getByRole("link", { name: "See the sim" });
    const target = document.getElementById(link.getAttribute("href")!.slice(1))!;
    expect(target.contains(screen.getByTestId("finale"))).toBe(true);
    // The rail stays at the top, so the jump leaves its height free above the sim.
    expect(target.className).toContain("scroll-mt-");
  });

  it("shows no See the sim link when the app passes no sim", () => {
    renderReport();
    expect(screen.queryByRole("link", { name: "See the sim" })).toBeNull();
  });

  it("shows the state of the league with each team in standings order", () => {
    renderReport();
    const state = within(document.getElementById("state")!);
    // Each row header holds the place, then the team name, so the sticky team column keeps both on a phone.
    const rows = state.getAllByRole("rowheader").map((cell) => cell.textContent);
    expect(rows).toEqual(rowsOf(0).map((name, index) => `${String(index + 1).padStart(2, "0")} ${name}`));
    expect(rows[0]).toBe("01 All You Need Is Love");
  });

  it("shows the points for and against of each team with 2 decimal places", () => {
    // AT-58. Team scores show 2 places, as Sleeper does, so the 898.0 points against of the last team read 898.00.
    renderReport();
    const state = within(document.getElementById("state")!);
    const last = state.getAllByRole("row").at(-1)!;
    expect(last.textContent).toContain("898.00");
    expect(last.textContent).toContain("700.97");
  });

  it("explains luck in a card above the table with the worked example of All You Need Is Love", () => {
    // AT-8.
    renderReport();
    const chapter = document.getElementById("luck")!;
    const card = within(chapter).getByRole("region", { name: 'What "wins if you played everyone" means' });
    expect(card.textContent).toContain("All You Need Is Love scored 114.33 and outscored 9 of 11 teams");
    expect(card.textContent).toContain("Over 8 weeks it outscored 47 of 88: 4.27 wins");
    expect(card.textContent).toContain("It won 7 real games, 2.73 more than 4.27");
    const table = within(chapter).getByRole("table", { name: "Schedule luck" });
    expect(card.compareDocumentPosition(table) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("never says All-play on the page", () => {
    // AT-8 and AT-59.
    renderReport(<div>The sim</div>);
    expect(document.body.textContent).not.toMatch(/all-play/i);
  });

  it("heads the luck table with plain words and puts a word under each luck number", () => {
    // AT-60.
    renderReport();
    const table = screen.getByRole("table", { name: "Schedule luck" });
    expect(within(table).getAllByRole("columnheader").map((head) => head.textContent)).toEqual([
      "Team",
      "Real wins",
      "Wins if you played everyone",
      "Luck (gap)",
      "PA",
      "Close",
    ]);
    const row = (name: string) => within(table).getByRole("rowheader", { name }).closest("tr")!;
    const luckCell = (name: string) => row(name).querySelector("[data-luck]")!;
    const word = (name: string) => luckCell(name).querySelector("[data-tag]")!;
    expect(luckCell("All You Need Is Love").textContent).toBe("+2.73lucky");
    expect(word("All You Need Is Love").getAttribute("data-tag")).toBe("accent");
    expect(luckCell("The Blue Tent").textContent).toBe("−0.09even");
    expect(word("The Blue Tent").getAttribute("data-tag")).toBe("mute");
    expect(luckCell("Maye d'force B with U").textContent).toBe("+0.91lucky");
    expect(word("Maye d'force B with U").getAttribute("data-tag")).toBe("mute");
    expect(luckCell("Bo Girds").textContent).toBe("−2.18unlucky");
    expect(word("Bo Girds").getAttribute("data-tag")).toBe("accent");
  });

  it("says the count of games of each table in plain words", () => {
    renderReport();
    const chapter = within(document.getElementById("luck")!);
    expect(chapter.getByText(/These count the 8 head-to-head games only\. The median game is out\./)).toBeTruthy();
    expect(chapter.getByText(/These records count all 16 games, 8 head to head and 8 median games, as in the standings\./)).toBeTruthy();
  });

  it("reads the count of median games and the change of each end from the file, and computes neither", () => {
    // The pipeline owns each fact (ADR 0013), so a changed count or change shows on the page as the file says.
    const report = structuredClone(midseason);
    const luck = report.acts.flatMap((act) => act.chapters).find((chapter) => chapter.key === "luck")!;
    if (luck.key !== "luck") throw new Error("no luck chapter");
    luck.facts.median_games = 0;
    luck.facts.swap.best_and_worst[0].best.change = 2;
    render(<MidseasonScreen report={report} shell={SHELL} pageHref="/midseason/2026/" />);
    const chapter = within(document.getElementById("luck")!);
    expect(chapter.getByText(/These records count all 8 head-to-head games, as in the standings\./)).toBeTruthy();
    const bo = within(chapter.getByRole("list", { name: "Schedule swap" })).getAllByRole("listitem")[0];
    expect(bo.textContent).toContain("Best 14-2 on the schedule of Maye d'force B with U+2");
  });

  it("shows the swap as one text row per team with the best and the worst, and no grid and no bar", () => {
    // AT-59.
    renderReport();
    const chapter = document.getElementById("luck")!;
    expect(within(chapter).queryByRole("table", { name: "Schedule swap" })).toBeNull();
    const swap = within(chapter).getByRole("list", { name: "Schedule swap" });
    expect(swap.querySelector("table, svg, [role=meter], [role=progressbar]")).toBeNull();
    const rows = within(swap).getAllByRole("listitem");
    expect(rows).toHaveLength(12);
    const bo = rows[0];
    expect(within(bo).getByRole("heading", { level: 5 }).textContent).toBe("Bo Girds");
    expect(bo.textContent).toContain("Real 9-7");
    expect(bo.textContent).toContain("Best 14-2 on the schedule of Maye d'force B with U+5");
    expect(bo.textContent).toContain("Worst 8-8 on the schedule of To Infinity and Bijan−1");
    const text = (name: string) => rows.find((row) => row.querySelector("h5")?.textContent === name)!.textContent;
    // A tie of 2 schedules reads "or", a tie of more reads "and N others", and no change reads "same".
    expect(text("To Infinity and Bijan")).toContain("Best 10-6 on the schedule of Maye d'force B with U or Teehee+3");
    expect(text("All You Need Is Love")).toContain("Best 11-5 on the schedule of Maye d'force B with Usame");
    expect(text("All You Need Is Love")).toContain("Worst 7-9 on the schedule of London Cooking and 2 others−4");
  });

  it("opens Position top 10 on RB, shows one position, and switches to QB with Josh Allen first", () => {
    renderReport();
    const chapter = within(document.getElementById("top10")!);
    const group = within(chapter.getByRole("group", { name: "Position" }));
    expect(group.getAllByRole("button").map((button) => button.textContent)).toEqual(["QB", "RB", "WR", "TE", "DEF"]);
    expect(group.getByRole("button", { name: "RB" }).getAttribute("aria-pressed")).toBe("true");
    expect(chapter.getAllByRole("list")).toHaveLength(1);
    expect(chapter.getByRole("list", { name: "RB top 10" }).children).toHaveLength(10);
    fireEvent.click(group.getByRole("button", { name: "QB" }));
    const qb = chapter.getByRole("list", { name: "QB top 10" });
    expect(chapter.getAllByRole("list")).toHaveLength(1);
    expect(qb.firstElementChild?.textContent).toContain("Josh Allen");
  });

  it("draws the position switch as text segments with an accent underline that slides to the chosen one", () => {
    // AT-56. The underline is a CSS transition, so the reduced-motion rule of globals.css stops its slide.
    renderReport();
    const group = screen.getByRole("group", { name: "Position" });
    const buttons = within(group).getAllByRole("button");
    for (const button of buttons) {
      expect(button.className).not.toMatch(/(^|\s)(rounded-|border|bg-)/);
      // A native button with no negative tabindex, so Tab reaches each segment and the focus ring of the site shows.
      expect(button.getAttribute("tabindex")).toBeNull();
    }
    const line = group.querySelector<HTMLElement>("[data-underline]")!;
    expect(line.getAttribute("aria-hidden")).toBe("true");
    expect(line.className).toMatch(/(^|\s)h-sp-0(\s|$)/);
    expect(line.className).toMatch(/(^|\s)bg-accent(\s|$)/);
    expect(line.className).toMatch(/(^|\s)transition-\[left\](\s|$)/);
    expect([line.style.left, line.style.width]).toEqual(["20%", "20%"]);
    buttons[4].focus();
    expect(document.activeElement).toBe(buttons[4]);
    fireEvent.click(buttons[4]);
    expect(buttons[4].getAttribute("aria-pressed")).toBe("true");
    expect(line.style.left).toBe("80%");
  });

  it("puts Free agent in the second line of the DEF #3 row, with 77.8 points", () => {
    // AT-55 and AT-58. The Buccaneers are on the wire, so the second line names no manager.
    renderReport();
    const chapter = within(document.getElementById("top10")!);
    fireEvent.click(chapter.getByRole("button", { name: "DEF" }));
    const third = chapter.getByRole("list", { name: "DEF top 10" }).children[2];
    expect(third.textContent).toContain("Tampa Bay Buccaneers");
    expect(within(third as HTMLElement).getByText("Free agent").parentElement!.textContent).toBe("TB · Free agent");
    expect(third.textContent).toContain("77.8");
    expect(third.textContent).not.toContain("77.75");
  });

  it("draws each tag of the report as a plain word, with no fill and no border", () => {
    // AT-55. Open each long list first, so the tags of its hidden rows count too.
    renderReport();
    for (const button of screen.getAllByRole("button", { name: /^Show all/ })) fireEvent.click(button);
    const tags = [...document.querySelectorAll("[data-tag]")];
    expect(tags.map((tag) => tag.textContent)).toEqual(expect.arrayContaining(["Just bad", "Streaming king"]));
    for (const tag of tags) expect(tag.className).not.toMatch(/(^|\s)(bg-|border|rounded)/);
    const tone = (word: string) => tags.find((tag) => tag.textContent === word)!.getAttribute("data-tag");
    expect([tone("Just bad"), tone("Hurt"), tone("Streaming king")]).toEqual([
      "accent",
      "mute",
      "mute",
    ]);
  });

  it("gives each card 8 px corners and draws no full pill", () => {
    // AT-56. rounded-report is the 8 px radius of the report. rounded-sm is the pill radius of the shared look.
    // The report is the page under the top band. The band and its menu belong to the shell of the whole site.
    renderReport();
    for (const button of screen.getAllByRole("button", { name: /^Show all/ })) fireEvent.click(button);
    const report = screen.getByRole("navigation", { name: "Chapters" }).parentElement!;
    const rounded = [...report.querySelectorAll("[class*='rounded']")];
    expect(rounded.length).toBeGreaterThan(0);
    for (const element of rounded) {
      expect(element.className).not.toMatch(/(^|\s)rounded-(pill|full|sm|card)(\s|$)/);
    }
    // No corner is above 8 px, so the hero and the tile of the shared look give way to rounded-report too.
    const corners = new Set(rounded.flatMap((element) => element.className.match(/(?<=(?:^|\s))rounded-\S+/g) ?? []));
    expect([...corners]).toEqual(["rounded-report"]);
    // A sticky table cell takes the card color too, so a cell is no card.
    const cards = [...report.querySelectorAll(".bg-card:not(td, th)")];
    expect(cards.length).toBeGreaterThan(10);
    for (const card of cards) expect(card.className).toMatch(/(^|\s)rounded-report(\s|$)/);
  });

  it("shows the title of each chapter of Acts II and III", () => {
    renderReport();
    for (const act of midseason.acts.slice(1)) {
      const section = within(document.getElementById(act.key)!);
      expect(section.getAllByRole("heading", { level: 3 }).map((heading) => heading.textContent)).toEqual(
        act.chapters.map((chapter) => chapter.title),
      );
    }
  });

  it("shows the prose of each chapter as one paragraph with no roast block", () => {
    // AT-61. The roast is the voice of the paragraph, so the page has no "The roast" heading.
    renderReport();
    expect(screen.queryByText(/the roast/i)).toBeNull();
    // Quick hits has no prose of its own, so each of its parts stands in for it.
    const chapters = midseason.acts
      .flatMap((act) => act.chapters)
      .flatMap((chapter): { key: string; blurb: Blurb | null }[] =>
        chapter.key === "quick-hits" ? chapter.chapters : [chapter],
      );
    expect(chapters).toHaveLength(11);
    for (const chapter of chapters) {
      expect(chapter).not.toHaveProperty("roast");
      if (chapter.blurb === null) continue;
      const text = chapter.blurb.sentences.map((sentence) => sentence.text).join(" ");
      expect(within(document.getElementById(chapter.key)!).getByText(text)).toBeTruthy();
    }
  });

  it("puts the finale that the app passes at the end of the last act", () => {
    renderReport(<div data-testid="finale">The sim</div>);
    const last = document.getElementById("what-comes-next")!;
    expect(last.lastElementChild!.firstElementChild).toBe(screen.getByTestId("finale"));
  });
});

/* The team names of the state of the league, in the order of the file. */
function rowsOf(index: number): string[] {
  const chapter = midseason.acts[0].chapters[index];
  return chapter.key === "state" ? chapter.facts.teams.map((team) => team.name) : [];
}
