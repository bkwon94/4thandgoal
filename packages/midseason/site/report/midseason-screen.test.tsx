/**
 * Tests for the midseason report page on the real build of CPC 2026 week 8 in the package fixture.
 * They read what a manager sees: the opener, the three acts with their title pages, the rail, and the chapters of Act I.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { midseason } from "../fixtures/midseason";
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
    expect(chapters).toEqual(["The State of the League", "Arcs", "Schedule Luck", "The Injury Toll", "Position Top 10"]);
  });

  it("shows the state of the league with each team in standings order", () => {
    renderReport();
    const state = within(document.getElementById("state")!);
    // Each row header holds the place, then the team name, so the sticky team column keeps both on a phone.
    const rows = state.getAllByRole("rowheader").map((cell) => cell.textContent);
    expect(rows).toEqual(rowsOf(0).map((name, index) => `${String(index + 1).padStart(2, "0")} ${name}`));
    expect(rows[0]).toBe("01 All You Need Is Love");
  });

  it("explains the All-play record in one plain sentence beside the luck table", () => {
    renderReport();
    const luck = within(document.getElementById("luck")!);
    const sentence = luck.getByText(/All-play wins count each week as a game against every other team/);
    expect(sentence.textContent!.split(". ")[0].split(" ").length).toBeLessThanOrEqual(25);
    expect(luck.getByRole("table", { name: "Schedule swap" })).toBeTruthy();
  });

  it("shows Bo Girds at 14-2 with the schedule that it missed", () => {
    renderReport();
    const missed = within(screen.getByRole("list", { name: "Best schedule missed" }));
    const bo = missed.getAllByRole("listitem").find((item) => item.textContent?.startsWith("Bo Girds"));
    expect(bo?.textContent).toContain("14-2");
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

  it("tags a free agent in Position top 10", () => {
    renderReport();
    const chapter = within(document.getElementById("top10")!);
    fireEvent.click(chapter.getByRole("button", { name: "DEF" }));
    const third = chapter.getByRole("list", { name: "DEF top 10" }).children[2];
    expect(third.textContent).toContain("Free agent");
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

  it("puts the finale that the app passes at the end of the last act", () => {
    renderReport(<div data-testid="finale">The sim</div>);
    const last = document.getElementById("what-comes-next")!;
    expect(last.lastElementChild).toBe(screen.getByTestId("finale"));
  });
});

/* The team names of the state of the league, in the order of the file. */
function rowsOf(index: number): string[] {
  const chapter = midseason.acts[0].chapters[index];
  return chapter.key === "state" ? chapter.facts.teams.map((team) => team.name) : [];
}
