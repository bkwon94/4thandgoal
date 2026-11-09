/**
 * Tests for the egg board, rendered from the board fixture that the API tests hold to the real answer.
 * A variant of the fixture gives each other state: a won egg word, an egg word with no letters, a close race, and a tie.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { EggsError, type Board } from "../lib/api";
import { board, boardWith, fakeEggsApi } from "../lib/fixtures/eggs-api";
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

/* The board of AT-22: Lil Fridge holds five letters of EAGLES and two of CORNERSTONE, and no manager holds a letter of LANSDALE. */
const close = boardWith({ EAGLES: { 3: ["E", "A", "G", "L", "S"] }, CORNERSTONE: { 3: ["C", "O"] } });

const tabNames = () => screen.getAllByRole("tab").map((tab) => tab.textContent);
const selectedTab = () => screen.getAllByRole("tab").find((tab) => tab.getAttribute("aria-selected") === "true");
const panel = () => screen.getByRole("tabpanel");
const panelRows = () => within(panel()).queryAllByRole("listitem");
/* The state of each letter of the giant word of the shown slide: lit, outline, or won. */
const giant = () =>
  [...within(panel()).getByRole("heading", { level: 2 }).querySelectorAll("[data-letter]")].map((letter) => letter.getAttribute("data-letter"));

