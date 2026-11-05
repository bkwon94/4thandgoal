/**
 * Tests for the analyzer, the week page, the home page, the power rankings, the waiver page, and the manager page with the reduced-motion media query on. The content must show at rest at once.
 * matchMedia is a stub, and it must exist before Framer Motion first reads it, so the stub runs at the top of the file.
 * jsdom ignores opacity, so this test proves the text is present. The browser capture 12-week-off-390.png proves no motion.
 */
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";
import { apiTarget, analyzeResponse as fixtureJson } from "@cpc/analyzer/lib/fixtures/api";
import HomePage from "@/app/page";
import WeekPage from "@/app/_routes/week/page";
import type { AnalyzeResponse } from "@cpc/analyzer/lib/analyze-types";
import type { Team } from "@cpc/analyzer/lib/api";
import type { Manager } from "@cpc/managers/schema/manager-types";
import AnalyzeResult from "@cpc/analyzer/form/analyze-result";
import { managers as managersFixture } from "@cpc/managers/fixtures/managers";
import { ManagerHero } from "@cpc/managers/page/manager-hero";
import { Roster } from "@cpc/managers/page/roster";
import { SeasonSoFar } from "@cpc/managers/page/season-so-far";
import { rankings } from "@cpc/rankings/fixtures/rankings";
import { PowerRankings } from "@cpc/rankings/chapters/power-rankings";
import { TradeForm } from "@cpc/analyzer/form/trade-form";
import { waiver } from "@/fixtures/waiver";
import { WarChest } from "@cpc/waiver/war-chest";
import { TeamPicker } from "@cpc/analyzer/form/team-picker";
import { week6 } from "@cpc/week/fixtures/week-page";

