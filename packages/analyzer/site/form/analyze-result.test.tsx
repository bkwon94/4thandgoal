/**
 * Tests for the analyzer result. The API fixture document is the one input, and each test reads the screen.
 * They check what a reader sees, not the class names.
 */
import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
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
/* The switcher of the sides, its tab names in order, and the open tab panel. A closed panel is hidden, so the role query finds the open one only. */
const switcher = () => screen.getByRole("tablist", { name: "The sides" });
const tabNames = () => within(switcher()).getAllByRole("tab").map((tab) => tab.textContent);
const openPanel = () => screen.getByRole("tabpanel");
/* The bands of a panel, each a group named by its heading, and the claims of the rows of a band or a panel. */
const bandsOf = (panel: HTMLElement) => within(panel).getAllByRole("group").filter((g) => ["For", "Against", "Even"].includes(bandName(g)));
const bandName = (group: HTMLElement) => document.getElementById(group.getAttribute("aria-labelledby") ?? "")?.textContent ?? "";
const bandNames = (panel: HTMLElement) => bandsOf(panel).map(bandName);
const rowsOf = (el: HTMLElement) => [...el.querySelectorAll("[data-bullet-text]")];
/* The fixture with other Bullets on one side. */
const withBullets = (rosterId: number, bullets: AnalyzeResponse["sides"][number]["bullets"]): AnalyzeResponse => ({
  ...fixture,
  sides: fixture.sides.map((side) => (side.roster_id === rosterId ? { ...side, bullets } : side)),
});
/* Taps the tab of a team, then returns its open panel. */
const openTab = (team: string) => {
  fireEvent.click(within(switcher()).getByRole("tab", { name: team }));
  return openPanel();
};
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
    expect(screen.getByRole("heading", { level: 2, name: lean })).toBeTruthy();
    expect(screen.getByText(fixture.case)).toBeTruthy();
  });

  it("puts the Lean above the swap card and the sides", () => {
    render(<AnalyzeResult doc={fixture} />);
    const decision = screen.getByRole("heading", { level: 2, name: "Lean yes" });
    const trade = screen.getByRole("heading", { level: 2, name: "The Trade" });
    const side = switcher();
    expect(decision.compareDocumentPosition(trade) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(trade.compareDocumentPosition(side) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("opens the read chapter with the Lean word as a level-two heading", () => {
    render(<AnalyzeResult doc={fixture} />);
    const heading = screen.getByRole("heading", { level: 2, name: "Lean yes" });
    const trade = screen.getByRole("heading", { level: 2, name: "The Trade" });
    expect(heading.compareDocumentPosition(trade) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  /* The read fills the hero slots, and the hero ends at the feature with no empty stats or action. */
  it("puts the read in the slots: the side, the Lean, then the scale, the Case, and the fairness block in the feature", () => {
    render(<AnalyzeResult doc={fixture} />);
    const hero = screen.getByRole("region", { name: "The Read" });
    expect(slotsOf(hero)).toEqual(["eyebrow", "title", "feature"]);
    expect(slotText(hero, "eyebrow")).toBe("The read for Pukancun on 3");
    expect(slotText(hero, "title")).toBe("Lean yes");
    const feature = within(hero.querySelector("[data-hero-slot=feature]") as HTMLElement);
    const scale = feature.getByRole("list", { name: "The Lean scale" });
    const readCase = feature.getByText(fixture.case);
    const fairness = feature.getByText("Fairness");
    expect(scale.compareDocumentPosition(readCase) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(readCase.compareDocumentPosition(fairness) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(hero.querySelector("[data-hero-rule]")).toBeNull();
  });

  /* The scale reads from the no end to the yes end, so the lit step shows how strong the call is. */
  it.each(LEANS)("shows the 5-step scale from Pass to Send it with the step %s lit", (lean) => {
    render(<AnalyzeResult doc={withLean(lean)} />);
    const steps = within(screen.getByRole("list", { name: "The Lean scale" })).getAllByRole("listitem");
    expect(steps.map((step) => step.textContent)).toEqual(["Pass", "Lean no", "Gut call", "Lean yes", "Send it"]);
    const lit = steps.filter((step) => step.getAttribute("aria-current") === "step");
    expect(lit.map((step) => step.textContent)).toEqual([lean]);
  });

  /* A phone clamps the Case to 3 lines, and the button opens the rest. jsdom draws no lines, so the test reads the state the button sets. */
  it("clamps the Case on the phone, and Read the full case opens the rest", () => {
    render(<AnalyzeResult doc={fixture} />);
    const button = screen.getByRole("button", { name: "Read the full case" });
    const readCase = screen.getByText(fixture.case);
    expect(button.getAttribute("aria-expanded")).toBe("false");
    expect(button.getAttribute("aria-controls")).toBe(readCase.id);
    expect(readCase.className).toContain("line-clamp-3");
    fireEvent.click(button);
    expect(readCase.className).not.toContain("line-clamp-3");
    expect(screen.queryByRole("button", { name: "Read the full case" })).toBeNull();
  });

  it("keeps the static grid, the glow, and the brackets in the read hero, and draws no scene (AT-35, AT-44)", () => {
    render(<AnalyzeResult doc={tradeA} />);
    const hero = screen.getByRole("region", { name: "The Read" });
    expect(document.querySelectorAll("canvas[data-hero-scene]")).toHaveLength(0);
    // The static hero: the texture layer holds the grid and the glow, and the four brackets sit in the corners.
    expect(hero.querySelectorAll("[data-hero-art='texture']")).toHaveLength(1);
    expect(hero.querySelectorAll("[data-hero-art='bracket']")).toHaveLength(4);
  });

  it("keeps the scale and the Case in the feature, with no fairness card, when the document has no fairness block and no note", () => {
    render(<AnalyzeResult doc={{ ...fixture, fairness: undefined }} />);
    const hero = screen.getByRole("region", { name: "The Read" });
    expect(slotsOf(hero)).toEqual(["eyebrow", "title", "feature"]);
    expect(within(hero).queryByText("Fairness")).toBeNull();
  });

  it("shows no letter grade anywhere in the result", () => {
    for (const lean of LEANS) {
      const { container } = render(<AnalyzeResult doc={withLean(lean)} />);
      expect(container.textContent).not.toMatch(LETTER);
      cleanup();
    }
  });

  it("puts one tab per team under the swap card, with the tab of the asker first and open", () => {
    render(<AnalyzeResult doc={fixture} />);
    const trade = screen.getByRole("heading", { level: 2, name: "The Trade" });
    expect(trade.compareDocumentPosition(switcher()) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(tabNames()).toEqual(["Pukancun on 3", "Amon-Ra Dawg Your Team"]);
    const [mine, other] = within(switcher()).getAllByRole("tab");
    expect(mine.getAttribute("aria-selected")).toBe("true");
    expect(other.getAttribute("aria-selected")).toBe("false");
    expect(within(openPanel()).getByText(ANALYSIS)).toBeTruthy();
    expect(within(openPanel()).queryByText(fixture.sides[1].bullets[1].text)).toBeNull();
  });

  it("shows the Bullets of the other team after a tap on its tab", () => {
    render(<AnalyzeResult doc={fixture} />);
    const panel = openTab("Amon-Ra Dawg Your Team");
    expect(within(switcher()).getByRole("tab", { name: "Amon-Ra Dawg Your Team" }).getAttribute("aria-selected")).toBe("true");
    expect(within(panel).getByText(fixture.sides[1].bullets[1].text)).toBeTruthy();
    expect(within(panel).queryByText(ANALYSIS)).toBeNull();
  });

  it("moves the open tab with the arrow keys", () => {
    render(<AnalyzeResult doc={three} />);
    const [first, second] = within(switcher()).getAllByRole("tab");
    fireEvent.keyDown(first, { key: "ArrowRight" });
    expect(second.getAttribute("aria-selected")).toBe("true");
    expect(document.activeElement).toBe(second);
    fireEvent.keyDown(second, { key: "ArrowLeft" });
    expect(first.getAttribute("aria-selected")).toBe("true");
    fireEvent.keyDown(first, { key: "ArrowLeft" });
    expect(tabNames().at(-1)).toBe(document.activeElement?.textContent);
  });

  it("shows three tabs for a 3-team trade, the asker first", () => {
    render(<AnalyzeResult doc={three} />);
    expect(tabNames()).toEqual(["Pukancun on 3", "Amon-Ra Dawg Your Team", "To Infinity and Bijan"]);
  });

  it("shows the Bullets of the open tab as rows, each with its claim, and no The Data part", () => {
    render(<AnalyzeResult doc={fixture} />);
    const texts = fixture.sides[0].bullets.map((bullet) => bullet.text);
    const rows = rowsOf(openPanel());
    expect(rows.map((row) => row.textContent)).toEqual(texts);
    expect(screen.queryByText("The Data")).toBeNull();
  });

  it("puts the Bullets in For, then Against, then Even bands, whatever the order of the document", () => {
    const mixed = [...fixture.sides[0].bullets].reverse();
    render(<AnalyzeResult doc={withBullets(4, mixed)} />);
    const bands = bandsOf(openPanel());
    expect(bands.map(bandName)).toEqual(["For", "Against", "Even"]);
    for (const [band, mark] of bands.map((band, i) => [band, (["for", "against", "even"] as const)[i]] as const)) {
      expect(rowsOf(band).map((row) => row.textContent)).toEqual(mixed.filter((b) => b.mark === mark).map((b) => b.text));
    }
  });

  it("leaves out a band with no Bullet", () => {
    render(<AnalyzeResult doc={withBullets(4, fixture.sides[0].bullets.filter((b) => b.mark !== "even"))} />);
    expect(bandNames(openPanel())).toEqual(["For", "Against"]);
    render(<AnalyzeResult doc={withBullets(4, fixture.sides[0].bullets.filter((b) => b.mark === "against"))} />);
    expect(bandNames(screen.getAllByRole("tabpanel").at(-1)!)).toEqual(["Against"]);
  });

  it("marks each Bullet with a glyph that a screen reader hears as its word", () => {
    render(<AnalyzeResult doc={fixture} />);
    const card = openPanel();
    const glyphs = [...card.querySelectorAll("[aria-hidden='true']")].map((el) => el.textContent).filter((t) => t && /[▲▼–]/.test(t));
    const GLYPH = { for: "▲", against: "▼", even: "–" } as const;
    expect(glyphs).toEqual(fixture.sides[0].bullets.map((bullet) => GLYPH[bullet.mark]));
    // The row is a button, and its name starts with the word of the Mark, so the glyph never reaches a screen reader.
    for (const bullet of fixture.sides[0].bullets) {
      expect(within(card).getByRole("button", { name: `${bullet.mark} ${bullet.text}` })).toBeTruthy();
    }
  });

  it("opens the fact of a row under it on a tap, and closes it on a second tap", () => {
    render(<AnalyzeResult doc={fixture} />);
    const bullet = fixture.sides[0].bullets[0];
    const row = within(openPanel()).getByRole("button", { name: `${bullet.mark} ${bullet.text}` });
    const fact = within(openPanel()).getByText(bullet.fact_text);
    expect(row.getAttribute("aria-expanded")).toBe("false");
    expect(fact.closest("[aria-hidden='true']")).not.toBeNull();
    fireEvent.click(row);
    expect(row.getAttribute("aria-expanded")).toBe("true");
    expect(row.getAttribute("aria-controls")).toBe(fact.closest("[id]")?.id);
    expect(fact.closest("[aria-hidden='true']")).toBeNull();
    expect(row.compareDocumentPosition(fact) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    fireEvent.click(row);
    expect(row.getAttribute("aria-expanded")).toBe("false");
  });

  it("shows the players the side gets and gives with the headshot, the position, and the team", () => {
    render(<AnalyzeResult doc={fixture} />);
    const mine = within(openPanel());
    expect(mine.getByText("You Get")).toBeTruthy();
    expect(mine.getByText("You Give")).toBeTruthy();
    for (const name of ["Dalton Kincaid", "Garrett Wilson", "Nico Collins"]) {
      expect(mine.getByText(name)).toBeTruthy();
    }
    expect(mine.getByText("TE · BUF")).toBeTruthy();
    expect(mine.getByText("WR · HOU")).toBeTruthy();
    // One headshot per player of the side, and the name names it.
    expect(openPanel().querySelectorAll("img")).toHaveLength(3);
    const other = within(openTab("Amon-Ra Dawg Your Team"));
    expect(other.getByText("Gets")).toBeTruthy();
    expect(other.getByText("Gives")).toBeTruthy();
  });

  it("shows the Season rank of each player in the side card, and the Recent rank only when it is present", () => {
    render(<AnalyzeResult doc={fixture} />);
    const mine = within(openPanel());
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
    // A fact text can name a Season rank in prose, so the scan reads the rank lines only.
    expect(screen.queryByText(/^Season rank/)).toBeNull();
  });

  it("puts the players, then the Bullets in each side card, with no fold of factor rows", () => {
    render(<AnalyzeResult doc={fixture} />);
    const card = openPanel();
    const player = within(card).getByText("Nico Collins");
    const bullet = within(card).getByText(ANALYSIS);
    expect(player.compareDocumentPosition(bullet) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(card.querySelector("details")).toBeNull();
    expect(screen.queryByText(/How the grade adds up/)).toBeNull();
  });

  it("shows the box This week and next with the two Week lines after the Bullets", () => {
    render(<AnalyzeResult doc={fixture} />);
    const card = openPanel();
    const bullet = within(card).getByText(ANALYSIS);
    const box = within(card).getByRole("region", { name: "This week and next" });
    expect(within(box).getAllByRole("listitem").map((li) => li.textContent)).toEqual(
      fixture.sides[0].week_lines.map((line) => line.text),
    );
    expect(bullet.compareDocumentPosition(box) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("shows the box This week and next on every side of a three-side trade", () => {
    render(<AnalyzeResult doc={three} />);
    for (const side of three.trade.sides) {
      expect(within(openTab(side.team)).getAllByRole("region", { name: "This week and next" })).toHaveLength(1);
    }
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
    expect(tabNames()).toEqual(["Amon-Ra Dawg Your Team", "Pukancun on 3"]);
    expect(within(openPanel()).getByText(fixture.sides[1].bullets[0].text)).toBeTruthy();
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
    const decision = screen.getByRole("heading", { level: 2, name: "Lean yes" });
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
    const decision = screen.getByRole("heading", { level: 2, name: "Lean yes" });
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

  it("renders four chapters for a two-team trade: the read, the trade, the sides, and the counters", () => {
    const { container } = render(<AnalyzeResult doc={withFairness("fair")} />);
    expect(container.querySelectorAll("section")).toHaveLength(4);
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
    for (const side of three.sides) {
      expect(within(openTab(three.trade.sides.find((t) => t.roster_id === side.roster_id)!.team)).getByText(side.bullets[0].text)).toBeTruthy();
    }
  });
});
