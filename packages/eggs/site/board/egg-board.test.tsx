/**
 * Tests for the egg board, rendered from the board fixture that the API tests hold to the real answer.
 * A variant of the fixture gives each other state: a won egg word, and the board before the first drop.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import type { Board } from "../lib/api";
import { board, fakeEggsApi } from "../lib/fixtures/eggs-api";
import { EggBoard } from "./egg-board";
import { EggBoardScreen } from "./egg-board-screen";

afterEach(cleanup);

const LIL_FRIDGE = { roster_id: 3, team: "Lil Fridge" };
// One hour after the claim of the fixture.
const NOW = new Date("2026-10-19T13:00:00-04:00");

/* The fixture with EAGLES filled by Lil Fridge, as the API answers after the claim of the last S. */
const won: Board = {
  ...board,
  words: board.words.map((word) =>
    word.word !== "EAGLES"
      ? word
      : {
          ...word,
          winner: LIL_FRIDGE,
          managers: word.managers.map((manager) =>
            manager.roster_id === LIL_FRIDGE.roster_id ? { ...manager, letters: ["E", "A", "G", "L", "E", "S"] } : manager,
          ),
        },
  ),
  latest: [{ ...LIL_FRIDGE, letter: "S", word: "EAGLES", claimed_at: "2026-10-19T12:30:00-04:00" }, ...board.latest],
};

/* The fixture before the first drop: no egg out, no letter, no claim, and every slot still to drop. */
const empty: Board = {
  ...board,
  counts: { left: 0, found: 0, to_drop: 54 },
  weeks: board.weeks.map((week) => ({ ...week, slots: week.slots.map(() => "future" as const) })),
  words: board.words.map((word) => ({ ...word, managers: word.managers.map((manager) => ({ ...manager, letters: [] })) })),
  latest: [],
  last_drop: null,
};

const card = (word: string) => screen.getByRole("region", { name: word });
const rows = (word: string) => within(card(word)).getAllByRole("listitem");

describe("The hero of the egg board", () => {
  it("shows the counts left to find, found, and to drop", () => {
    render(<EggBoard board={board} now={NOW} />);
    const hero = screen.getByRole("region", { name: "Egg hunt" });
    const counts = within(hero)
      .getAllByRole("term")
      .map((term) => [term.textContent, term.nextElementSibling?.textContent]);
    expect(counts).toEqual([
      ["Left to find", "1"],
      ["Found", "1"],
      ["To drop", "52"],
    ]);
  });

  it("shows the 54 slots, one column per week from 9 to 17, each found, out, or still to drop", () => {
    render(<EggBoard board={board} now={NOW} />);
    const grid = screen.getByRole("list", { name: "The eggs of each week" });
    const weeks = within(grid).getAllByRole("listitem");
    expect(weeks.map((week) => week.getAttribute("aria-label"))).toEqual([
      "Week 9: 1 found, 1 out now, 4 to drop",
      ...[10, 11, 12, 13, 14, 15, 16, 17].map((week) => `Week ${week}: 6 to drop`),
    ]);
    expect(grid.querySelectorAll('[data-slot="found"]')).toHaveLength(1);
    expect(grid.querySelectorAll('[data-slot="out"]')).toHaveLength(1);
    expect(grid.querySelectorAll('[data-slot="future"]')).toHaveLength(52);
  });
});