vi.stubGlobal(
  "matchMedia",
  (query: string) =>
    ({
      // Framer Motion asks for "(prefers-reduced-motion)" with no value, so the stub matches the feature name.
      matches: query.includes("prefers-reduced-motion"),
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as MediaQueryList,
);

const player = (id: string, name: string) => ({
  player_id: id,
  name,
  position: "WR",
  nfl_team: "NYJ",
  headshot: `https://cdn.test/${id}.png`,
});

const TEAMS: Team[] = [
  { roster_id: 4, team: "Pukancun on 3", manager: "Ana", avatar: null, players: [player("p1", "Ana One")] },
  { roster_id: 12, team: "Blitz Bakers", manager: "Ben", avatar: null, players: [player("p3", "Ben One")] },
  { roster_id: 7, team: "Punt Punks", manager: "Cy", avatar: null, players: [player("p5", "Cy One")] },
];

/* No box from the element up to the page root fades or moves. A motion box at its start state carries opacity 0 or a translate. */
function expectAtRest(element: HTMLElement) {
  for (let box: HTMLElement | null = element; box; box = box.parentElement) {
    expect(box.style.opacity).not.toBe("0");
    expect(box.style.transform).not.toMatch(/translate/);
  }
}

/* Opens a picker with a click on its trigger and picks one item. Base UI commits a mouse pick only for a press that starts on the item. */
async function choose(trigger: HTMLElement, name: string) {
  fireEvent.click(trigger);
  const list = await screen.findByRole("listbox");
  const option = within(list).getByRole("option", { name: new RegExp(name) });
  fireEvent.pointerDown(option, { pointerType: "mouse" });
  fireEvent.click(option);
  if (screen.queryByRole("listbox")) fireEvent.keyDown(list, { key: "Escape" });
  await waitFor(() => expect(screen.queryByRole("listbox")).toBeNull());
}

afterEach(cleanup);
afterAll(() => {
  vi.unstubAllGlobals();
});

describe("Reduced motion", () => {
  it("shows the decision word at once", () => {
    render(<AnalyzeResult doc={fixtureJson as AnalyzeResponse} />);
    expect(screen.getByText("Not as is")).toBeTruthy();
  });

  it("shows the fairness line at once", () => {
    // The state is set here, so the test does not depend on the fixture state.
    const doc = fixtureJson as AnalyzeResponse;
    render(<AnalyzeResult doc={{ ...doc, fairness: { ...doc.fairness!, state: "fair", gives_more: null } }} />);
    expect(screen.getByText("Fair")).toBeTruthy();
  });

  it("shows the picked team in the trigger at once", async () => {
    render(<TradeForm teams={TEAMS} target={apiTarget} finderOn={false} passphrase="localtest" onUnauthorized={() => {}} />);
    await choose(screen.getByRole("combobox", { name: "Your Team" }), "Pukancun on 3");
    expect(screen.getByRole("combobox", { name: "Your Team" }).textContent).toContain("Pukancun on 3");
  });

  it("shows no sweep while the grade runs", async () => {
    vi.stubGlobal("fetch", vi.fn(() => new Promise(() => {})));
    render(<TradeForm teams={TEAMS} target={apiTarget} finderOn={false} passphrase="localtest" onUnauthorized={() => {}} />);
    await choose(screen.getByRole("combobox", { name: "Your Team" }), "Pukancun on 3");
    await choose(screen.getByRole("combobox", { name: "Team Two" }), "Blitz Bakers");
    await choose(screen.getByRole("combobox", { name: "Pukancun on 3 Gives" }), "Ana One");
    await choose(screen.getByRole("combobox", { name: "Blitz Bakers Gives" }), "Ben One");
    fireEvent.click(screen.getByRole("button", { name: "Grade the Trade" }));
    const status = screen.getByRole("status");
    expect(status.getAttribute("aria-busy")).toBe("true");
    // The track is aria-hidden, so the query must include hidden elements to find the sweep if it existed.
    expect(within(status).queryByRole("presentation", { hidden: true })).toBeNull();
  });
});

describe("Reduced motion on the trade form", () => {
  it("adds a side and a picked row at rest, and removes a side at once", async () => {
    render(<TradeForm teams={TEAMS} target={apiTarget} finderOn={false} passphrase="localtest" onUnauthorized={() => {}} />);
    await choose(screen.getByRole("combobox", { name: "Your Team" }), "Pukancun on 3");
    await choose(screen.getByRole("combobox", { name: "Team Two" }), "Blitz Bakers");
    fireEvent.click(screen.getByRole("button", { name: "Add a Team" }));
    expectAtRest(screen.getByRole("group", { name: "Team Three" }));

    await choose(screen.getByRole("combobox", { name: "Team Three" }), "Punt Punks");
    await choose(screen.getByRole("combobox", { name: "Punt Punks Gives" }), "Cy One");
    expectAtRest(within(screen.getByRole("list", { name: "Players Punt Punks Gives" })).getByRole("listitem"));

    fireEvent.click(screen.getByRole("button", { name: "Remove Team Three" }));
    // The exit takes the instant transition, so the side leaves by the next frame. A real exit fails the short wait.
    await waitFor(() => expect(screen.queryByRole("group", { name: "Team Three" })).toBeNull(), { timeout: 50 });
  });
});

describe("Reduced motion on the power rankings", () => {
  it("opens a card at once", async () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={week6.avatars} />);
    const button = screen.getByRole("button", { name: /Lil Fridge/ });
    fireEvent.click(button);
    expect(button.getAttribute("aria-expanded")).toBe("true");
    const panel = document.getElementById(button.getAttribute("aria-controls") ?? "")!;
    expect(panel.getAttribute("aria-hidden")).toBe("false");
    // With motion off the panel takes the instant transition, so it is at rest and fully open by the next frame.
    // The wait is far shorter than the collapse duration, so a real animation fails it.
    await waitFor(
      () => {
        expect(panel.style.opacity).toBe("1");
        expect(panel.style.height).toBe("auto");
      },
      { timeout: 50 },
    );
  });
});

describe("Reduced motion on the waiver page", () => {
  it("turns the drift off and shows the top six at once", () => {
    render(<WarChest board={waiver} teams={week6.teams} avatars={week6.avatars} TeamPicker={TeamPicker} />);
    const field = screen.getByRole("group", { name: "Top six" });
    expect(field.getAttribute("data-drift")).toBe("off");
    expect(within(field).getAllByRole("button")).toHaveLength(6);
    // With motion off a headshot takes no rise, so it sits at rest with no transform from the first render.
    for (const orb of field.querySelectorAll("[data-reveal]")) {
      expect((orb as HTMLElement).style.transform).not.toMatch(/translate/);
    }
  });
});

