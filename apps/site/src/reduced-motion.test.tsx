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
import { ManagersIndex } from "@cpc/managers/page/managers-index";
import { Roster } from "@cpc/managers/page/roster";
import { SeasonSoFar } from "@cpc/managers/page/season-so-far";
import { rankings } from "@cpc/rankings/fixtures/rankings";
import { PowerRankings } from "@cpc/rankings/chapters/power-rankings";
import { TradeForm } from "@cpc/analyzer/form/trade-form";
import { waiver } from "@/fixtures/waiver";
import { WarChest } from "@cpc/waiver/war-chest";
import { TeamPicker } from "@cpc/analyzer/form/team-picker";
import { week6, week8 } from "@cpc/week/fixtures/week-page";
import { AllMatchups } from "@cpc/week/chapters/all-matchups";

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

/* Opens the team sheet of a slot or of "+" with a click, and taps one team. */
async function pickTeam(button: string | RegExp, team: string) {
  fireEvent.click(screen.getByRole("button", { name: button }));
  fireEvent.click(within(await screen.findByRole("dialog")).getByRole("button", { name: new RegExp(team) }));
  await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
}

/* Opens the picker of a side, checks one player on the tab of the source team, and taps Done. */
async function pickPlayer(side: string, from: string, name: string) {
  fireEvent.click(screen.getByRole("button", { name: `Add a player ${side} gets` }));
  const open = within(await screen.findByRole("dialog"));
  fireEvent.click(open.getByRole("tab", { name: from }));
  fireEvent.click(open.getByRole("checkbox", { name: new RegExp(name) }));
  fireEvent.click(open.getByRole("button", { name: /^Done/ }));
  await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
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

  it("shows the picked team on its card at once", async () => {
    render(<TradeForm teams={TEAMS} target={apiTarget} finderOn={false} passphrase="localtest" onUnauthorized={() => {}} />);
    await pickTeam("Pick Your Team", "Pukancun on 3");
    const card = screen.getByRole("region", { name: "Your Team gets" });
    expect(within(card).getByText("Pukancun on 3")).toBeTruthy();
    expectAtRest(card);
  });

  it("shows the Ready halo at its level at once", async () => {
    render(<TradeForm teams={TEAMS} target={apiTarget} finderOn={false} passphrase="localtest" onUnauthorized={() => {}} />);
    await pickTeam("Pick Your Team", "Pukancun on 3");
    await pickTeam("Pick Team Two", "Blitz Bakers");
    const halo = document.querySelector<HTMLElement>("[data-halo]")!;
    // Two teams and no player: the brightness is 2 of 6 by the next render, and no box of the halo moves.
    expect(Number(halo.style.opacity)).toBeCloseTo(2 / 6, 2);
    expectAtRest(halo);
    await pickPlayer("Your Team", "Blitz Bakers", "Ben One");
    await pickPlayer("Team Two", "Pukancun on 3", "Ana One");
    expect(halo.style.opacity).toBe("1");
    expectAtRest(halo);
  });

  it("shows no sweep while the grade runs", async () => {
    vi.stubGlobal("fetch", vi.fn(() => new Promise(() => {})));
    render(<TradeForm teams={TEAMS} target={apiTarget} finderOn={false} passphrase="localtest" onUnauthorized={() => {}} />);
    await pickTeam("Pick Your Team", "Pukancun on 3");
    await pickTeam("Pick Team Two", "Blitz Bakers");
    await pickPlayer("Your Team", "Blitz Bakers", "Ben One");
    await pickPlayer("Team Two", "Pukancun on 3", "Ana One");
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
    await pickTeam("Pick Your Team", "Pukancun on 3");
    await pickTeam("Pick Team Two", "Blitz Bakers");
    await pickTeam("Add a team", "Punt Punks");
    expectAtRest(screen.getByRole("region", { name: "Team Three gets" }));

    await pickPlayer("Team Three", "Pukancun on 3", "Ana One");
    expectAtRest(within(screen.getByRole("list", { name: "Players Team Three gets" })).getByRole("listitem"));

    fireEvent.click(screen.getByRole("button", { name: "Remove Team Three" }));
    // The exit takes the instant transition, so the side leaves by the next frame. A real exit fails the short wait.
    await waitFor(() => expect(screen.queryByRole("region", { name: "Team Three gets" })).toBeNull(), { timeout: 50 });
  });
});