describe("The egg word slider", () => {
  it("shows a tab per egg word in the fixed order, each with the count of its leader", () => {
    render(<EggBoard board={boardWith({ CORNERSTONE: { 3: ["C", "O"] }, LANSDALE: { 4: ["L"] } })} now={NOW} />);
    expect(screen.getByRole("tablist", { name: "Egg words" })).toBeTruthy();
    expect(tabNames()).toEqual(["CORNERSTONE 2/11", "LANSDALE 1/8", "EAGLES 0/6"]);
  });

  it("names a won egg word Won in its tab", () => {
    render(<EggBoard board={won} now={NOW} />);
    expect(tabNames()).toEqual(["CORNERSTONE 1/11", "LANSDALE 0/8", "EAGLES · Won"]);
  });

  it("opens on the open word whose leader holds the largest share, and keeps the tabs in the fixed order", () => {
    render(<EggBoard board={close} now={NOW} />);
    expect(selectedTab()!.textContent).toBe("EAGLES 5/6");
    expect(panel().getAttribute("aria-labelledby")).toBe(selectedTab()!.id);
    expect(within(panel()).getByRole("heading", { level: 2, name: "EAGLES" })).toBeTruthy();
    expect(tabNames()).toEqual(["CORNERSTONE 2/11", "LANSDALE 0/8", "EAGLES 5/6"]);
  });

  it("puts the open words closest first and a won word last", () => {
    render(<EggBoard board={won} now={NOW} />);
    const slides = screen.getAllByRole("tabpanel", { hidden: true });
    expect(slides.map((slide) => within(slide).getByRole("heading", { level: 2, hidden: true }).getAttribute("aria-label"))).toEqual([
      "CORNERSTONE",
      "LANSDALE",
      "EAGLES",
    ]);
    expect(selectedTab()!.textContent).toBe("CORNERSTONE 1/11");
  });

  it("lights the letters of the leader in the giant word and outlines the rest", () => {
    render(<EggBoard board={close} now={NOW} />);
    // The leader holds E, A, G, L, and S, so only the second E of EAGLES stays an outline.
    expect(giant()).toEqual(["lit", "lit", "lit", "lit", "outline", "lit"]);
  });

  it("names the leader and lists the top 5 with the tiles of each manager", () => {
    render(<EggBoard board={boardWith({ CORNERSTONE: { 3: ["C", "O", "R", "N"], 1: ["E"], 2: ["S"], 4: ["T"], 5: ["O"], 7: ["R"] } })} now={NOW} />);
    expect(panel().textContent).toContain("Lil Fridge leads with 4 of 11.");
    expect(panel().textContent).toContain("$50 gift card");
    const top = panelRows();
    expect(top).toHaveLength(5);
    expect(top.map((row) => row.querySelector("[data-team]")!.textContent)).toEqual([
      "Lil Fridge",
      "Brock ‘N’ Roll",
      "All You Need Is Love",
      "Pukancun on 3",
      "London Cooking",
    ]);
    expect(top[0].textContent).toContain("Leads");
    expect(top[0].textContent).toContain("4/11");
    // C, O, R, and N fill the first four slots of CORNERSTONE, and the other seven slots stay open.
    expect(within(top[0]).getAllByTestId("tile").map((tile) => tile.textContent)).toEqual(["C", "O", "R", "N", ...Array(7).fill("")]);
  });

  it("shows all 11 managers after a tap on Show all 11, and the top 5 after a second tap", () => {
    render(<EggBoard board={board} now={NOW} />);
    fireEvent.click(within(panel()).getByRole("button", { name: "Show all 11" }));
    expect(panelRows()).toHaveLength(11);
    fireEvent.click(within(panel()).getByRole("button", { name: "Show the top 5" }));
    expect(panelRows()).toHaveLength(5);
  });

  it("says that two managers tie, in the order of the rosters", () => {
    render(<EggBoard board={boardWith({ CORNERSTONE: { 3: ["C", "O"], 1: ["R", "N"] } })} now={NOW} />);
    expect(panel().textContent).toContain("Brock ‘N’ Roll and Lil Fridge tie with 2 of 11.");
    // The giant word lights the letters of the first manager of the ranking.
    expect(giant()).toEqual(["outline", "outline", "lit", "lit", ...Array(7).fill("outline")]);
  });

  it("says that three managers tie, in the order of the rosters", () => {
    render(<EggBoard board={boardWith({ LANSDALE: { 4: ["L"], 2: ["A"], 9: ["N"] } })} now={NOW} />);
    expect(panel().textContent).toContain("All You Need Is Love, Pukancun on 3, and Maye d'force B with U tie with 1 of 8.");
  });

  it("turns a won word red with every letter lit in red, its winner, and its gift card", () => {
    render(<EggBoard board={won} now={NOW} />);
    fireEvent.click(screen.getByRole("tab", { name: "EAGLES · Won" }));
    expect(giant()).toEqual(Array(6).fill("won"));
    expect(panel().textContent).toContain("WON");
    expect(panel().textContent).toContain("Lil Fridge won it.");
    expect(panel().textContent).toContain("The $20 gift card is theirs.");
    expect(within(panel()).queryByRole("button")).toBeNull();
  });

  it("opens on CORNERSTONE with every letter outlined before any claim", () => {
    render(<EggBoard board={empty} now={NOW} />);
    expect(selectedTab()!.textContent).toBe("CORNERSTONE 0/11");
    expect(giant()).toEqual(Array(11).fill("outline"));
    expect(panel().textContent).toContain("No letters yet. The race is open.");
    expect(panelRows()).toHaveLength(0);
  });

  it("moves between the tabs with the arrow keys, Home, and End, with a roving tabindex", () => {
    render(<EggBoard board={close} now={NOW} />);
    const [cornerstone, lansdale, eagles] = screen.getAllByRole("tab");
    fireEvent.click(cornerstone);
    expect(selectedTab()).toBe(cornerstone);
    fireEvent.keyDown(cornerstone, { key: "ArrowRight" });
    expect(selectedTab()).toBe(lansdale);
    expect(document.activeElement).toBe(lansdale);
    expect(within(panel()).getByRole("heading", { level: 2, name: "LANSDALE" })).toBeTruthy();
    fireEvent.keyDown(lansdale, { key: "ArrowRight" });
    expect(document.activeElement).toBe(eagles);
    expect(panel().getAttribute("aria-labelledby")).toBe(eagles.id);
    // The keys wrap at each end of the row.
    fireEvent.keyDown(eagles, { key: "ArrowRight" });
    expect(document.activeElement).toBe(cornerstone);
    fireEvent.keyDown(cornerstone, { key: "ArrowLeft" });
    expect(document.activeElement).toBe(eagles);
    fireEvent.keyDown(eagles, { key: "Home" });
    expect(document.activeElement).toBe(cornerstone);
    fireEvent.keyDown(cornerstone, { key: "End" });
    expect(document.activeElement).toBe(eagles);
    // Only the selected tab sits in the tab order.
    expect(screen.getAllByRole("tab").map((tab) => tab.tabIndex)).toEqual([-1, -1, 0]);
    expect(eagles.getAttribute("aria-controls")).toBe(panel().id);
  });

  it("puts the red accent only on a won slide, and an open slide on the dark hero ground", () => {
    render(<EggBoard board={won} now={NOW} />);
    const frame = () => panel().closest("section")!;
    for (const name of ["CORNERSTONE 1/11", "LANSDALE 0/8"]) {
      fireEvent.click(screen.getByRole("tab", { name }));
      expect(frame().classList.contains("bg-band")).toBe(true);
      expect(frame().classList.contains("bg-accent")).toBe(false);
    }
    fireEvent.click(screen.getByRole("tab", { name: "EAGLES · Won" }));
    expect(frame().classList.contains("bg-accent")).toBe(true);
  });
});