describe("Reduced motion on the static pages", () => {
  it("shows every week page chapter at once", async () => {
    render(await WeekPage({ params: Promise.resolve({ season: "2026", week: "week-06" }) }));
    // One line from each chapter, from the top story to next week. The text must be there on the first render.
    // The chapter rail repeats the chapter labels, so the queries stay inside the page column.
    const main = within(screen.getByRole("main"));
    expect(main.getByText("Matchup of the Week")).toBeTruthy();
    expect(main.getByText("Game Changer")).toBeTruthy();
    expect(main.getByText("WR · PIT · behold the lamb")).toBeTruthy();
    expect(main.getAllByText(week6.awards[0].title).length).toBeGreaterThan(0);
    expect(main.getByText("Position Leaders")).toBeTruthy();
    expect(main.getAllByText(week6.trades[0].sides[0].players[0].name).length).toBeGreaterThan(0);
    expect(main.getAllByRole("button", { name: /Read Recap/ })).toHaveLength(week6.matchups.length);
    expect(main.getByText("The Median Game")).toBeTruthy();
    expect(main.getByText("Standings")).toBeTruthy();
    expect(main.getByText(`Next Week · Week ${week6.week + 1}`)).toBeTruthy();
  });

  it("shows every home page row at once", () => {
    render(<HomePage />);
    expect(screen.getByRole("link", { name: /Week 6/ })).toBeTruthy();
    expect(screen.getByText("Oct 15 – Oct 19, 2026")).toBeTruthy();
  });
});

/* A fixture entry with the joined fields of the loader and playoff odds of 63 percent. */
function managerWithOdds(): Manager {
  const entry = managersFixture.managers[0] as Manager;
  return {
    ...entry,
    standing: 1,
    rank: 2,
    movement: 0,
    odds: { playoff: 63 },
    odds_change: 0,
  };
}

describe("Reduced motion on the manager page", () => {
  it("shows the final grade letter and the final playoff percent at once", async () => {
    render(<ManagerHero manager={managerWithOdds()} avatar="avatars/1.jpg" teams={12} />);
    const numbers = screen.getByRole("group", { name: "Hero Numbers" });
    const [grade, odds] = [...numbers.querySelectorAll("dt")].map((term) => term.nextElementSibling as HTMLElement);
    expect(grade.textContent).toBe("D");
    expect(odds.textContent).toBe("63%");
    // The instant transition sets the rest state by the next frame. A real motion fails the short wait.
    await waitFor(() => expectAtRest(within(grade).getByText("D")), { timeout: 50 });
    // The count never runs with motion off, so the final percent stays after a frame.
    await new Promise((done) => setTimeout(done, 50));
    expect(odds.textContent).toBe("63%");
  });

  it("shows the four slot rank lines at rest at once", async () => {
    render(<Roster manager={managerWithOdds()} teams={12} />);
    const lines = screen.getAllByRole("listitem");
    expect(lines.map((line) => line.textContent)).toEqual([
      "QB · 12th of 12 · fine",
      "RB · 9th of 12 · deep",
      "WR · 2nd of 12 · thin",
      "TE · 4th of 12 · deep",
    ]);
    await waitFor(() => lines.forEach((line) => expectAtRest(line)), { timeout: 50 });
  });

  it("shows the points line whole, with no draw in progress", async () => {
    render(<SeasonSoFar manager={managerWithOdds()} />);
    const line = screen.getByRole("img", { name: "Points per week against the league median" });
    const team = line.querySelector("[data-draw]")!;
    // A drawn path shows its full length: the first dash of the dash array is the whole normalized length.
    await waitFor(() => expect(team.getAttribute("stroke-dasharray")).toMatch(/^1(px)? /), { timeout: 50 });
    await waitFor(
      () => line.querySelectorAll("[data-result]").forEach((dot) => expect((dot as HTMLElement).style.opacity).not.toBe("0")),
      { timeout: 50 },
    );
  });
});