describe("The egg word cards", () => {
  it("shows one card per egg word, CORNERSTONE first, each with its gift card", () => {
    render(<EggBoard board={board} now={NOW} />);
    expect(screen.getAllByRole("heading", { level: 2 }).slice(0, 3).map((heading) => heading.textContent)).toEqual([
      "CORNERSTONE",
      "LANSDALE",
      "EAGLES",
    ]);
    expect(card("CORNERSTONE").textContent).toContain("$50 gift card");
    expect(card("LANSDALE").textContent).toContain("$30 gift card");
    expect(card("EAGLES").textContent).toContain("$20 gift card");
  });

  it("names the leader and lists the top 5 with the tiles of each manager", () => {
    render(<EggBoard board={board} now={NOW} />);
    expect(card("CORNERSTONE").textContent).toContain("Lil Fridge leads with 1 of 11.");
    const top = rows("CORNERSTONE");
    expect(top).toHaveLength(5);
    expect(top[0].textContent).toContain("Lil Fridge");
    expect(top[0].textContent).toContain("Leads");
    expect(top[0].textContent).toContain("1/11");
    // The C fills the first slot of CORNERSTONE, and the other ten slots stay open.
    expect(within(top[0]).getAllByTestId("tile").map((tile) => tile.textContent)).toEqual(["C", ...Array(10).fill("")]);
  });

  it("shows all 11 managers after a tap on Show all 11, and the top 5 after a second tap", () => {
    render(<EggBoard board={board} now={NOW} />);
    fireEvent.click(within(card("CORNERSTONE")).getByRole("button", { name: "Show all 11" }));
    expect(rows("CORNERSTONE")).toHaveLength(11);
    fireEvent.click(within(card("CORNERSTONE")).getByRole("button", { name: "Show the top 5" }));
    expect(rows("CORNERSTONE")).toHaveLength(5);
  });

  it("turns a won egg word into a hero card with a WON stamp and its winner", () => {
    render(<EggBoard board={won} now={NOW} />);
    const eagles = card("EAGLES");
    expect(eagles.textContent).toContain("WON");
    expect(eagles.textContent).toContain("Lil Fridge won it.");
    expect(eagles.textContent).toContain("The $20 gift card is theirs.");
    expect(within(eagles).queryByRole("button")).toBeNull();
    expect(card("CORNERSTONE").textContent).not.toContain("WON");
  });
});

describe("Latest claims", () => {
  it("shows the manager, the letter, and the egg word of each claim, newest first", () => {
    render(<EggBoard board={won} now={NOW} />);
    const feed = within(screen.getByRole("region", { name: "Latest claims" })).getAllByRole("listitem");
    expect(feed.map((row) => row.querySelector("[data-claim]")!.textContent)).toEqual([
      "Lil Fridge claimed an S and filled EAGLES.",
      "Lil Fridge claimed a C for CORNERSTONE.",
    ]);
    expect(feed.map((row) => row.querySelector("time")!.textContent)).toEqual(["30M", "1H"]);
  });

  it("says that no manager has claimed an egg yet", () => {
    render(<EggBoard board={{ ...board, latest: [] }} now={NOW} />);
    expect(screen.getByRole("region", { name: "Latest claims" }).textContent).toContain("No claims yet. 1 egg is out there.");
  });
});

describe("How the hunt works", () => {
  it("ends the page with the drop each Tuesday, the claim, the letter rule, the gift cards, and the commissioner", () => {
    const { container } = render(<EggBoard board={board} now={NOW} />);
    const sections = container.querySelectorAll("section");
    const last = sections[sections.length - 1];
    expect(last).toBe(screen.getByRole("region", { name: "How the hunt works" }));
    const text = last.textContent!;
    expect(text).toContain("6 new eggs drop each Tuesday from week 9 through week 17.");
    expect(text).toContain("The first manager to claim an egg gets its letter.");
    expect(text).toContain("the letter that the most managers still need");
    expect(text).toContain("CORNERSTONE $50, LANSDALE $30, and EAGLES $20");
    expect(text).toContain("The commissioner places every egg, so the commissioner cannot hunt.");
  });
});

describe("The egg board before the first drop", () => {
  it("shows the three egg words with no letters and 54 eggs to drop", () => {
    render(<EggBoard board={empty} now={NOW} />);
    const hero = screen.getByRole("region", { name: "Egg hunt" });
    expect(within(hero).getByText("To drop").nextElementSibling!.textContent).toBe("54");
    for (const word of ["CORNERSTONE", "LANSDALE", "EAGLES"]) {
      expect(card(word).textContent).toContain("No letters yet. The race is open.");
      expect(within(card(word)).queryAllByRole("listitem")).toHaveLength(0);
    }
    expect(screen.getByRole("region", { name: "Latest claims" }).textContent).toContain("No claims yet.");
  });
});

describe("The copy of the egg board", () => {
  it("names no rival and no commissioner by name in any state", () => {
    for (const state of [board, won, empty]) {
      const { container, unmount } = render(<EggBoard board={state} now={NOW} />);
      expect(container.textContent).not.toMatch(/rival/i);
      expect(container.textContent).not.toMatch(/Brian/);
      unmount();
    }
  });
});

describe("EggBoardScreen", () => {
  it("reads the board from the API at each visit", async () => {
    render(<EggBoardScreen api={fakeEggsApi({ match: false })} />);
    expect(await screen.findByRole("region", { name: "Latest claims" })).toBeTruthy();
  });
});
