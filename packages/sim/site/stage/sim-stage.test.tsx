/**
 * Tests for the replay of the sim page on the real week 10 sim file of CPC, with Bo Girds as Your team: "Sim week 11"
 * plays Games, then Standings; "Sim the season" plays Season, Playoffs, and Champion; a What-if picks a run that holds it.
 */
import "@cpc/design/ui/sheet-jsdom";
import { act, cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { weekSim } from "../fixtures/sim";
import { fakeWhatIfApi } from "../fixtures/what-if-api";
import { SimPage } from "../page/sim-page";

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  cleanup();
  // Framer Motion asks for its next frame once and waits for it, so the frame it asked for under the fake clock runs here.
  vi.advanceTimersByTime(100);
  vi.useRealTimers();
});

// Bo Girds is roster 6 in CPC. Week 11 is Bo Girds vs Maye d'force B with U.
const YOU = 6;
const OPPONENT = "Maye d'force B with U";

const stage = () => screen.getByRole("region", { name: "Sim replay" });
const controls = () => within(stage()).getByRole("group", { name: "Replay controls" });
const tab = (name: string) => within(stage()).getByRole("button", { name });
const press = (name: string) => fireEvent.click(screen.getByRole("button", { name }));

/* Moves the fake clock on and lets each effect of the replay run. */
async function wait(...holds: number[]) {
  for (const ms of holds) {
    await act(async () => {
      vi.advanceTimersByTime(ms);
    });
  }
}

/* The games of the week on the stage, each as its text. */
const games = () =>
  within(within(stage()).getByRole("list", { name: /^Week \d+ games$/ })).getAllByRole("listitem");

describe("Sim week 11", () => {
  it("plays the games with Bo Girds first and one median line, then the standings in the Race style", async () => {
    // Run 0 of the file: Bo Girds scores 100.2 and Maye d'force B with U scores 140.7. The median is 101.55.
    render(<SimPage sim={weekSim} you={YOU} random={() => 0} />);
    press("Sim week 11");
    expect(within(stage()).getByRole("list", { name: "Parts of the week" })).toBeTruthy();
    expect(tab("Games").getAttribute("aria-current")).toBe("step");
    // The part not yet played stays off.
    expect(tab("Standings").hasAttribute("disabled")).toBe(true);

    // The games play after a short hold on the draw.
    await wait(700, 1000);
    const rows = games();
    expect(rows).toHaveLength(6);
    expect(rows[0].textContent).toMatch(/^Bo Girds/);
    expect(rows[0].textContent).toContain(OPPONENT);
    expect(rows[0].textContent).toContain("100.2");
    expect(rows[0].textContent).toContain("140.7");
    const medians = within(stage()).getAllByText(/^Median /);
    expect(medians).toHaveLength(1);
    expect(medians[0].textContent).toBe("Median 101.6 · you were below");

    // The standings follow the games by themselves, then the rows move to the order after the week.
    await wait(2400, 700);
    expect(tab("Standings").getAttribute("aria-current")).toBe("step");
    const standings = within(within(stage()).getByRole("list", { name: "Standings" })).getAllByRole(
      "listitem",
    );
    // The Race style: the two byes fold into one line at the top, places 3 to 9 show in full, and 10 to 12 fold at the bottom.
    expect(standings[0].textContent).toMatch(/^1–2·byes: /);
    expect(standings.at(-1)?.textContent).toBe("10–12·out of it");
    const full = standings.slice(1, -1);
    expect(full.map((row) => row.textContent?.match(/^\d+/)?.[0])).toEqual([
      "3",
      "4",
      "5",
      "6",
      "7",
      "8",
      "9",
    ]);
    // A loss and a miss of the median take Bo Girds from 11-9 to 11-11.
    const you = full.find((row) => row.textContent?.includes("Bo Girds"));
    expect(you?.textContent).toContain("(Your team)");
    expect(you?.textContent).toContain("11-11");
    // Only the row of Your team has an avatar.
    const avatars = [
      ...within(stage()).getByRole("list", { name: "Standings" }).querySelectorAll("[data-avatar]"),
    ];
    expect(avatars.map((avatar) => avatar.closest("li")?.textContent)).toEqual([you?.textContent]);

    // The tab of a part that has played goes back to it.
    fireEvent.click(tab("Games"));
    // The part on the stage leaves before the next part comes in.
    await wait(500);
    expect(tab("Games").getAttribute("aria-current")).toBe("step");
    expect(games()[0].textContent).toMatch(/^Bo Girds/);
  });
});