describe("Reduced motion on the power rankings", () => {
  it("opens and closes a ladder card at once on the Open card", () => {
    render(<PowerRankings weeks={rankings.weeks} avatars={week6.avatars} />);
    const button = screen.getByRole("button", { name: /Lil Fridge/ });
    const card = button.closest<HTMLElement>(".open-card")!;
    const panel = document.getElementById(button.getAttribute("aria-controls") ?? "")!;
    // Every duration of the drawer, the blur, the rise, and the chevron reads --oc-dur, so 0s ends each one at once.
    expect(card.style.getPropertyValue("--oc-dur")).toBe("0s");
    fireEvent.click(button);
    expect(button.getAttribute("aria-expanded")).toBe("true");
    expect(panel.hasAttribute("hidden")).toBe(false);
    // With motion off the close hides the panel in the same tap. The closed card waits on no timer.
    fireEvent.click(button);
    expect(card.dataset.open).toBe("false");
    expect(panel.getAttribute("hidden")).toBe("until-found");
  });
});

describe("Reduced motion on the Open card", () => {
  it("opens and closes a game card at once, with no height change, no blur, and no spring", () => {
    render(<AllMatchups matchups={week8.matchups} avatars={week8.avatars} managersHref="/2026/managers/" />);
    const button = screen.getAllByRole("button").find((each) => !each.hasAttribute("aria-label") && each.textContent?.includes("All You Need Is Love"))!;
    const card = button.closest<HTMLElement>(".open-card")!;
    const panel = document.getElementById(button.getAttribute("aria-controls") ?? "")!;
    // Every duration of the drawer, the blur, the rise, and the chevron reads --oc-dur, so 0s ends each one at once.
    expect(card.style.getPropertyValue("--oc-dur")).toBe("0s");
    fireEvent.click(button);
    expect(card.dataset.open).toBe("true");
    expect(panel.hasAttribute("hidden")).toBe(false);
    // With motion off the close hides the panel in the same tap. The closed card waits on no timer.
    fireEvent.click(button);
    expect(card.dataset.open).toBe("false");
    expect(panel.getAttribute("hidden")).toBe("until-found");
  });
});

