/**
 * Tests for the week card of The Race on the real CPC week 11 sim file and the NorCal week 10 file, with Bo Girds as Your
 * team: the Score to beat, the result tiles, the root-for list of each result, the tiebreak gap, and the What-if of a tile.
 */
import "@cpc/design/ui/sheet-jsdom";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, spyOn } from "bun:test";
import { norcalWeekSim, weekElevenSim } from "../fixtures/sim";
import { elevenLossBelow, elevenWinAbove, fakeWhatIfApi } from "../fixtures/what-if-api";
import { SimPage } from "./sim-page";

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

// Bo Girds is roster 6 in CPC and roster 7 in NorCal. Week 12 of CPC is Bo Girds against roster 5.
const YOU = 6;
const NORCAL_YOU = 7;
const sim = weekElevenSim;
const page = sim.pages[YOU];
const card = page.week_card!;

const weekCard = () => screen.getByRole("article", { name: /^Week \d+ vs / });
const tiles = () =>
  within(within(weekCard()).getByRole("group", { name: "Results" })).getAllByRole("button");
const tile = (name: string) => tiles().find((entry) => entry.textContent?.startsWith(name))!;
const rootFor = () => within(weekCard()).getByRole("list", { name: "Games to root for" });
const medianRoot = () =>
  within(weekCard()).queryByRole("list", { name: "Median results to root for" });
const yourTeam = () => screen.getByRole("region", { name: "Your team" });
const cardOdds = () => yourTeam().querySelector("[data-goal-odds]")!.getAttribute("data-goal-odds");
const finishOdds = () =>
  within(screen.getByRole("group", { name: "Finish list for a playoff spot" }))
    .getAllByRole("button")
    .map((bar) => bar.getAttribute("data-odds"));
const boardOdds = () =>
  Object.fromEntries(
    within(screen.getByRole("group", { name: /^League board/ }))
      .getAllByRole("button")
      .map((bar) => [bar.getAttribute("data-roster"), bar.getAttribute("data-odds")]),
  );

const NAMES = [
  "Win and beat the median",
  "Win, but miss the median",
  "Lose, but beat the median",
  "Lose and miss the median",
];

describe("the week card", () => {
  it("names the opponent and shows the Score to beat against it and the median, to win and to be sure", () => {
    render(<SimPage sim={sim} you={YOU} />);
    const beat = page.score_to_beat[0];
    expect(card.opponent).toBe(5);
    expect(within(weekCard()).getByRole("heading").textContent).toBe(`Week 12 vs ${sim.names[5]}`);
    const table = within(weekCard()).getByRole("table", { name: "Score to beat" });
    expect(within(table).getByRole("columnheader", { name: "To win" })).toBeTruthy();
    expect(within(table).getByRole("columnheader", { name: "To be sure" })).toBeTruthy();
    const rows = within(table).getAllByRole("row").slice(1);
    expect(rows.map((row) => row.textContent)).toEqual([
      `Beat ${sim.names[5]}${beat.win}${beat.win_sure}`,
      `Beat the median${beat.median}${beat.median_sure}`,
    ]);
  });

  it("shows four tiles with the odds of the Goal after each result and how likely it is", () => {
    render(<SimPage sim={sim} you={YOU} />);
    expect(
      tiles().map((entry) => NAMES.find((name) => entry.textContent?.startsWith(name))),
    ).toEqual(NAMES);
    tiles().forEach((entry, i) => {
      expect(entry.textContent).toContain(`${card.goals.spot.odds[i]}%`);
      expect(entry.textContent).toContain(`${Math.round(card.results[i].chance)}% likely`);
    });
    fireEvent.click(screen.getByRole("radio", { name: "Bye" }));
    tiles().forEach((entry, i) =>
      expect(entry.textContent).toContain(`${card.goals.bye.odds[i]}%`),
    );
  });

  it("roots for every other game of the week for the most likely result before a tap", () => {
    render(<SimPage sim={sim} you={YOU} />);
    const likely = card.results.reduce(
      (best, r, i) => (r.chance > card.results[best].chance ? i : best),
      0,
    );
    expect(
      within(weekCard()).getByText(new RegExp(`^If you ${NAMES[likely].toLowerCase()}`)),
    ).toBeTruthy();
    expect(within(rootFor()).getAllByRole("listitem")).toHaveLength(5);
  });
});

