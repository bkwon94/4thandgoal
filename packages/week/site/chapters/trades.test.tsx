/**
 * Tests for the trades chapter. They render the week 6 JSON and read the teams, the players, and the For tag.
 * A copy of the JSON with no trades checks that the chapter is left out.
 */
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { week6 } from "../fixtures/week-page";
import { Trades } from "./trades";

afterEach(() => {
  cleanup();
});

describe("Trades", () => {
  it("shows the label and both teams of the first trade", () => {
    render(<Trades trades={week6.trades} avatars={week6.avatars} />);
    expect(screen.getByText("Trades")).toBeTruthy();
    expect(screen.getAllByText("Pukancun on 3").length).toBe(2);
    expect(screen.getAllByText("Amon-Ra Dawg Your Team").length).toBe(3);
  });

  it("shows each player a side gets", () => {
    render(<Trades trades={week6.trades} avatars={week6.avatars} />);
    for (const name of ["Jacory Croskey-Merritt", "David Montgomery", "Omarion Hampton", "Tony Pollard", "Lamar Jackson"]) {
      expect(screen.getByText(name)).toBeTruthy();
    }
  });

  it("puts one For tag and two Gets labels on each two-side trade", () => {
    render(<Trades trades={week6.trades} avatars={week6.avatars} />);
    expect(screen.getAllByText("For").length).toBe(week6.trades.length);
    expect(screen.getAllByText("Gets").length).toBe(week6.trades.length * 2);
  });

  it("shows picks as plain lines and gives a three-side trade no For tag", () => {
    const [a, b] = week6.trades[0].sides;
    const third = { ...a, players: [], picks: ["2027 1st round"] };
    render(<Trades trades={[{ sides: [a, b, third] }]} avatars={week6.avatars} />);
    expect(screen.getByText("2027 1st round")).toBeTruthy();
    expect(screen.queryByText("For")).toBeNull();
  });

  it("gives a four-side trade no For tag and shows all four teams", () => {
    const [a, b] = week6.trades[0].sides;
    const c = { ...a, team: { ...a.team, roster_id: 901, name: "Third Team" }, players: [], picks: ["2027 2nd round"] };
    const d = { ...b, team: { ...b.team, roster_id: 902, name: "Fourth Team" }, players: [], picks: ["2028 1st round"] };
    render(<Trades trades={[{ sides: [a, b, c, d] }]} avatars={week6.avatars} />);
    expect(screen.queryByText("For")).toBeNull();
    for (const name of [a.team.name, b.team.name, "Third Team", "Fourth Team"]) {
      expect(screen.getAllByText(name).length).toBeGreaterThan(0);
    }
  });

  it("leaves the chapter out when the week has no trades", () => {
    const copy = { ...week6, trades: [] };
    const { container } = render(<Trades trades={copy.trades} avatars={copy.avatars} />);
    expect(container.innerHTML).toBe("");
    expect(screen.queryByText("Trades")).toBeNull();
  });

  it("links a side's team name to its manager page only when the season has the managers file", () => {
    const { rerender } = render(<Trades trades={week6.trades} avatars={week6.avatars} managersHref="/2026/managers/" />);
    expect(screen.getAllByRole("link", { name: "Pukancun on 3" })[0].getAttribute("href")).toBe("/2026/managers/4/");
    rerender(<Trades trades={week6.trades} avatars={week6.avatars} />);
    expect(screen.queryByRole("link", { name: "Pukancun on 3" })).toBeNull();
  });
});