describe("Reduced motion on the Index list", () => {
  it("opens and closes a row at once, with no height change, no blur, and no spring", () => {
    const managers = managersFixture.managers.map((entry, i) => ({
      ...entry,
      standing: i + 1,
      rank: i + 1,
      movement: 0,
      odds: { playoff: 50, bye: 10, seed: null, status: "open" as const },
      odds_change: 0,
    }));
    render(<ManagersIndex managers={{ season: 2026, through: 6, managers }} avatars={{}} managersHref="/2026/managers/" />);
    const list = within(screen.getByRole("list", { name: "Index List" }));
    const head = within(list.getAllByRole("listitem")[0]).getByRole("button");
    const row = head.closest<HTMLElement>(".open-card")!;
    const panel = document.getElementById(head.getAttribute("aria-controls") ?? "")!;
    // The drawer, the blur, and the rise of the row read --oc-dur, so 0s ends each one at once.
    expect(row.style.getPropertyValue("--oc-dur")).toBe("0s");
    fireEvent.click(head);
    expect(row.dataset.open).toBe("true");
    expect(panel.hasAttribute("hidden")).toBe(false);
    // With motion off the close hides the panel in the same tap. The closed row waits on no timer.
    fireEvent.click(head);
    expect(row.dataset.open).toBe("false");
    expect(panel.getAttribute("hidden")).toBe("until-found");
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

/* Every bar fill under a box shows at its width with no scale: no fill sits at 0 or grows. */
async function expectBarsAtRest(box: HTMLElement, count: number) {
  const fills = [...box.querySelectorAll<HTMLElement>("[data-bar-fill]")];
  expect(fills).toHaveLength(count);
  // The wait is far shorter than the 0.7 s growth, and a fill that grows holds a scale on its first frame.
  await new Promise((done) => setTimeout(done, 50));
  for (const fill of fills) {
    expect(fill.style.transform).not.toMatch(/scale/);
    expect(fill.style.width || fill.style.height).toMatch(/%$/);
  }
}

describe("Reduced motion on the bars", () => {
  it("shows every share bar and median bar of the week page at its width at once", async () => {
    render(await WeekPage({ params: Promise.resolve({ season: "2026", week: "week-06" }) }));
    // One share bar for the Matchup of the Week, one for each game card, and one bar for each team of the median game.
    const bars = 1 + week6.matchups.length + (week6.median?.bars.length ?? 0);
    await expectBarsAtRest(screen.getByRole("main"), bars);
  });

  it("shows every playoff odds bar of the power rankings at its width at once", async () => {
    const { container } = render(<PowerRankings weeks={rankings.weeks} avatars={week6.avatars} />);
    await expectBarsAtRest(container, container.querySelectorAll("[data-odds-bar]").length);
  });

  it("shows every budget bar of the war chest at its height at once", async () => {
    const { container } = render(
      <WarChest board={waiver} teams={week6.teams} avatars={week6.avatars} TeamPicker={TeamPicker} />,
    );
    await expectBarsAtRest(within(container).getByRole("list", { name: "Budgets" }), waiver.budgets.length);
  });
});

describe("Reduced motion on the static pages", () => {
  it("shows every week page chapter at once", async () => {
    render(await WeekPage({ params: Promise.resolve({ season: "2026", week: "week-06" }) }));
    // One line from each chapter, from the top story to next week. The text must be there on the first render.
    // The chapter rail repeats the chapter labels, so the queries stay inside the page column.
    const main = within(screen.getByRole("main"));
    expect(main.getByRole("heading", { level: 1 }).textContent).toBe("Week 06 // Matchup of the Week");
    expect(main.getByRole("region", { name: "The week in numbers" })).toBeTruthy();
    expect(main.getByText("Every game")).toBeTruthy();
    expect(main.getByRole("heading", { level: 2, name: "Game Changer" })).toBeTruthy();
    expect(main.getByText("WR · PIT · behold the lamb")).toBeTruthy();
    expect(main.getAllByText(week6.awards[0].title).length).toBeGreaterThan(0);
    expect(main.getByText("Position leaders")).toBeTruthy();
    expect(main.getAllByText(week6.trades[0].sides[0].players[0].name).length).toBeGreaterThan(0);
    // The award and trade cards are Open cards too, so the count of game cards stays inside Every game.
    const games = within(main.getByRole("region", { name: "Every game" }));
    expect(games.getAllByRole("button", { expanded: false, name: /\d/ })).toHaveLength(week6.matchups.length);
    expect(main.getByText("The median game")).toBeTruthy();
    expect(main.getByText("Standings")).toBeTruthy();
    expect(main.getByText("Next week")).toBeTruthy();
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
    odds: { playoff: 63, bye: 20, seed: 3, status: "open" },
    odds_change: 0,
  };
}

describe("Reduced motion on the manager page", () => {
  it("shows the final grade letter and the final playoff percent at once", async () => {
    render(<ManagerHero manager={managerWithOdds()} avatar="avatars/1.jpg" teams={12} />);
    const numbers = screen.getByRole("group", { name: "Hero Numbers" });
    const odds = numbers.children[0].children[1] as HTMLElement;
    const grade = screen.getByRole("button", { name: /^Grade D/ });
    expect(grade.textContent).toBe("D");
    expect(odds.textContent).toBe("63%");
    // The instant transition sets the rest state by the next frame. A real motion fails the short wait.
    await waitFor(() => expectAtRest(grade), { timeout: 50 });
    // The count never runs with motion off, so the final percent stays after a frame.
    await new Promise((done) => setTimeout(done, 50));
    expect(odds.textContent).toBe("63%");
  });

  it("shows the four slot tiles at rest at once", async () => {
    render(<Roster manager={managerWithOdds()} teams={12} />);
    const lines = within(screen.getByRole("list", { name: "Slot Ranks" })).getAllByRole("listitem");
    expect(lines.map((line) => line.textContent)).toEqual([
      "QB12thof 12 · fine",
      "RB9thof 12 · deep",
      "WR2ndof 12 · thin",
      "TE4thof 12 · deep",
    ]);
    await waitFor(() => lines.forEach((line) => expectAtRest(line)), { timeout: 50 });
  });

  it("shows the points line whole, with no draw in progress", async () => {
    render(<SeasonSoFar manager={managerWithOdds()} teams={12} />);
    const line = screen.getByRole("img", { name: "Points per week against the league median" });
    const team = line.querySelector("[data-draw]")!;
    // A drawn path shows its full length: the first dash of the dash array is the whole normalized length.
    await waitFor(() => expect(team.getAttribute("stroke-dasharray")).toMatch(/^1(px)? /), { timeout: 50 });
    await waitFor(
      () => line.querySelectorAll("[data-result]").forEach((dot) => expect((dot as HTMLElement).style.opacity).not.toBe("0")),
      { timeout: 50 },
    );
  });

  it("shows each arc of the Grade dial lit at once, with no wait and no stagger", async () => {
    render(<SeasonSoFar manager={managerWithOdds()} teams={12} />);
    const dial = screen.getByRole("list", { name: "Grade Dial" });
    const arcs = within(dial).getAllByRole("img");
    const lit = () => arcs.map((arc) => arc.querySelectorAll('[data-blade][data-on="true"]').length);
    // The fixture entry ranks 1st, 4th, 7th, and 10th on the four parts.
    expect(lit()).toEqual([12, 9, 6, 3]);
    // The dial never darkens the lit blades to wait for the view, and no blade carries a stagger delay.
    await new Promise((done) => setTimeout(done, 50));
    expect(dial.hasAttribute("data-wait")).toBe(false);
    expect(lit()).toEqual([12, 9, 6, 3]);
    dial.querySelectorAll<SVGElement>("[data-blade]").forEach((blade) => expect(blade.style.transitionDelay).toBe(""));
  });
});