describe("a tap on a result tile", () => {
  beforeEach(() => {
    spyOn(globalThis, "fetch").mockImplementation((() =>
      Promise.reject(new TypeError("fetch failed"))) as unknown as typeof fetch);
  });

  it("lists the 5 other games with both results, a gray tag on a game under 1 point, and 1 or 2 median rows", async () => {
    const api = fakeWhatIfApi();
    render(<SimPage sim={sim} you={YOU} whatIf={api} />);
    fireEvent.click(tile("Win and beat the median"));
    await waitFor(() => expect(cardOdds()).toBe(`${elevenWinAbove.page.playoff}%`));
    const rows = within(rootFor()).getAllByRole("listitem");
    expect(rows).toHaveLength(5);
    const roots = elevenWinAbove.page.week_card!.goals.spot.root_for[0];
    expect(roots).toHaveLength(5);
    roots.forEach((root, i) => {
      const text = rows[i].textContent!;
      if (root.odds - root.other < 1) {
        expect(text).toContain(`${sim.names[root.winner]} vs ${sim.names[root.loser]}`);
        expect(within(rows[i]).getByText("Doesn't matter")).toBeTruthy();
      } else {
        expect(text).toContain(
          `${sim.names[root.winner]} beats ${sim.names[root.loser]}→ ${root.odds}%`,
        );
        expect(text).toContain(`${sim.names[root.loser]} wins→ ${root.other}%`);
        expect(within(rows[i]).queryByText("Doesn't matter")).toBeNull();
      }
    });
    const medians = within(medianRoot()!).getAllByRole("listitem");
    expect(medians.length).toBeGreaterThanOrEqual(1);
    expect(medians.length).toBeLessThanOrEqual(2);
    expect(medians[0].textContent).toMatch(/misses the median→ \d+%$/);
  });

  it("sets a What-if, and the Finish list and the board take the numbers of the response", async () => {
    const api = fakeWhatIfApi();
    render(<SimPage sim={sim} you={YOU} whatIf={api} />);
    const before = finishOdds();
    fireEvent.click(tile("Lose and miss the median"));
    expect(api.calls.map((call) => call.ask)).toEqual([
      { you: YOU, set: [{ week: 12, game: "loss", median: "below" }] },
    ]);
    const answer = elevenLossBelow;
    await waitFor(() => expect(cardOdds()).toBe(`${answer.page.playoff}%`));
    expect(screen.getByRole("region", { name: "What-if" }).textContent).toContain(
      "Wk 12 lose, miss median",
    );
    expect(finishOdds()).toEqual(answer.page.finishes.spot.map((finish) => String(finish.odds)));
    expect(finishOdds()).not.toEqual(before);
    expect(boardOdds()).toEqual(
      Object.fromEntries(
        answer.board.map((team) => [String(team.roster_id), String(team.goals.spot.odds)]),
      ),
    );
    // The pressed tile takes the odds of the answer, and each other tile keeps the odds of the file.
    expect(tile("Lose and miss the median").getAttribute("aria-pressed")).toBe("true");
    expect(tile("Lose and miss the median").textContent).toContain(`${answer.page.playoff}%`);
    expect(tile("Win and beat the median").textContent).toContain(`${card.goals.spot.odds[0]}%`);
  });

  it("keeps the numbers of the file with the API down, shows a quiet note, and roots for the tapped result", async () => {
    render(<SimPage sim={sim} you={YOU} />);
    const before = finishOdds();
    fireEvent.click(tile("Lose and miss the median"));
    await screen.findByText("The What-if is not available now.");
    expect(finishOdds()).toEqual(before);
    expect(cardOdds()).toBe(`${page.goals.spot.odds}%`);
    await waitFor(() =>
      expect(within(weekCard()).getByText(/^If you lose and miss the median/)).toBeTruthy(),
    );
    expect(within(rootFor()).getAllByRole("listitem")).toHaveLength(5);
    // The file holds a game under 1 point for a win over the median, and it shows the gray tag.
    fireEvent.click(tile("Win and beat the median"));
    await waitFor(() =>
      expect(within(weekCard()).getByText(/^If you win and beat the median/)).toBeTruthy(),
    );
    const flat = card.goals.spot.root_for[0].filter((root) => root.odds - root.other < 1);
    expect(flat.length).toBeGreaterThan(0);
    expect(within(rootFor()).getAllByText("Doesn't matter")).toHaveLength(flat.length);
  });
});

describe("the root-for list of a Goal", () => {
  it("holds no list on a seed, and points to the spot and the bye", async () => {
    render(<SimPage sim={sim} you={YOU} />);
    fireEvent.click(screen.getByRole("radio", { name: "Seed" }));
    await waitFor(() =>
      expect(within(weekCard()).getByText("Pick Spot or Bye to see who to root for.")).toBeTruthy(),
    );
    expect(within(weekCard()).queryByRole("list", { name: "Games to root for" })).toBeNull();
  });
});

describe("the week card of NorCal", () => {
  it("shows 2 tiles, no median score, and no median rooting", () => {
    render(<SimPage sim={norcalWeekSim} you={NORCAL_YOU} />);
    expect(tiles().map((entry) => entry.textContent?.split(/\d/)[0])).toEqual(["Win", "Lose"]);
    const table = within(weekCard()).getByRole("table", { name: "Score to beat" });
    expect(table.textContent).not.toContain("median");
    expect(medianRoot()).toBeNull();
  });

  it("shows the tiebreak gap when another team sits close across the edge of the Goal", () => {
    // Bo Girds trails roster 11 by 10.2 Points For at the edge of a playoff spot.
    const gap = norcalWeekSim.pages[NORCAL_YOU].week_card!.goals.spot.tiebreak!;
    expect(gap).toEqual({ roster_id: 11, points: -10.2 });
    render(<SimPage sim={norcalWeekSim} you={NORCAL_YOU} />);
    fireEvent.click(screen.getByRole("radio", { name: "Spot" }));
    expect(
      within(weekCard()).getByText(
        `Points For break a tie. You trail ${norcalWeekSim.names[11]} by 10.2.`,
      ),
    ).toBeTruthy();
  });
});
