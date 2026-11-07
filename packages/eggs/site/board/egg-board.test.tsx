/**
 * Tests for the plain egg board, rendered from the board fixture that the API tests hold to the real answer.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { board, fakeEggsApi } from "../lib/fixtures/eggs-api";
import { EggBoard } from "./egg-board";
import { EggBoardScreen } from "./egg-board-screen";

afterEach(cleanup);

describe("EggBoard", () => {
  it("lists each manager in each egg word with the letters of the manager", () => {
    render(<EggBoard board={board} />);
    for (const word of ["CORNERSTONE", "LANSDALE", "EAGLES"]) {
      const card = screen.getByRole("region", { name: new RegExp(word) });
      expect(within(card).getAllByRole("listitem")).toHaveLength(board.managers.length);
    }
    const cornerstone = screen.getByRole("region", { name: /CORNERSTONE/ });
    expect(within(cornerstone).getByText("Lil Fridge").closest("li")!.textContent).toContain("C");
    expect(screen.getByRole("region", { name: /CORNERSTONE/ }).textContent).toContain("$50");
  });

  it("shows the counts left to find, found, and to drop", () => {
    render(<EggBoard board={board} />);
    expect(screen.getByText("1 left to find · 1 found · 52 to drop")).toBeTruthy();
  });

  it("lists the latest claims with the manager, the letter, and the egg word", () => {
    render(<EggBoard board={board} />);
    const feed = screen.getByRole("region", { name: "Latest claims" });
    expect(within(feed).getAllByRole("listitem").map((item) => item.textContent)).toEqual([
      "Lil Fridge · C · CORNERSTONE",
    ]);
  });
});

describe("EggBoardScreen", () => {
  it("reads the board from the API at each visit", async () => {
    render(<EggBoardScreen api={fakeEggsApi({ match: false })} />);
    expect(await screen.findByRole("region", { name: "Latest claims" })).toBeTruthy();
  });
});