describe("The motion of the egg word slider", () => {
  /* The box that takes the swipe: it holds the frame of the slides. */
  const swipeBox = () => panel().closest("[data-swipe]") as HTMLElement;
  /* A swipe on the slider from one point to another, as a finger on a phone. */
  const swipe = (dx: number, dy: number) => {
    const start = { clientX: 200, clientY: 300, isPrimary: true, pointerType: "touch" };
    fireEvent.pointerDown(swipeBox(), start);
    fireEvent.pointerUp(swipeBox(), { ...start, clientX: start.clientX + dx, clientY: start.clientY + dy });
  };

  it("moves to the next slide on a swipe to the left, and back on a swipe to the right", () => {
    // The board of AT-22 opens on EAGLES, then CORNERSTONE, then LANSDALE.
    render(<EggBoard board={close} now={NOW} />);
    expect(selectedTab()!.textContent).toBe("EAGLES 5/6");
    swipe(-120, 10);
    expect(selectedTab()!.textContent).toBe("CORNERSTONE 2/11");
    expect(within(panel()).getByRole("heading", { level: 2, name: "CORNERSTONE" })).toBeTruthy();
    swipe(120, -10);
    expect(selectedTab()!.textContent).toBe("EAGLES 5/6");
  });

  it("keeps the slide on a vertical swipe and lets the page scroll, and keeps it on a short drag", () => {
    render(<EggBoard board={close} now={NOW} />);
    swipe(-60, -160);
    expect(selectedTab()!.textContent).toBe("EAGLES 5/6");
    swipe(-20, 0);
    expect(selectedTab()!.textContent).toBe("EAGLES 5/6");
    // The browser cancels the pointer when it scrolls the page, so the end of that touch moves no slide.
    fireEvent.pointerDown(swipeBox(), { clientX: 200, clientY: 300, isPrimary: true });
    fireEvent.pointerCancel(swipeBox(), { clientX: 200, clientY: 300, isPrimary: true });
    fireEvent.pointerUp(swipeBox(), { clientX: 60, clientY: 300, isPrimary: true });
    expect(selectedTab()!.textContent).toBe("EAGLES 5/6");
    // The slider allows only a vertical pan, so the browser keeps the page scroll and leaves the side swipe to the slider.
    expect(swipeBox().classList.contains("touch-pan-y")).toBe(true);
  });

  /* The slide of an egg word, shown or not. */
  const slide = (word: string) => document.getElementById(`egg-slide-${word}`)!;
  /* The roll of the giant word of a slide: in, out-up, out-down, wait-up, or wait-down. */
  const roll = (word: string) => slide(word).querySelector("h2")!.getAttribute("data-roll");

  it("rolls the slides on a move: the shown slide leaves to the side and its word rolls out letter by letter", () => {
    render(<EggBoard board={close} now={NOW} />);
    // Before a move, the shown word rests in place and the others wait below.
    expect(roll("EAGLES")).toBe("in");
    expect(roll("CORNERSTONE")).toBe("wait-down");
    fireEvent.click(screen.getByRole("tab", { name: "CORNERSTONE 2/11" }));
    expect([slide("EAGLES"), slide("CORNERSTONE"), slide("LANSDALE")].map((each) => each.getAttribute("data-rel"))).toEqual(["-1", "0", "1"]);
    // Only the shown slide is in the accessibility tree. The neighbors roll away blurred, out of reach of a tap.
    expect(slide("EAGLES").getAttribute("aria-hidden")).toBe("true");
    expect(slide("EAGLES").hasAttribute("inert")).toBe(true);
    expect(slide("CORNERSTONE").hasAttribute("inert")).toBe(false);
    // LANSDALE wraps from one side to the other behind the frame, so it jumps with no roll.
    expect(slide("LANSDALE").getAttribute("data-jump")).toBe("true");
    expect(slide("CORNERSTONE").getAttribute("data-jump")).toBe("false");
    expect(roll("EAGLES")).toBe("out-up");
    expect(roll("CORNERSTONE")).toBe("in");
    expect(roll("LANSDALE")).toBe("wait-down");
    // Each letter knows its place in the word, so the letters roll in one after another.
    const letters = [...slide("CORNERSTONE").querySelectorAll<HTMLElement>("[data-letter]")];
    expect(letters.map((letter) => letter.style.getPropertyValue("--k"))).toEqual([..."CORNERSTONE"].map((_, index) => String(index)));
    // A swipe back rolls the other way.
    swipe(120, 0);
    expect(roll("EAGLES")).toBe("in");
    expect(roll("CORNERSTONE")).toBe("out-down");
    expect(roll("LANSDALE")).toBe("wait-up");
    // The motion runs for its full time.
    const slider = panel().closest<HTMLElement>("[data-slider]")!;
    expect(slider.style.getPropertyValue("--es-dur")).toBe("0.75s");
    expect(slider.style.getPropertyValue("--es-on")).toBe("1");
  });

  it("washes the frame red on a move to a won slide", () => {
    render(<EggBoard board={won} now={NOW} />);
    const frame = () => panel().closest("section")!;
    expect(frame().classList.contains("egg-wash")).toBe(true);
    fireEvent.click(screen.getByRole("tab", { name: "EAGLES · Won" }));
    expect(frame().classList.contains("egg-wash")).toBe(true);
    expect(frame().classList.contains("bg-accent")).toBe(true);
  });
});

