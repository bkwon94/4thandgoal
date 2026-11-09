/**
 * Tests for the egg board, rendered from the board fixture that the API tests hold to the real answer.
 * A variant of the fixture gives each other state: a won egg word, and an egg word with no letters.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { EggsError, type Board } from "../lib/api";
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

/* The text of one hero slot of the egg board hero, or null for an absent slot. */
const slot = (name: string) => screen.getByRole("region", { name: "Egg hunt" }).querySelector(`[data-hero-slot="${name}"]`);

/* The label and the number of each tile in the stats of the egg board hero. */
const tiles = () =>
  within(slot("stats") as HTMLElement)
    .getByRole("group", { name: "Egg counts" })
    .querySelectorAll(":scope > div");

describe("The hero of the egg board", () => {
  it("fills the hero slots: the eyebrow, the title, the meta of the gift cards, the grid, and the counts", () => {
    render(<EggBoard board={board} now={NOW} />);
    expect(slot("eyebrow")!.textContent).toBe("Egg hunt");
    expect(slot("title")!.textContent).toBe("The Egg Board");
    expect(slot("title")!.tagName).toBe("H1");
    expect(slot("meta")!.textContent).toBe("$100 in gift cards. Three egg words. First to fill a word wins it.");
    const feature = slot("feature") as HTMLElement;
    expect(within(feature).getByRole("list", { name: "The eggs of each week" })).toBeTruthy();
    expect(feature.textContent).toContain("Drops on a later Tuesday");
    expect(slot("action")).toBeNull();
  });

  it("shows the counts left to find, found, and to drop as three tiles in the stats", () => {
    render(<EggBoard board={board} now={NOW} />);
    expect([...tiles()].map((tile) => [tile.children[0].textContent, tile.children[1].textContent])).toEqual([
      ["Left to find", "1"],
      ["Found", "1"],
      ["To drop", "52"],
    ]);
  });

  it("draws no hero scene", () => {
    render(<EggBoard board={board} now={NOW} />);
    expect(screen.getByRole("region", { name: "Egg hunt" }).querySelectorAll("canvas")).toHaveLength(0);
  });

  it("marks the week of the last drop in the grid", () => {
    render(<EggBoard board={board} now={NOW} />);
    const grid = screen.getByRole("list", { name: "The eggs of each week" });
    const marked = [...within(grid).getAllByRole("listitem")].filter((week) => week.getAttribute("aria-current") === "date");
    expect(marked.map((week) => week.getAttribute("aria-label"))).toEqual(["Week 9: 1 found, 1 out now, 4 to drop"]);
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

describe("The look of the egg board", () => {
  it("puts a plate only in the text slots of the board hero, and shows the grid and the glow only behind the art", () => {
    for (const state of [board, won]) {
      const { container, unmount } = render(<EggBoard board={state} now={NOW} />);
      // The board hero takes the text slots of the shared hero, each with its plate. The texture is hidden, so each
      // plate has the band color on the band color. A word card has no plate.
      const boardHero = screen.getByRole("region", { name: "Egg hunt" });
      const plates = [...container.querySelectorAll(".plate")];
      expect(plates.map((plate) => plate.getAttribute("data-hero-slot"))).toEqual(["eyebrow", "title", "meta"]);
      for (const plate of plates) expect(boardHero.contains(plate)).toBe(true);
      // Each hero hides its full texture, and an oval of the texture sits behind its art.
      const heroes = [...container.querySelectorAll("section")].filter((section) => section.querySelector("[data-hero-art]"));
      expect(heroes.length).toBe(state === won ? 2 : 1);
      for (const hero of heroes) {
        expect(hero.classList.contains("egg-hero")).toBe(true);
        expect(hero.querySelector(".egg-art-ground")).not.toBeNull();
      }
      unmount();
    }
  });

  it("lays each letter row out as one grid column per letter, each tile the full width of its column", () => {
    render(<EggBoard board={board} now={NOW} />);
    const tiles = screen.getAllByTestId("tile");
    const rows = new Set(tiles.map((tile) => tile.parentElement!));
    expect(rows.size).toBeGreaterThan(1);
    for (const row of rows) {
      expect(row.classList.contains("grid")).toBe(true);
      expect(row.style.gridTemplateColumns).toMatch(new RegExp(`^repeat\\(${row.children.length}, minmax\\(0(px)?, var\\(--spacing-letter(-sm)?\\)\\)\\)$`));
      for (const tile of row.children) expect(tile.classList.contains("w-full")).toBe(true);
    }
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
    expect(text).toContain("A tie goes to the earlier letter. No letter repeats in one drop.");
    expect(text).toContain("No egg holds the last letter that a leader needs. If that rules out every letter, the egg holds the next letter by need.");
    expect(text).toContain("CORNERSTONE $50, LANSDALE $30, and EAGLES $20");
    expect(text).toContain("The commissioner places every egg, so the commissioner cannot hunt.");
  });
});

describe("An egg word with no letters", () => {
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

/* The content that the app gives for the time before the first drop: the 404 page of the site. */
const CLOSED = <p>404</p>;
const TITLE = "Egg Board · CPC";

describe("EggBoardScreen", () => {
  it("reads the board from the API at each visit, and names the page the egg board", async () => {
    document.title = "Page Not Found · CPC";
    render(<EggBoardScreen api={fakeEggsApi({ match: false })} closed={CLOSED} title={TITLE} />);
    expect(await screen.findByRole("region", { name: "Latest claims" })).toBeTruthy();
    expect(document.title).toBe(TITLE);
  });

  it("shows nothing while the board loads", () => {
    const { container } = render(<EggBoardScreen api={fakeEggsApi({ match: false })} closed={CLOSED} title={TITLE} />);
    expect(container.innerHTML).toBe("");
  });

  it("shows the closed content and no egg copy before the first drop", async () => {
    document.title = "Page Not Found · CPC";
    const api = fakeEggsApi({ match: false }, {}, empty);
    const { container } = render(<EggBoardScreen api={api} closed={CLOSED} title={TITLE} />);
    await act(async () => {});
    expect(container.innerHTML).toBe("<p>404</p>");
    expect(document.title).toBe("Page Not Found · CPC");
  });

  it("shows the closed content when the board call fails", async () => {
    const api = fakeEggsApi({ match: false }, { board: new EggsError(500, "Server error") });
    const { container } = render(<EggBoardScreen api={api} closed={CLOSED} title={TITLE} />);
    await act(async () => {});
    expect(container.innerHTML).toBe("<p>404</p>");
  });
});
