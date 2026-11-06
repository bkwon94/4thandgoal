/**
 * Tests for the sim replay on the real sim file of CPC 2026 week 8: a press plays a run beat by beat, a skip shows the end,
 * a press during a run starts a clean run, the odds of all runs show, and no control picks a winner. The clock is fake.
 */
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { oneDecimal } from "@cpc/design/format/format";
import { sim } from "../fixtures/sim";
import { beatsOf } from "./beats";
import { replaySeason } from "./season";
import { SimReplay } from "./sim-replay";

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
});

/* A pick that plays the given runs in order, so a test knows each run. */
function picks(...runs: number[]) {
  let press = 0;
  return () => runs[press++ % runs.length];
}

/* Moves the clock past the holds of the next `count` beats of run `run`, from beat `from`. */
function playBeats(run: number, from: number, count: number) {
  const beats = beatsOf(replaySeason(sim, run));
  for (const beat of beats.slice(from, from + count)) {
    act(() => {
      vi.advanceTimersByTime(beat.ms);
    });
  }
}

const press = () => fireEvent.click(screen.getByRole("button", { name: "Sim the season" }));
const stage = () => screen.getByRole("region", { name: "The replay" });

describe("the sim replay", () => {
  it("waits for a press, with the odds of all runs and no skip", () => {
    render(<SimReplay sim={sim} pick={picks(0)} />);
    expect(screen.getByRole("button", { name: "Sim the season" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Skip to the end" })).toBeNull();
    const odds = screen.getByRole("table", { name: "The odds of all 10,000 runs" });
    // One row per team, ordered by mean wins, with the playoff, bye, and title odds of the file.
    const rows = within(odds).getAllByRole("row").slice(1);
    expect(rows).toHaveLength(12);
    const fridge = rows.find((row) => row.textContent?.includes("Lil Fridge"))!;
    const t = sim.teams[3];
    expect(within(fridge).getAllByRole("cell").map((cell) => cell.textContent)).toEqual([
      `${t.playoff}%`,
      `${t.bye}%`,
      `${t.title}%`,
      "–",
    ]);
  });

  it("plays a run: a lower third each week, the PLAYOFFS wipe, the final standings, the bracket, and the champion", () => {
    render(<SimReplay sim={sim} pick={picks(0)} />);
    press();
    const season = replaySeason(sim, 0);

    // Week 9: the lower third names the week and the median, over the scores of the week.
    const third = within(stage()).getByRole("group", { name: "Week 9 final" });
    expect(third.textContent).toContain("WEEK 9 FINAL");
    expect(third.textContent).toContain(`Median ${oneDecimal(season.weeks[0].median!)}`);
    expect(third.textContent).toContain("The Blue Tent 112.9");

    // Each week reorders the standings to the order after that week.
    playBeats(0, 0, 5);
    expect(within(stage()).getByRole("group", { name: "Week 14 final" })).toBeTruthy();
    const order = within(stage()).getByRole("list", { name: "Standings" });
    expect(within(order).getAllByRole("listitem").map((row) => row.dataset.roster)).toEqual(
      season.weeks[5].standings.map((row) => String(row.roster_id)),
    );

    // After week 14: the red PLAYOFFS wipe, then the final standings with the byes and the cut under seed 6.
    playBeats(0, 5, 1);
    expect(within(stage()).getByText("PLAYOFFS")).toBeTruthy();
    playBeats(0, 6, 1);
    expect(within(stage()).queryByText("PLAYOFFS")).toBeNull();
    const final = within(stage()).getByRole("list", { name: "Final standings" });
    const rows = within(final).getAllByRole("listitem");
    expect(rows.filter((row) => within(row).queryByText("BYE")).map((row) => row.dataset.roster)).toEqual(["3", "8"]);
    expect(rows[5].dataset.cut).toBe("true");
    expect(rows.slice(6).every((row) => row.dataset.out === "true")).toBe(true);

    // The bracket draws in round by round. In the semifinal seed 1 meets the lowest seed left.
    playBeats(0, 7, 1);
    const bracket = within(stage()).getByRole("list", { name: "Bracket" });
    expect(within(bracket).getByRole("listitem", { name: "Round 1, week 15" })).toBeTruthy();
    playBeats(0, 8, 2);
    const semi = within(bracket).getByRole("listitem", { name: "Semifinal, week 16" });
    expect(within(semi).getAllByRole("group")[0].getAttribute("aria-label")).toBe(
      "Seed 1 Lil Fridge against seed 6 Maye d'force B with U",
    );

    // The champion card ends the run.
    playBeats(0, 10, 4);
    const card = within(stage()).getByRole("dialog", { name: "Champion of this run" });
    expect(card.textContent).toContain("Lil Fridge");
    expect(card.textContent).toContain("Wins the title in 14.4% of all 10,000 runs");
    expect(screen.queryByRole("button", { name: "Skip to the end" })).toBeNull();
  });

  it("names the seed of this run in the odds after the split", () => {
    render(<SimReplay sim={sim} pick={picks(0)} />);
    press();
    playBeats(0, 0, 6);
    const odds = screen.getByRole("table", { name: "The odds of all 10,000 runs" });
    const fridge = within(odds).getAllByRole("row").find((row) => row.textContent?.includes("Lil Fridge"))!;
    expect(within(fridge).getAllByRole("cell").at(-1)!.textContent).toBe("1");
  });

  it("shows the final state at once on a skip, and the bracket behind the champion card", () => {
    render(<SimReplay sim={sim} pick={picks(0)} />);
    press();
    playBeats(0, 0, 2);
    fireEvent.click(screen.getByRole("button", { name: "Skip to the end" }));
    const card = within(stage()).getByRole("dialog", { name: "Champion of this run" });
    expect(card.textContent).toContain("Wins the title in 14.4% of all 10,000 runs");
    fireEvent.click(within(card).getByRole("button", { name: "See the bracket" }));
    expect(within(stage()).queryByRole("dialog")).toBeNull();
    const final = within(stage()).getByRole("listitem", { name: "Final, week 17" });
    expect(within(final).getByRole("group").dataset.winner).toBe("3");
  });

  it("starts a clean run at week 9 on a press during a run", () => {
    render(<SimReplay sim={sim} pick={picks(0, 1)} />);
    press();
    playBeats(0, 0, 2);
    expect(within(stage()).getByRole("group", { name: "Week 11 final" })).toBeTruthy();
    press();
    expect(within(stage()).getByRole("group", { name: "Week 9 final" })).toBeTruthy();
    expect(within(stage()).queryByRole("group", { name: "Week 11 final" })).toBeNull();
    // Run 1 plays to its own champion, with no beat of run 0 left on the clock.
    playBeats(1, 0, 14);
    const card = within(stage()).getByRole("dialog", { name: "Champion of this run" });
    const champion = replaySeason(sim, 1).champion;
    expect(card.textContent).toContain(champion.name);
    expect(card.textContent).toContain(`Wins the title in ${champion.title}% of all 10,000 runs`);
  });

  it("plays a random run of the 200 when no pick is given", () => {
    vi.spyOn(Math, "random").mockReturnValue(0.5);
    render(<SimReplay sim={sim} />);
    press();
    fireEvent.click(screen.getByRole("button", { name: "Skip to the end" }));
    const card = within(stage()).getByRole("dialog", { name: "Champion of this run" });
    expect(card.textContent).toContain(replaySeason(sim, 100).champion.name);
    vi.restoreAllMocks();
  });

  it("has no control to pick the winner of a game at any beat", () => {
    render(<SimReplay sim={sim} pick={picks(0)} />);
    const allowed = new Set(["Sim the season", "Skip to the end", "See the bracket"]);
    const controls = () =>
      [...document.querySelectorAll("button, a, input, select, [role=button], [role=radio], [role=checkbox]")].map(
        (control) => control.textContent,
      );
    expect(controls().every((name) => allowed.has(name ?? ""))).toBe(true);
    press();
    for (let beat = 0; beat < 14; beat++) {
      expect(controls().every((name) => allowed.has(name ?? ""))).toBe(true);
      playBeats(0, beat, 1);
    }
    expect(controls().every((name) => allowed.has(name ?? ""))).toBe(true);
  });
});