describe("Sim the season", () => {
  it("plays Season, Playoffs one round at a time, then Champion, with the controls in their own row", async () => {
    // Run 0 of the file: Lil Fridge wins the title, and Bo Girds finishes 8th and misses the playoffs.
    render(<SimPage sim={weekSim} you={YOU} random={() => 0} />);
    press("Sim the season");
    expect(document.documentElement.style.overflow).toBe("hidden");
    const screens = within(stage()).getByRole("list", { name: "Screens" });
    expect(
      within(screens)
        .getAllByRole("button")
        .map((button) => button.textContent),
    ).toEqual(["Season", "Playoffs", "Champion"]);
    expect(tab("Playoffs").hasAttribute("disabled")).toBe(true);
    // The controls sit in their own row, after the body of the stage and outside it.
    const body = within(stage()).getByTestId("stage-body");
    expect(body.contains(controls())).toBe(false);
    expect(
      body.compareDocumentPosition(controls()) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
    expect(within(controls()).getByRole("button", { name: "Pause" })).toBeTruthy();
    expect(within(controls()).getByRole("button", { name: "Skip" })).toBeTruthy();
    expect(within(controls()).getByRole("button", { name: "Sim again" })).toBeTruthy();

    // The season plays week by week: after week 10, then weeks 11 to 14.
    expect(within(stage()).getByText("After week 10")).toBeTruthy();
    await wait(900);
    expect(within(stage()).getByText("Week 11")).toBeTruthy();
    fireEvent.click(within(controls()).getByRole("button", { name: "Skip" }));
    await wait(0);
    expect(within(stage()).getByText("Playoff field set")).toBeTruthy();

    // The playoffs play one round at a time.
    fireEvent.click(within(controls()).getByRole("button", { name: "Skip" }));
    await wait(0);
    expect(tab("Playoffs").getAttribute("aria-current")).toBe("step");
    const rounds = () => within(stage()).getAllByRole("region", { name: /, week 1[5-7]$/ });
    expect(rounds().map((round) => round.getAttribute("aria-label"))).toEqual(["Round 1, week 15"]);
    await wait(1500, 2000);
    expect(rounds().map((round) => round.getAttribute("aria-label"))).toEqual([
      "Semifinal, week 16",
    ]);
    await wait(800, 2000);
    expect(rounds().map((round) => round.getAttribute("aria-label"))).toEqual(["Final, week 17"]);

    // The champion, and one line on where Your team finished.
    await wait(800, 2000);
    expect(tab("Champion").getAttribute("aria-current")).toBe("step");
    expect(within(stage()).getByRole("heading", { name: "Lil Fridge" })).toBeTruthy();
    expect(
      within(stage()).getByText(/^Your team finished 8th at \d+-\d+ and missed the playoffs\.$/),
    ).toBeTruthy();
    expect(within(controls()).getByRole("button", { name: "Sim again" })).toBeTruthy();
    fireEvent.click(within(controls()).getByRole("button", { name: "Done" }));
    await wait(1000);
    expect(screen.queryByRole("region", { name: "Sim replay" })).toBeNull();
    expect(document.documentElement.style.overflow).toBe("");
  });
});

describe("the replay of a What-if", () => {
  it("plays a run where Bo Girds wins week 11 and beats the median, for each pick", async () => {
    const api = fakeWhatIfApi();
    for (const random of [0, 0.5, 0.9999]) {
      render(<SimPage sim={weekSim} you={YOU} whatIf={api} random={() => random} />);
      const card = screen.getByRole("article", { name: /^Week 11 vs / });
      fireEvent.click(
        within(within(card).getByRole("group", { name: "Results" })).getByRole("button", {
          name: /^Win, beat median/,
        }),
      );
      await wait(0);
      await wait(400);
      // The next week opens after the tap, so the reader goes back to week 11.
      fireEvent.click(
        within(screen.getByRole("navigation", { name: "Weeks" })).getByRole("button", {
          name: /^Wk 11/,
        }),
      );
      press("Sim week 11");
      fireEvent.click(within(controls()).getByRole("button", { name: "Skip" }));
      await wait(0);
      fireEvent.click(tab("Games"));
      const [mine] = games();
      const [you, them] = [...mine.querySelectorAll("[data-score]")].map((score) =>
        Number(score.textContent),
      );
      expect(mine.textContent).toMatch(/^Bo Girds/);
      expect(mine.textContent).toContain(OPPONENT);
      expect(mine.textContent).toContain("Bo Girds wins.");
      expect(you).toBeGreaterThan(them);
      expect(within(stage()).getByText(/^Median \d+\.\d · you were above$/)).toBeTruthy();
      cleanup();
    }
  });

  it("plays a loss of Bo Girds in run 0 of the file with no set result", async () => {
    // The same pick with no What-if plays run 0 of the file, where Bo Girds loses 100.2 to 140.7.
    render(<SimPage sim={weekSim} you={YOU} random={() => 0} />);
    press("Sim week 11");
    fireEvent.click(within(controls()).getByRole("button", { name: "Skip" }));
    await wait(0);
    fireEvent.click(tab("Games"));
    expect(games()[0].textContent).toContain(`${OPPONENT} wins.`);
  });
});
