/**
 * Tests for the analyzer result. The API fixture document is the one input, and each test reads the screen.
 * They check what a reader sees, not the class names.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { analyzeResponse as fixtureJson, analyzeResponseThree as threeJson, analyzeResponseTradeA as tradeA } from "../lib/fixtures/api";
import type { AnalyzeResponse, Fairness, Lean } from "../lib/analyze-types";
import AnalyzeResult from "./analyze-result";

const fixture = fixtureJson as AnalyzeResponse;
const three = threeJson as AnalyzeResponse;
/* An old document has no to and no from, so the strip drops both from every player. */
const stripMoves = (doc: AnalyzeResponse): AnalyzeResponse => ({
  ...doc,
  trade: {
    ...doc.trade,
    sides: doc.trade.sides.map((side) => ({
      ...side,
      gives: side.gives.map(({ to: _to, ...player }) => player),
      gets: side.gets.map(({ from: _from, ...player }) => player),
    })),
  },
});
/* The swap card is the chapter under The Trade heading. */
const tradeChapter = () => screen.getByRole("heading", { level: 2, name: "The Trade" }).closest("section") as HTMLElement;
/* The move tag of a chip, found by its full text. The word and the team sit in two spans, so a plain text match misses it. */
const byTag = (text: string) => (_: string, el: Element | null) =>
  el?.tagName === "SPAN" && el.textContent === text && el.querySelector("span") !== null;
/* Every tag the three-side fixture can show, so a test can check that none shows. */
const THREE_TAGS = three.trade.sides.flatMap((side) => [`To ${side.team}`, `From ${side.team}`]);
const withLean = (lean: Lean): AnalyzeResponse => ({ ...fixture, lean });
const withAsker = (asker: number): AnalyzeResponse => ({ ...fixture, trade: { ...fixture.trade, asker } });
/* The first Bullet of the asker in the fixture. */
const ANALYSIS = fixture.sides[0].bullets[0].text;
const LEANS = ["Send it", "Lean yes", "Gut call", "Lean no", "Pass"] as const;
/* A single letter on its own is a grade. A letter in an initial such as "A.J." is a name, so the scan skips it. */
const LETTER = /(?<![\w.])[A-F](?![\w.])/;
const NOTE = "This week's player values are not out yet, so both sides start even.";
/* The card of one side, found by its label. */
const sideCard = (label: string) => screen.getByText(label).closest("section") as HTMLElement;
/* The fixture reasons repeat breakdown text, so the fairness tests use reasons that show only once on the page. */
const MY_REASON = "My side gets the better lineup.";
const THEIR_REASON = "Their side moves up in the standings.";
const withFairness = (state: Fairness["state"], gives_more: number | null = null): AnalyzeResponse => ({
  ...fixture,
  fairness: {
    state,
    gives_more,
    sides: [
      { roster_id: 4, reason: MY_REASON },
      { roster_id: 12, reason: THEIR_REASON },
    ],
  } as Fairness,
});

afterEach(() => {
  cleanup();
});

/* The filled hero slots of a hero, in the order of the markup. */
const slotsOf = (hero: HTMLElement) => [...hero.querySelectorAll("[data-hero-slot]")].map((slot) => slot.getAttribute("data-hero-slot"));
const slotText = (hero: HTMLElement, slot: string) => hero.querySelector(`[data-hero-slot=${slot}]`)?.textContent;