describe("The look of the egg board", () => {
  it("puts a plate only in the text slots of the board hero, and shows the grid and the glow only behind the art", () => {
    for (const state of [board, won]) {
      const { container, unmount } = render(<EggBoard board={state} now={NOW} />);
      // The board hero takes the text slots of the shared hero, each with its plate. The texture is hidden, so each
      // plate has the band color on the band color. A slide has no plate.
      const boardHero = screen.getByRole("region", { name: "Egg hunt" });
      const plates = [...container.querySelectorAll(".plate")];
      expect(plates.map((plate) => plate.getAttribute("data-hero-slot"))).toEqual(["eyebrow", "title", "meta"]);
      for (const plate of plates) expect(boardHero.contains(plate)).toBe(true);
      // The board hero and the frame of the slider each hide the full texture. An oval of the texture sits behind the
      // grid of the board hero only, so each slide keeps its text on a flat color.
      const heroes = [...container.querySelectorAll("section")].filter((section) => section.querySelector("[data-hero-art]"));
      expect(heroes).toHaveLength(2);
      for (const hero of heroes) expect(hero.classList.contains("egg-hero")).toBe(true);
      expect(boardHero.querySelector(".egg-art-ground")).not.toBeNull();
      expect(heroes[1].querySelector(".egg-art-ground")).toBeNull();
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
    for (const name of ["CORNERSTONE 0/11", "LANSDALE 0/8", "EAGLES 0/6"]) {
      fireEvent.click(screen.getByRole("tab", { name }));
      expect(panel().textContent).toContain("No letters yet. The race is open.");
      expect(panelRows()).toHaveLength(0);
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
