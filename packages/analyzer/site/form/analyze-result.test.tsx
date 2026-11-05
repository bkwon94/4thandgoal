/**
 * Tests for the analyzer result. The API fixture document is the one input, and each test reads the screen.
 * They check what a reader sees, not the class names.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { analyzeResponse as fixtureJson, analyzeResponseThree as threeJson } from "../lib/fixtures/api";
import type { AnalyzeResponse, Decision, Fairness } from "../lib/analyze-types";
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
const withAnswer = (answer: Decision["answer"]): AnalyzeResponse => ({ ...fixture, decision: { ...fixture.decision, answer } });
const ANALYSIS = "Nico Collins leads the trade in points per game.";
/* A single letter on its own is a grade. A letter in an initial such as "A.J." is a name, so the scan skips it. */
const LETTER = /(?<![\w.])[A-F](?![\w.])/;
const FALLBACK_LINE = "The analysis is unavailable, so the rows stand alone.";
const DEAL = "What you get and what you give are about even, after a discount on the side with more players.";
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

describe("AnalyzeResult", () => {
  it.each([
    ["yes", "Yes"],
    ["no", "No"],
    ["not_as_is", "Not as is"],
  ] as const)("shows the answer %s as the word %s with its reason", (answer, word) => {
    render(<AnalyzeResult doc={withAnswer(answer)} />);
    expect(screen.getByText("Decision for Pukancun on 3")).toBeTruthy();
    expect(screen.getByText(word)).toBeTruthy();
    expect(screen.getByText(fixture.decision.reason)).toBeTruthy();
  });

  it("puts the decision above the swap card and the sides", () => {
    render(<AnalyzeResult doc={fixture} />);
    const decision = screen.getByText("Not as is");
    const trade = screen.getByRole("heading", { level: 2, name: "The Trade" });
    const side = screen.getByText("Pukancun on 3 · Your Side");
    expect(decision.compareDocumentPosition(trade) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(trade.compareDocumentPosition(side) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("opens the decision chapter with a level-two heading", () => {
    render(<AnalyzeResult doc={fixture} />);
    const heading = screen.getByRole("heading", { level: 2, name: "Decision for Pukancun on 3" });
    const trade = screen.getByRole("heading", { level: 2, name: "The Trade" });
    expect(heading.compareDocumentPosition(trade) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("shows no letter grade anywhere in the result", () => {
    for (const answer of ["yes", "no", "not_as_is"] as const) {
      const { container } = render(<AnalyzeResult doc={withAnswer(answer)} />);
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
    expect(screen.getAllByText(ANALYSIS)).toHaveLength(2);
  });

  it("shows the bullets of each side as a list, with no The Data part", () => {
    render(<AnalyzeResult doc={fixture} />);
    const mine = within(sideCard("Pukancun on 3 · Your Side"));
    const items = mine.getAllByRole("listitem").filter((li) => fixture.sides[0].bullets.includes(li.textContent ?? ""));
    expect(items.map((li) => li.textContent)).toEqual(fixture.sides[0].bullets);
    expect(screen.queryByText("The Data")).toBeNull();
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

  it("puts the players, then the bullets, then the closed fold in each side card", () => {
    render(<AnalyzeResult doc={fixture} />);
    const card = sideCard("Pukancun on 3 · Your Side");
    const player = within(card).getByText("Nico Collins");
    const bullet = within(card).getByText(ANALYSIS);
    const fold = card.querySelector("details") as HTMLDetailsElement;
    expect(player.compareDocumentPosition(bullet) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(bullet.compareDocumentPosition(fold) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(fold.open).toBe(false);
    expect(within(card).getByText(`How the grade adds up · ${fixture.sides[0].factors.length} rows`)).toBeTruthy();
  });

  it("puts the deal row first in the fold, with its mark", () => {
    render(<AnalyzeResult doc={fixture} />);
    const fold = sideCard("Pukancun on 3 · Your Side").querySelector("details") as HTMLElement;
    const rows = within(fold).getAllByRole("listitem");
    expect(rows).toHaveLength(fixture.sides[0].factors.length);
    expect(rows[0].textContent).toContain(DEAL);
    expect(within(rows[0]).getByText("even")).toBeTruthy();
  });

  it("says 1 row when a side has one row", () => {
    const sides = fixture.sides.map((side) => ({ ...side, factors: side.factors.slice(0, 1) }));
    render(<AnalyzeResult doc={{ ...fixture, sides }} />);
    expect(screen.getAllByText("How the grade adds up · 1 row")).toHaveLength(2);
  });

  it("shows the same layout when the address has a query string", () => {
    window.history.replaceState({}, "", "/analyze?layout=b");
    render(<AnalyzeResult doc={fixture} />);
    expect(sideCard("Pukancun on 3 · Your Side").querySelector("details")).toBeTruthy();
    window.history.replaceState({}, "", "/");
  });

  it("shows a factor reason with a number once, under The reasoning only", () => {
    const reason = "He played 41 of 60 snaps last week.";
    const sides = fixture.sides.map((side, i) =>
      i === 0 ? { ...side, factors: side.factors.map((f, j) => (j === 2 ? { ...f, reason } : f)) } : side,
    );
    render(<AnalyzeResult doc={{ ...fixture, sides }} />);
    expect(screen.getAllByText(reason)).toHaveLength(1);
  });

  it("passes the letter scan with a player named A.J. Brown in the swap card", () => {
    const brown = { player_id: "6801", name: "A.J. Brown", position: "WR", nfl_team: "PHI", headshot: "https://cdn.test/6801.png" };
    const tradeSides = fixture.trade.sides.map((side, i) => (i === 0 ? { ...side, gets: [...side.gets, brown] } : side));
    const { container } = render(<AnalyzeResult doc={{ ...fixture, trade: { ...fixture.trade, sides: tradeSides } }} />);
    expect(within(tradeChapter()).getByText("A.J. Brown")).toBeTruthy();
    expect(container.textContent).not.toMatch(LETTER);
  });

  it("orders the sides by the decision side, so the decision and your side name the same team", () => {
    render(<AnalyzeResult doc={{ ...fixture, decision: { ...fixture.decision, for_roster: 12 } }} />);
    expect(screen.getByText("Decision for Amon-Ra Dawg Your Team")).toBeTruthy();
    const mine = screen.getByText("Amon-Ra Dawg Your Team · Your Side");
    const other = screen.getAllByText("Pukancun on 3").at(-1) as HTMLElement;
    expect(mine.compareDocumentPosition(other) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("names your side when the decision team is not in the trade", () => {
    render(<AnalyzeResult doc={{ ...fixture, decision: { ...fixture.decision, for_roster: 99 } }} />);
    expect(screen.getByText("Decision for Your Side")).toBeTruthy();
  });

  it("shows every factor in the fold with its lean and reason", () => {
    render(<AnalyzeResult doc={fixture} />);
    expect(screen.queryByText("The Reasoning")).toBeNull();
    for (const name of ["deal", "roster fit", "standing", "trend and usage", "injury", "handcuff", "schedule"]) {
      expect(screen.getAllByText(name)).toHaveLength(2);
    }
    for (const side of fixture.sides) {
      for (const factor of side.factors) {
        expect(screen.getAllByText(factor.reason).length).toBeGreaterThan(0);
      }
    }
    expect(screen.getAllByText("for")).toHaveLength(2);
    expect(screen.getAllByText("against")).toHaveLength(1);
    expect(screen.getAllByText("even")).toHaveLength(11);
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

  it("shows the no-values note under the decision when the document says the week has no chart", () => {
    render(<AnalyzeResult doc={{ ...fixture, as_of: { ...fixture.as_of, no_chart: true, no_chart_note: NOTE } }} />);
    const note = screen.getByText(NOTE);
    const decision = screen.getByText("Not as is");
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

  it("shows the decision, the rows, and the fallback line when a side has no bullets", () => {
    const sides = fixture.sides.map((side) => ({ ...side, bullets: [] }));
    render(<AnalyzeResult doc={{ ...fixture, sides, fallback: true }} />);
    expect(screen.getByText("Not as is")).toBeTruthy();
    expect(screen.getAllByText(FALLBACK_LINE)).toHaveLength(2);
    expect(screen.getAllByText(DEAL)).toHaveLength(2);
    expect(screen.getAllByText(/^How the grade adds up · /)).toHaveLength(2);
    expect(screen.queryByText(ANALYSIS)).toBeNull();
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

  it("puts the fairness line under the decision and above the swap card", () => {
    render(<AnalyzeResult doc={withFairness("fair")} />);
    const decision = screen.getByText("Not as is");
    const line = screen.getByText("Fair");
    const trade = screen.getByRole("heading", { level: 2, name: "The Trade" });
    expect(decision.compareDocumentPosition(line) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(line.compareDocumentPosition(trade) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("puts the decision text before the fairness text in the same chapter", () => {
    render(<AnalyzeResult doc={withFairness("fair")} />);
    const reason = screen.getByText(fixture.decision.reason);
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
    render(<AnalyzeResult doc={{ ...doc, decision: { ...doc.decision, for_roster: 12 } }} />);
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
    expect(screen.getByText(fixture.decision.reason)).toBeTruthy();
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
    expect(screen.getByText(three.decision.reason)).toBeTruthy();
    expect(screen.getAllByText(/^How the grade adds up · \d+ rows$/)).toHaveLength(3);
    const mine = screen.getByText("Pukancun on 3 · Your Side");
    // The swap card and the fairness reasons name each team first, so the side label is the last match.
    const middle = screen.getAllByText("Amon-Ra Dawg Your Team").at(-1) as HTMLElement;
    const last = screen.getAllByText("To Infinity and Bijan").at(-1) as HTMLElement;
    expect(mine.compareDocumentPosition(middle) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(middle.compareDocumentPosition(last) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });
});