describe("AnalyzeResult", () => {
  it.each(LEANS)("shows the Lean %s as the word, with the Case under it", (lean) => {
    render(<AnalyzeResult doc={withLean(lean)} />);
    expect(screen.getByText("The read for Pukancun on 3")).toBeTruthy();
    expect(screen.getByText(lean)).toBeTruthy();
    expect(screen.getByText(fixture.case)).toBeTruthy();
  });

  it("puts the Lean above the swap card and the sides", () => {
    render(<AnalyzeResult doc={fixture} />);
    const decision = screen.getByText("Lean yes");
    const trade = screen.getByRole("heading", { level: 2, name: "The Trade" });
    const side = screen.getByText("Pukancun on 3 · Your Side");
    expect(decision.compareDocumentPosition(trade) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(trade.compareDocumentPosition(side) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("opens the read chapter with the Lean word as a level-two heading", () => {
    render(<AnalyzeResult doc={fixture} />);
    const heading = screen.getByRole("heading", { level: 2, name: "Lean yes" });
    const trade = screen.getByRole("heading", { level: 2, name: "The Trade" });
    expect(heading.compareDocumentPosition(trade) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  /* The read fills the hero slots, and the hero ends at the fairness block with no empty stats or action. */
  it("puts the read in the slots: the side, the Lean, the Case, then the fairness block last", () => {
    render(<AnalyzeResult doc={fixture} />);
    const hero = screen.getByRole("region", { name: "The Read" });
    expect(slotsOf(hero)).toEqual(["eyebrow", "title", "meta", "feature"]);
    expect(slotText(hero, "eyebrow")).toBe("The read for Pukancun on 3");
    expect(slotText(hero, "title")).toBe("Lean yes");
    expect(slotText(hero, "meta")).toBe(fixture.case);
    const feature = hero.querySelector("[data-hero-slot=feature]") as HTMLElement;
    expect(within(feature).getByText("Fairness")).toBeTruthy();
    expect(hero.querySelector("[data-hero-rule]")).toBeNull();
  });

  it("keeps the static grid, the glow, and the brackets in the read hero, and draws no scene (AT-35, AT-44)", () => {
    render(<AnalyzeResult doc={tradeA} />);
    const hero = screen.getByRole("region", { name: "The Read" });
    expect(document.querySelectorAll("canvas[data-hero-scene]")).toHaveLength(0);
    // The static hero: the texture layer holds the grid and the glow, and the four brackets sit in the corners.
    expect(hero.querySelectorAll("[data-hero-art='texture']")).toHaveLength(1);
    expect(hero.querySelectorAll("[data-hero-art='bracket']")).toHaveLength(4);
  });

  it("leaves out the feature slot when the document has no fairness block and no note", () => {
    render(<AnalyzeResult doc={{ ...fixture, fairness: undefined }} />);
    const hero = screen.getByRole("region", { name: "The Read" });
    expect(slotsOf(hero)).toEqual(["eyebrow", "title", "meta"]);
  });

  it("shows no letter grade anywhere in the result", () => {
    for (const lean of LEANS) {
      const { container } = render(<AnalyzeResult doc={withLean(lean)} />);
      expect(container.textContent).not.toMatch(LETTER);
      cleanup();
    }
  });

  it("puts your side first, then the other side, each with its bullets", () => {
    render(<AnalyzeResult doc={fixture} />);
    const mine = screen.getByText("Pukancun on 3 · Your Side");
    // The swap card names the team first, so the side label is the last match.
    const other = screen.getAllByText("Amon-Ra Dawg Your Team").at(-1) as HTMLElement;
    expect(mine.compareDocumentPosition(other) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(within(sideCard("Pukancun on 3 · Your Side")).getByText(ANALYSIS)).toBeTruthy();
    expect(screen.getByText(fixture.sides[1].bullets[1].text)).toBeTruthy();
  });

  it("shows the Bullets of each side as rows, each with its Mark, and no The Data part", () => {
    render(<AnalyzeResult doc={fixture} />);
    const mine = within(sideCard("Pukancun on 3 · Your Side"));
    const texts = fixture.sides[0].bullets.map((bullet) => bullet.text);
    const rows = mine.getAllByRole("listitem").filter((li) => texts.some((text) => li.textContent?.endsWith(text)));
    expect(rows.map((li) => li.lastElementChild?.textContent)).toEqual(texts);
    expect(screen.queryByText("The Data")).toBeNull();
  });

  it("marks each Bullet with a glyph that a screen reader hears as its word", () => {
    render(<AnalyzeResult doc={fixture} />);
    const card = sideCard("Pukancun on 3 · Your Side");
    const glyphs = [...card.querySelectorAll("[aria-hidden='true']")].map((el) => el.textContent).filter((t) => t && /[▲▼–]/.test(t));
    const GLYPH = { for: "▲", against: "▼", even: "–" } as const;
    expect(glyphs).toEqual(fixture.sides[0].bullets.map((bullet) => GLYPH[bullet.mark]));
    for (const bullet of fixture.sides[0].bullets) {
      const row = within(card).getByText(bullet.text).closest("li") as HTMLElement;
      expect(within(row).getByText(bullet.mark).className).toContain("sr-only");
    }
  });

  it("shows the players the side gets and gives with the headshot, the position, and the team", () => {
    render(<AnalyzeResult doc={fixture} />);
    const mine = within(sideCard("Pukancun on 3 · Your Side"));
    expect(mine.getByText("You Get")).toBeTruthy();
    expect(mine.getByText("You Give")).toBeTruthy();
    for (const name of ["Dalton Kincaid", "Garrett Wilson", "Nico Collins"]) {
      expect(mine.getByText(name)).toBeTruthy();
    }
    expect(mine.getByText("TE · BUF")).toBeTruthy();
    expect(mine.getByText("WR · HOU")).toBeTruthy();
    // The swap card names the team first, so the side label is the last match.
    const other = within((screen.getAllByText("Amon-Ra Dawg Your Team").at(-1) as HTMLElement).closest("section") as HTMLElement);
    expect(other.getByText("Gets")).toBeTruthy();
    expect(other.getByText("Gives")).toBeTruthy();
    // One headshot per player of the side, and the name names it.
    expect(sideCard("Pukancun on 3 · Your Side").querySelectorAll("img")).toHaveLength(3);
  });

  it("shows the Season rank of each player in the side card, and the Recent rank only when it is present", () => {
    render(<AnalyzeResult doc={fixture} />);
    const mine = within(sideCard("Pukancun on 3 · Your Side"));
    expect(mine.getByText("Season rank WR20")).toBeTruthy();
    expect(mine.getByText("Season rank WR11")).toBeTruthy();
    // Kincaid is TE10 by total points and TE39 by points per game of the last 4 weeks, so his Recent rank shows.
    expect(mine.getByText("Season rank TE10 · Recent rank TE39")).toBeTruthy();
    expect(mine.getAllByText(/Recent rank/)).toHaveLength(1);
    // The swap card shows no rank, so the finder cards that reuse it stay as they are.
    expect(within(tradeChapter()).queryByText(/Season rank/)).toBeNull();
  });

  it("shows no rank line for a player with no Season rank", () => {
    const noRanks: AnalyzeResponse = {
      ...fixture,
      trade: {
        ...fixture.trade,
        sides: fixture.trade.sides.map((side) => ({
          ...side,
          gives: side.gives.map(({ season_rank: _s, recent_rank: _r, ...player }) => player),
          gets: side.gets.map((player) => ({ ...player, season_rank: null, recent_rank: null })),
        })),
      },
    };
    render(<AnalyzeResult doc={noRanks} />);
    expect(screen.queryByText(/Season rank/)).toBeNull();
  });

  it("puts the players, then the Bullets in each side card, with no fold of factor rows", () => {
    render(<AnalyzeResult doc={fixture} />);
    const card = sideCard("Pukancun on 3 · Your Side");
    const player = within(card).getByText("Nico Collins");
    const bullet = within(card).getByText(ANALYSIS);
    expect(player.compareDocumentPosition(bullet) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(card.querySelector("details")).toBeNull();
    expect(screen.queryByText(/How the grade adds up/)).toBeNull();
  });

  it("shows the box This week and next with the two Week lines after the Bullets", () => {
    render(<AnalyzeResult doc={fixture} />);
    const card = sideCard("Pukancun on 3 · Your Side");
    const bullet = within(card).getByText(ANALYSIS);
    const box = within(card).getByRole("region", { name: "This week and next" });
    expect(within(box).getAllByRole("listitem").map((li) => li.textContent)).toEqual(
      fixture.sides[0].week_lines.map((line) => line.text),
    );
    expect(bullet.compareDocumentPosition(box) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("shows the box This week and next on every side of a three-side trade", () => {
    render(<AnalyzeResult doc={three} />);
    expect(screen.getAllByRole("region", { name: "This week and next" })).toHaveLength(three.sides.length);
  });

  it("passes the letter scan with a player named A.J. Brown in the swap card", () => {
    const brown = { player_id: "6801", name: "A.J. Brown", position: "WR", nfl_team: "PHI", headshot: "https://cdn.test/6801.png" };
    const tradeSides = fixture.trade.sides.map((side, i) => (i === 0 ? { ...side, gets: [...side.gets, brown] } : side));
    const { container } = render(<AnalyzeResult doc={{ ...fixture, trade: { ...fixture.trade, sides: tradeSides } }} />);
    expect(within(tradeChapter()).getByText("A.J. Brown")).toBeTruthy();
    expect(container.textContent).not.toMatch(LETTER);
  });

  it("orders the sides by the asker, so the Lean and your side name the same team", () => {
    render(<AnalyzeResult doc={withAsker(12)} />);
    expect(screen.getByText("The read for Amon-Ra Dawg Your Team")).toBeTruthy();
    const mine = screen.getByText("Amon-Ra Dawg Your Team · Your Side");
    const other = screen.getAllByText("Pukancun on 3").at(-1) as HTMLElement;
    expect(mine.compareDocumentPosition(other) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("names your side when the asker is not in the trade", () => {
    render(<AnalyzeResult doc={withAsker(99)} />);
    expect(screen.getByText("The read for Your Side")).toBeTruthy();
  });

  it("shows the players each side gets in the swap card", () => {
    render(<AnalyzeResult doc={fixture} />);
    const trade = within(tradeChapter());
    expect(trade.getByText("You Get")).toBeTruthy();
    expect(trade.getByText("Gets")).toBeTruthy();
    expect(trade.getByText("Dalton Kincaid")).toBeTruthy();
    expect(trade.getByText("Garrett Wilson")).toBeTruthy();
    expect(trade.getByText("Nico Collins")).toBeTruthy();
  });

  it("shows the counters placeholder", () => {
    render(<AnalyzeResult doc={fixture} />);
    expect(screen.getByRole("heading", { level: 2, name: "Suggested Counters" })).toBeTruthy();
    expect(screen.getByText("No counters yet.")).toBeTruthy();
  });

  it("shows the as-of line with the fetch time in the reader's locale", () => {
    render(<AnalyzeResult doc={fixture} />);
    const fetched = new Date(fixture.as_of.rosters_fetched as string).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
    const line = screen.getByText(/^Stats through week 5.* · rosters fetched/);
    expect(line.textContent).toBe(
      `Stats through week 5, plus 14 week 6 games · Usage pending for 8 games · rosters fetched ${fetched}`,
    );
    expect(line.textContent).not.toMatch(/chart/i);
    expect(line.textContent).not.toMatch(/live|partial|current week/i);
  });

  it("leaves out the fetch time when the API sends null", () => {
    render(<AnalyzeResult doc={{ ...fixture, as_of: { ...fixture.as_of, chart_week: null, rosters_fetched: null } }} />);
    const line = screen.getByText(/^Stats through week 5/);
    expect(line.textContent).not.toMatch(/null|1970|Chart week|rosters fetched/);
  });

  it("shows the no-values note under the Lean when the document says the week has no chart", () => {
    render(<AnalyzeResult doc={{ ...fixture, as_of: { ...fixture.as_of, no_chart: true, no_chart_note: NOTE } }} />);
    const note = screen.getByText(NOTE);
    const decision = screen.getByText("Lean yes");
    expect(decision.compareDocumentPosition(note) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(note.closest("section")).toBe(decision.closest("section"));
  });

  it("shows no no-values note when the document lacks the field", () => {
    render(<AnalyzeResult doc={fixture} />);
    expect(screen.queryByText(NOTE)).toBeNull();
  });

  it("shows the in-progress count and each pending count as its own segment", () => {
    const known_games = { week: 7, games: 13, in_progress: 2, pending: { snaps: 9 } };
    render(<AnalyzeResult doc={{ ...fixture, as_of: { ...fixture.as_of, stats_through: 7, completed_through: 6, known_games } }} />);
    const line = screen.getByText(/^Stats through week 6/);
    expect(line.textContent).toMatch(
      /^Stats through week 6, plus 13 week 7 games, 2 in progress · Snaps pending for 9 games · rosters fetched /,
    );
  });

  it("shows the stale stats segment after the pending segments and before the fetch time", () => {
    const { known_games: _k, ...asOf } = fixture.as_of;
    render(<AnalyzeResult doc={{ ...fixture, as_of: { ...asOf, stats_through: 6 }, stale: ["stats"] }} />);
    expect(screen.getByText(/^Stats through week 6 · Week 7 stats not fetched · rosters fetched$/)).toBeTruthy();
  });

  it("shows the stats week alone when the document has no known-games block", () => {
    const { completed_through: _c, known_games: _k, ...asOf } = fixture.as_of;
    render(<AnalyzeResult doc={{ ...fixture, as_of: asOf }} />);
    expect(screen.getByText(/^Stats through week 6 · rosters fetched$/)).toBeTruthy();
  });

  it.each([
    ["win_win", "Good for both"],
    ["fair", "Fair"],
  ] as const)("shows the fairness state %s as the line %s", (state, line) => {
    render(<AnalyzeResult doc={withFairness(state)} />);
    expect(screen.getByText(line)).toBeTruthy();
  });

  it("names the team that gives more on a lopsided line", () => {
    render(<AnalyzeResult doc={withFairness("lopsided", 12)} />);
    expect(screen.getByText("Lopsided: Amon-Ra Dawg Your Team gives more.")).toBeTruthy();
  });

  it.each([
    ["win_win", "Every side gets more than it gives."],
    ["fair", "No side gives much more than it gets, so every side can take it without a loss."],
  ] as const)("shows the meaning of the fairness state %s under the word", (state, meaning) => {
    render(<AnalyzeResult doc={withFairness(state)} />);
    const word = screen.getByText(state === "fair" ? "Fair" : "Good for both");
    const sentence = screen.getByText(meaning);
    expect(word.compareDocumentPosition(sentence) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("keeps the lopsided line and adds what the side that gives more loses", () => {
    render(<AnalyzeResult doc={withFairness("lopsided", 12)} />);
    const line = screen.getByText("Lopsided: Amon-Ra Dawg Your Team gives more.");
    const sentence = screen.getByText("It gives more than it gets.");
    expect(line.compareDocumentPosition(sentence) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("says Good for all on a win-win trade of three sides", () => {
    // The three-side fixture is fair, so the test makes it win-win.
    render(<AnalyzeResult doc={{ ...three, fairness: { ...three.fairness!, state: "win_win", gives_more: null } as Fairness }} />);
    expect(screen.getByText("Good for all")).toBeTruthy();
    expect(screen.queryByText("Good for both")).toBeNull();
    expect(screen.getByText("Every side gets more than it gives.")).toBeTruthy();
  });

  it("puts the fairness line under the Lean and above the swap card", () => {
    render(<AnalyzeResult doc={withFairness("fair")} />);
    const decision = screen.getByText("Lean yes");
    const line = screen.getByText("Fair");
    const trade = screen.getByRole("heading", { level: 2, name: "The Trade" });
    expect(decision.compareDocumentPosition(line) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(line.compareDocumentPosition(trade) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("puts the Case before the fairness text in the same chapter", () => {
    render(<AnalyzeResult doc={withFairness("fair")} />);
    const reason = screen.getByText(fixture.case);
    const line = screen.getByText("Fair");
    expect(reason.compareDocumentPosition(line) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(reason.closest("section")).toBe(line.closest("section"));
  });

  it("renders five chapters for a two-team trade", () => {
    const { container } = render(<AnalyzeResult doc={withFairness("fair")} />);
    expect(container.querySelectorAll("section")).toHaveLength(5);
  });

  it("puts the as-of line last, in the counters chapter", () => {
    const { container } = render(<AnalyzeResult doc={fixture} />);
    const line = screen.getByText(/ · rosters fetched/);
    const counters = screen.getByRole("heading", { level: 2, name: "Suggested Counters" });
    expect(container.textContent?.trimEnd().endsWith(line.textContent ?? "")).toBe(true);
    expect(line.closest("section")).toBe(counters.closest("section"));
  });

  it("shows the two fairness reasons under the line, the asker's side first", () => {
    // The asker here is roster 12, the second side of the trade, so the order must flip.
    const doc = withFairness("win_win");
    render(<AnalyzeResult doc={{ ...doc, trade: { ...doc.trade, asker: 12 } }} />);
    const line = screen.getByText("Good for both");
    const theirs = screen.getByText(THEIR_REASON);
    const mine = screen.getByText(MY_REASON);
    expect(line.compareDocumentPosition(theirs) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(theirs.compareDocumentPosition(mine) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("shows no fairness line and no reasons when the document has no fairness block", () => {
    const { fairness: _fairness, ...doc } = withFairness("fair");
    render(<AnalyzeResult doc={doc} />);
    expect(screen.queryByText("Fair")).toBeNull();
    expect(screen.queryByText(MY_REASON)).toBeNull();
    expect(screen.queryByText(THEIR_REASON)).toBeNull();
    expect(screen.queryByText("Fairness")).toBeNull();
    expect(screen.getByText(fixture.case)).toBeTruthy();
  });

  it("renders the arrow swap card for the two-side fixture", () => {
    render(<AnalyzeResult doc={fixture} />);
    const trade = within(tradeChapter());
    expect(trade.getByText("For")).toBeTruthy();
    expect(trade.getByText("You Get")).toBeTruthy();
    expect(trade.queryAllByRole("group")).toHaveLength(0);
    expect(trade.queryByText(/^(To|From)$/)).toBeNull();
  });

  it("renders one row per side for the three-side fixture, the asker first, with the From and To tags", () => {
    render(<AnalyzeResult doc={three} />);
    const trade = within(tradeChapter());
    expect(trade.queryByText("For")).toBeNull();
    const rows = trade.getAllByRole("group");
    expect(rows.map((row) => row.getAttribute("aria-label"))).toEqual([
      "Pukancun on 3",
      "Amon-Ra Dawg Your Team",
      "To Infinity and Bijan",
    ]);

    const [mine, middle, last] = rows.map((row) => within(row));
    expect(mine.getByText("You Give")).toBeTruthy();
    expect(mine.getByText("You Get")).toBeTruthy();
    expect(mine.getByText("Nico Collins")).toBeTruthy();
    expect(mine.getByText(byTag("To Amon-Ra Dawg Your Team"))).toBeTruthy();
    expect(mine.getByText(byTag("From Amon-Ra Dawg Your Team"))).toBeTruthy();
    expect(mine.getByText(byTag("From To Infinity and Bijan"))).toBeTruthy();

    expect(middle.getByText("Gives")).toBeTruthy();
    expect(middle.getByText("Gets")).toBeTruthy();
    expect(middle.getByText(byTag("To Pukancun on 3"))).toBeTruthy();
    expect(middle.getByText(byTag("To To Infinity and Bijan"))).toBeTruthy();
    expect(middle.getByText(byTag("From Pukancun on 3"))).toBeTruthy();

    expect(last.getByText("Marvin Harrison")).toBeTruthy();
    expect(last.getByText(byTag("To Pukancun on 3"))).toBeTruthy();
    expect(last.getByText("Garrett Wilson")).toBeTruthy();
    expect(last.getByText(byTag("From Amon-Ra Dawg Your Team"))).toBeTruthy();
  });

  it("puts each player in gives before the players in gets within a row", () => {
    render(<AnalyzeResult doc={three} />);
    const mine = within(within(tradeChapter()).getAllByRole("group")[0]);
    const gives = mine.getByText("You Give");
    const gets = mine.getByText("You Get");
    expect(gives.compareDocumentPosition(mine.getByText("Nico Collins")) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(mine.getByText("Nico Collins").compareDocumentPosition(gets) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(gets.compareDocumentPosition(mine.getByText("Marvin Harrison")) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("renders the rows without tags for a three-side document with no to and from", () => {
    render(<AnalyzeResult doc={stripMoves(three)} />);
    const trade = within(tradeChapter());
    expect(trade.getAllByRole("group")).toHaveLength(3);
    expect(trade.getAllByText("Marvin Harrison")).toHaveLength(2);
    for (const tag of THREE_TAGS) {
      expect(trade.queryByText(byTag(tag))).toBeNull();
    }
  });

  it("renders the arrow swap card for a two-side document with no to and from", () => {
    render(<AnalyzeResult doc={stripMoves(fixture)} />);
    const trade = within(tradeChapter());
    expect(trade.getByText("For")).toBeTruthy();
    expect(trade.getByText("You Get")).toBeTruthy();
    expect(trade.queryAllByRole("group")).toHaveLength(0);
  });

  it("renders one side read per side of the three-side fixture, in order", () => {
    render(<AnalyzeResult doc={three} />);
    expect(screen.getByText(three.case)).toBeTruthy();
    expect(screen.getAllByRole("region", { name: "This week and next" })).toHaveLength(3);
    const mine = screen.getByText("Pukancun on 3 · Your Side");
    // The swap card and the fairness reasons name each team first, so the side label is the last match.
    const middle = screen.getAllByText("Amon-Ra Dawg Your Team").at(-1) as HTMLElement;
    const last = screen.getAllByText("To Infinity and Bijan").at(-1) as HTMLElement;
    expect(mine.compareDocumentPosition(middle) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(middle.compareDocumentPosition(last) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });
});
