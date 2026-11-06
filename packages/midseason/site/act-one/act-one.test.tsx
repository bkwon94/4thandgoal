/**
 * Tests for the chapters of Act I on the real build of CPC 2026 week 8 in the package fixture.
 * They read what a manager sees: the arcs and the Position top 10.
 */
import { cleanup, fireEvent, render, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { sleeperHeadshot } from "@cpc/league/images";
import { midseason } from "../fixtures/midseason";
import { MidseasonScreen } from "../report/midseason-screen";
import type { ArcsChapter, MidseasonChapter } from "../schema/midseason-types";
import { Arcs } from "./arcs";

afterEach(cleanup);

const SHELL = {
  title: "CPC Fantasy Football",
  brand: { home: "/", logo: null },
  menu: { items: [{ kind: "home" as const, label: "Home", short: "Home", href: "/" }], weeks: [] },
};

const renderReport = () =>
  render(<MidseasonScreen report={midseason} shell={SHELL} pageHref="/midseason/2026/" />);

/* The chapter of the fixture with the key `key`. */
function chapterOf<K extends MidseasonChapter["key"]>(key: K): Extract<MidseasonChapter, { key: K }> {
  const found = midseason.acts.flatMap((act) => act.chapters).find((chapter) => chapter.key === key);
  if (found === undefined) throw new Error(`The fixture has no ${key} chapter`);
  return found as Extract<MidseasonChapter, { key: K }>;
}

const chapterEl = (key: string) => within(document.getElementById(key)!);

describe("arcs", () => {
  it("gives a row only to a team with an arc", () => {
    renderReport();
    const { teams } = chapterOf("arcs").facts;
    const withArc = teams.filter((team) => team.arcs.length > 0);
    expect(withArc.length).toBeGreaterThan(0);
    expect(withArc.length).toBeLessThan(teams.length);
    const rows = [...chapterEl("arcs").getByRole("list", { name: "Arcs" }).children];
    expect(rows.map((row) => row.firstElementChild!.textContent)).toEqual(withArc.map((team) => team.name));
    expect(document.getElementById("arcs")!.textContent).not.toMatch(/no arc/i);
  });

  it("says in one line that no team has an arc when no team has one", () => {
    const chapter = chapterOf("arcs");
    const none: ArcsChapter = {
      ...chapter,
      facts: { teams: chapter.facts.teams.map((team) => ({ ...team, arcs: [] })) },
    };
    render(<Arcs chapter={none} />);
    const page = within(document.getElementById("arcs")!);
    expect(page.queryByRole("list", { name: "Arcs" })).toBeNull();
    expect(page.getByText("No team has an arc yet.")).toBeTruthy();
  });
});

describe("position top 10", () => {
  it("gives each row a small headshot of the player, with alt text, a fixed size, and lazy load", () => {
    renderReport();
    const rb = chapterOf("top10").facts.positions.find((board) => board.position === "RB")!;
    const rows = [...chapterEl("top10").getByRole("list", { name: "RB top 10" }).children] as HTMLElement[];
    expect(rows).toHaveLength(rb.players.length);
    for (const [index, row] of rows.entries()) {
      const player = rb.players[index];
      const img = within(row).getByRole("img", { name: player.name });
      expect(img.getAttribute("src")).toBe(sleeperHeadshot(player.player_id));
      expect(img.getAttribute("loading")).toBe("lazy");
      expect(img.parentElement!.className).toMatch(/(^|\s)size-avatar(\s|$)/);
    }
  });

  it("gives each DEF row a frame of fixed size with the initials of the team, as the helper has no team logo", () => {
    renderReport();
    const chapter = chapterEl("top10");
    fireEvent.click(chapter.getByRole("button", { name: "DEF" }));
    const def = chapterOf("top10").facts.positions.find((board) => board.position === "DEF")!;
    const rows = [...chapter.getByRole("list", { name: "DEF top 10" }).children] as HTMLElement[];
    for (const [index, row] of rows.entries()) {
      expect(row.querySelector("img")).toBeNull();
      const frame = within(row).getByRole("img", { name: def.players[index].name });
      expect(frame.className).toMatch(/(^|\s)size-avatar(\s|$)/);
    }
  });
});
