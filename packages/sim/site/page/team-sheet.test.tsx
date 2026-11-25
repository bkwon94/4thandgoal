/**
 * Tests for the team sheet on the real CPC week 11 sim file: it lists each stored way of the Clinch lines of the team for
 * the Goal in full, with the copy of clinch-copy.ts, and shows none for a Seed Goal or a team with no line.
 */
import "@cpc/design/ui/sheet-jsdom";
import { render, screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, spyOn } from "bun:test";
import { weekElevenSim } from "../fixtures/sim";
import { clinchText, clinchWayTexts } from "./clinch-copy";
import { TeamSheet } from "./team-sheet";

beforeEach(() => {
  spyOn(window, "matchMedia").mockImplementation(
    (query: string) =>
      ({
        matches: false,
        media: query,
        addEventListener: () => {},
        removeEventListener: () => {},
      }) as unknown as MediaQueryList,
  );
});

const sim = weekElevenSim;
const linesOf = (id: number) => sim.board.find((row) => row.roster_id === id)!.clinch;
const wayRows = () =>
  within(screen.getByRole("region", { name: "This week" }))
    .getAllByRole("listitem")
    .map((row) => row.textContent);

describe("The team sheet", () => {
  it("lists each way of the spot line of Lil Fridge in full, with every other result named", () => {
    // Roster 3 clinches a spot in 4 ways. The last 2 name 4 results of other teams, which the board cuts to 2.
    const [line] = linesOf(3);
    expect(line.ways).toHaveLength(4);
    render(<TeamSheet sim={sim} team={3} goal="spot" onClose={() => {}} />);
    const texts = clinchWayTexts(sim, line);
    expect(wayRows()).toEqual(
      line.ways.map((way, index) => `${texts[index]}${Math.round(way.chance)}% likely`),
    );
    expect(texts[0]).toBe(clinchText(sim, line));
    expect(clinchText(sim, line)).not.toContain("more result");
    for (const text of texts) expect(text).not.toContain("more result");
    expect(clinchText(sim, { ...line, ways: [line.ways[2]] })).toContain("and 2 more results");
    for (const other of line.ways[2].others) {
      const id = other.kind === "game" ? other.loser : other.roster_id;
      expect(texts[2]).toContain(sim.names[id]);
    }
  });

  it("lists all 8 stored ways of a bye line, and only the line of the Goal of the view", () => {
    // Roster 7 has a spot line and a bye line. The bye view shows only the bye line.
    const bye = linesOf(7).find((line) => line.goal === "bye")!;
    render(<TeamSheet sim={sim} team={7} goal="bye" onClose={() => {}} />);
    const rows = wayRows();
    expect(rows).toHaveLength(8);
    expect(rows[0]).toStartWith("Out of the bye race");
    expect(rows.map((row) => row!.replace(/\d+% likely$/, ""))).toEqual(clinchWayTexts(sim, bye));
  });

  it("shows no Clinch line on a Seed Goal", () => {
    render(<TeamSheet sim={sim} team={7} goal="seed-1" onClose={() => {}} />);
    expect(screen.queryByRole("region", { name: "This week" })).toBeNull();
  });

  it("shows no Clinch line for a team with none this week", () => {
    expect(linesOf(1)).toEqual([]);
    render(<TeamSheet sim={sim} team={1} goal="spot" onClose={() => {}} />);
    expect(screen.getByRole("dialog")).toBeTruthy();
    expect(screen.queryByRole("region", { name: "This week" })).toBeNull();
  });
});
