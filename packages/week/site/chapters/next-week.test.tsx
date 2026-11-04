/**
 * Tests for next week. They render the week 6 JSON and read the label, the teams, the records, the tags, and the bye lines.
 * They check what a reader sees, not the class names.
 */
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { firstSentence, week6 } from "../fixtures/week-page";
import { NextWeek } from "./next-week";

afterEach(() => {
  cleanup();
});

/* The published week 6 JSON has no byes, so the bye tests add them to three sides of two games.
   One side has a key starter and a player who is not, one has an empty list, and the rest have none. */
const gamesWithByes = week6.next.map((game, i) => {
  if (i === 0) {
    const byes = [
      { player_id: "4984", name: "Josh Allen", position: "QB", key: true },
      { player_id: "7525", name: "Dalton Kincaid", position: "TE", key: false },
    ];
    return { ...game, a: { ...game.a, byes }, b: { ...game.b, byes: [] } };
  }
  if (i === 2) {
    return { ...game, a: { ...game.a, byes: [{ player_id: "8183", name: "Jayden Daniels", position: "QB", key: true }] } };
  }
  return game;
});

function renderNext(games = week6.next) {
  return render(<NextWeek week={week6.week} games={games} avatars={week6.avatars} blurb={week6.blurbs.next_week} />);
}

describe("NextWeek", () => {
  it("names the week after the page's week", () => {
    renderNext();
    expect(screen.getByText("Next Week · Week 7")).toBeTruthy();
  });

  it("shows both teams of each game with the records", () => {
    renderNext();
    expect(screen.getByText("Lil Fridge")).toBeTruthy();
    expect(screen.getByText("10-2")).toBeTruthy();
    expect(screen.getByText("Return of T Mac")).toBeTruthy();
    expect(screen.getAllByText("vs").length).toBe(week6.next.length);
  });

  it("tags the Must Watch games and shows the reason", () => {
    renderNext();
    expect(screen.getAllByText("Must Watch").length).toBe(2);
    expect(screen.getByText("1st vs 7th, near the playoff cut")).toBeTruthy();
  });

  it("puts the Must Watch tag above the first team of its card", () => {
    renderNext();
    const game = week6.next.find((g) => g.must_watch);
    expect(game).toBeDefined();
    const tag = screen.getAllByText("Must Watch")[0];
    const firstTeam = screen.getAllByText(game!.a.name)[0];
    expect(tag.compareDocumentPosition(firstTeam) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("shows the blurb", () => {
    renderNext();
    expect(screen.getByText(firstSentence(week6.blurbs.next_week), { exact: false })).toBeTruthy();
  });

  it("labels each side with players on bye and none with an empty list", () => {
    renderNext(gamesWithByes);
    const sidesWithByes = gamesWithByes.flatMap((game) => [game.a, game.b]).filter((team) => team.byes?.length);
    expect(sidesWithByes.length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("On bye").length).toBe(sidesWithByes.length);
    expect(screen.queryAllByText("Bye").length).toBe(0);
  });

  it("puts a middle dot between two players on bye on one side", () => {
    renderNext(gamesWithByes);
    const line = screen.getByText("Josh Allen").parentElement?.parentElement;
    expect(line?.textContent).toContain("Josh Allen QB · Dalton Kincaid TE");
    expect(line?.textContent).not.toContain(",");
  });

  it("still shows the Must Watch tag and the reason when the second team has players on bye", () => {
    const games = week6.next.map((game) =>
      game.must_watch
        ? { ...game, b: { ...game.b, byes: [{ player_id: "8183", name: "Jayden Daniels", position: "QB", key: true }] } }
        : game,
    );
    renderNext(games);
    expect(screen.getAllByText("Must Watch").length).toBe(2);
    expect(screen.getByText("1st vs 7th, near the playoff cut")).toBeTruthy();
    expect(screen.getAllByText("On bye").length).toBe(2);
  });

  it("lists each player on bye with his position and bolds the key starter", () => {
    renderNext(gamesWithByes);
    const byes = gamesWithByes.flatMap((game) => [game.a, game.b]).flatMap((team) => team.byes ?? []);
    for (const player of byes) {
      const name = screen.getByText(player.name);
      expect(name.parentElement?.textContent).toContain(`${player.name} ${player.position}`);
      expect(name.tagName === "STRONG").toBe(player.key);
    }
    expect(byes.some((player) => player.key)).toBe(true);
    expect(byes.some((player) => !player.key)).toBe(true);
  });

  it("shows no bye label for a side with an empty list or no list", () => {
    renderNext(gamesWithByes);
    const sides = gamesWithByes.flatMap((game) => [game.a, game.b]);
    expect(sides.some((team) => team.byes?.length === 0)).toBe(true);
    expect(sides.some((team) => team.byes === undefined)).toBe(true);
    expect(screen.getAllByText("On bye").length).toBe(sides.filter((team) => team.byes?.length).length);
  });
});
