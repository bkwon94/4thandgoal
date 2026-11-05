/**
 * Tests for the analyzer: the passphrase dialog, the teams fetch, and the empty Stack under them.
 * fetch is a test stub. Each test reads the screen, the stored passphrase, and the stored teams.
 */
import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { apiTarget } from "../lib/fixtures/api";
import { Analyzer } from "./analyzer";

const TEAMS = {
  teams: [
    { roster_id: 1, team: "Gridiron Ghosts", manager: "Ana", avatar: null, players: [] },
    { roster_id: 2, team: "Blitz Bakers", manager: "Ben", avatar: "https://cdn.test/b.png", players: [] },
    { roster_id: 3, team: "Punt Punks", manager: "Cy", players: [] },
  ],
};

const fetchStub = vi.fn();

function answer(status: number, body: unknown = {}, headers: Record<string, string> = {}) {
  fetchStub.mockResolvedValueOnce(new Response(JSON.stringify(body), { status, headers }));
}

/* A fetch answer that waits until the test calls the returned function, so the test can read the screen mid-load. */
function answerLater(body: unknown) {
  let release: () => void = () => {};
  fetchStub.mockReturnValueOnce(
    new Promise<Response>((resolve) => {
      release = () => resolve(new Response(JSON.stringify(body), { status: 200 }));
    }),
  );
  return () => release();
}

const STORE_KEY = "cpc.teams.2026";

function storeEntry(teams: unknown[], ageMs: number) {
  sessionStorage.setItem(STORE_KEY, JSON.stringify({ storedAt: Date.now() - ageMs, teams }));
}

const STORED = [{ roster_id: 9, team: "Stored Sliders", manager: "Dee", avatar: null, players: [] }];

const player = (id: string, name: string) => ({ player_id: id, name, position: "WR", nfl_team: "NYJ", headshot: "" });

/* Two teams with players, for the tests that pick a trade. */
const ROSTERS = [
  { roster_id: 1, team: "Gridiron Ghosts", manager: "Ana", avatar: null, players: [player("p2", "Ana Two")] },
  { roster_id: 2, team: "Blitz Bakers", manager: "Ben", avatar: null, players: [player("p3", "Ben One")] },
];

const submit = () => screen.getByRole("button", { name: "Grade the Trade" }) as HTMLButtonElement;

type SideTitle = "Your Team" | "Team Two";
/* The slot of a side in the teams row. Its name says the team once picked. */
const slot = (side: SideTitle) => screen.getByRole("button", { name: new RegExp(`^(Pick ${side}|${side}: )`) }) as HTMLButtonElement;

/* The teams arrive when the slots turn on. */
async function formReady() {
  await waitFor(() => expect(slot("Your Team").disabled).toBe(false));
}

/* The rows of the team sheet of a side. The test opens the sheet, reads each row, and closes it. */
async function teamNames(side: SideTitle) {
  fireEvent.click(slot(side));
  const rows = within(await screen.findByRole("list", { name: "Teams" })).getAllByRole("button");
  const names = rows.filter((r) => !(r as HTMLButtonElement).disabled).map((r) => r.textContent);
  fireEvent.click(within(screen.getByRole("dialog")).getByRole("button", { name: "Close" }));
  await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
  return names;
}

async function pickTeam(side: SideTitle, team: string) {
  fireEvent.click(slot(side));
  fireEvent.click(within(await screen.findByRole("dialog")).getByRole("button", { name: new RegExp(team) }));
  await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
}

/* Opens the picker of a side, checks the first player of the list that matches, and taps Done. */
async function pickPlayer(side: SideTitle, ...names: string[]) {
  fireEvent.click(screen.getByRole("button", { name: `Add a player ${side} gets` }));
  const open = within(await screen.findByRole("dialog"));
  const name = names.find((n) => open.queryByRole("checkbox", { name: new RegExp(n) }))!;
  fireEvent.click(open.getByRole("checkbox", { name: new RegExp(name) }));
  fireEvent.click(open.getByRole("button", { name: /^Done/ }));
  await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
}

/* Picks both teams, then Ben One for my side and Ana One or Ana Two for the other side. */
async function pickTrade() {
  await pickTeam("Your Team", "Gridiron Ghosts");
  await pickTeam("Team Two", "Blitz Bakers");
  await pickPlayer("Your Team", "Ben One");
  await pickPlayer("Team Two", "Ana One", "Ana Two");
}

beforeEach(() => {
  localStorage.clear();
  sessionStorage.clear();
  fetchStub.mockReset();
  vi.stubGlobal("fetch", fetchStub);
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

async function submitPassphrase(value: string) {
  fireEvent.change(await screen.findByLabelText("Passphrase"), { target: { value } });
  fireEvent.click(screen.getByRole("button", { name: "Continue" }));
}

describe("Analyzer", () => {
  it("shows the dialog over the empty Stack on first load, with each control off", async () => {
    render(<Analyzer target={apiTarget} finderOn={false} />);
    expect(await screen.findByRole("dialog")).toBeTruthy();
    // The modal dialog hides the page from the accessibility tree, so these queries take hidden elements too.
    expect(screen.getByRole("heading", { level: 1, name: "Trade Analyzer", hidden: true })).toBeTruthy();
    expect(screen.getByText("2 of 4")).toBeTruthy();
    expect((screen.getByRole("button", { name: "Pick Your Team", hidden: true }) as HTMLButtonElement).disabled).toBe(true);
    expect((screen.getByRole("button", { name: "Grade the Trade", hidden: true }) as HTMLButtonElement).disabled).toBe(true);
    expect(fetchStub).not.toHaveBeenCalled();
  });

  it("fetches the teams with the header after a submit and shows both pickers", async () => {
    answer(200, TEAMS);
    render(<Analyzer target={apiTarget} finderOn={false} />);
    await submitPassphrase("localtest");

    await formReady();
    const [url, init] = fetchStub.mock.calls[0];
    expect(url).toBe("https://api.example.test/clients/cpc/teams?season=2026");
    expect(init.headers["X-League-Passphrase"]).toBe("localtest");
    expect(localStorage.getItem("cpc.passphrase")).toBe("localtest");
    expect(slot("Your Team").getAttribute("aria-label")).toBe("Pick Your Team");
    expect(slot("Team Two").getAttribute("aria-label")).toBe("Pick Team Two");
    expect(await teamNames("Your Team")).toEqual(["Gridiron GhostsAna", "Blitz BakersBen", "Punt PunksCy"]);
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("skips the dialog when a passphrase is stored", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    answer(200, TEAMS);
    render(<Analyzer target={apiTarget} finderOn={false} />);

    await formReady();
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(fetchStub.mock.calls[0][1].headers["X-League-Passphrase"]).toBe("localtest");
  });

  it("clears the passphrase on a 401, shows the error, and fetches again after a new submit", async () => {
    localStorage.setItem("cpc.passphrase", "wrong");
    answer(401, { detail: "bad passphrase" });
    render(<Analyzer target={apiTarget} finderOn={false} />);

    expect(await screen.findByText("That passphrase is wrong.")).toBeTruthy();
    expect(screen.getByRole("dialog")).toBeTruthy();
    expect(localStorage.getItem("cpc.passphrase")).toBeNull();

    answer(200, TEAMS);
    await submitPassphrase("localtest");
    await formReady();
    expect(fetchStub).toHaveBeenCalledTimes(2);
  });

  it("shows the wait time on a 429", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    answer(429, { detail: "slow down" }, { "Retry-After": "30" });
    render(<Analyzer target={apiTarget} finderOn={false} />);
    expect(await screen.findByText("Too many requests. Try again in 30 seconds.")).toBeTruthy();
  });

  it("shows the wait in hours on a 429 with a Retry-After over an hour", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    answer(429, { detail: "slow down" }, { "Retry-After": "50000" });
    render(<Analyzer target={apiTarget} finderOn={false} />);
    expect(await screen.findByText("Too many requests. Try again in 14 hours.")).toBeTruthy();
  });

  it("shows the loading line and the Stack off before the teams arrive, then turns the Stack on", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    const release = answerLater(TEAMS);
    render(<Analyzer target={apiTarget} finderOn={false} />);

    expect(await screen.findByText("Loading the teams…")).toBeTruthy();
    expect(slot("Your Team").disabled).toBe(true);

    release();
    await formReady();
    expect(screen.queryByText("Loading the teams…")).toBeNull();
    expect(JSON.parse(sessionStorage.getItem(STORE_KEY)!).teams).toHaveLength(3);
  });

  it("shows stored teams at once, then replaces them with the fetch answer", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    storeEntry(STORED, 60_000);
    const release = answerLater(TEAMS);
    render(<Analyzer target={apiTarget} finderOn={false} />);

    // The fetch has not answered, so the pickers come from the store.
    await formReady();
    expect(await teamNames("Your Team")).toEqual(["Stored SlidersDee"]);
    expect(screen.queryByText("Loading the teams…")).toBeNull();
    expect(fetchStub).toHaveBeenCalledTimes(1);

    release();
    await waitFor(() => expect(JSON.parse(sessionStorage.getItem(STORE_KEY)!).teams).toHaveLength(3));
    expect(await teamNames("Your Team")).toEqual(["Gridiron GhostsAna", "Blitz BakersBen", "Punt PunksCy"]);
    expect(JSON.parse(sessionStorage.getItem(STORE_KEY)!).teams[0].team).toBe("Gridiron Ghosts");
  });

  it("ignores a stored entry older than 5 minutes", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    storeEntry(STORED, 6 * 60_000);
    const release = answerLater(TEAMS);
    render(<Analyzer target={apiTarget} finderOn={false} />);

    expect(await screen.findByText("Loading the teams…")).toBeTruthy();
    expect(screen.queryByText("Stored Sliders")).toBeNull();

    release();
    await formReady();
    expect(screen.queryByText("Stored Sliders")).toBeNull();
  });

  it("keeps the stored list with no error when the background fetch fails", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    storeEntry(STORED, 60_000);
    answer(500);
    render(<Analyzer target={apiTarget} finderOn={false} />);

    await formReady();
    await waitFor(() => expect(fetchStub).toHaveBeenCalledTimes(1));
    // The failed answer settles in a later task, so the test lets it land before it reads the screen.
    await act(() => new Promise((resolve) => setTimeout(resolve, 0)));
    expect(await teamNames("Team Two")).toEqual(["Stored SlidersDee"]);
    expect(screen.queryByText("The API did not answer. Try again.")).toBeNull();
    expect(screen.queryByRole("button", { name: "Try Again" })).toBeNull();
  });

  it("asks for the passphrase again on a 401 during the background fetch", async () => {
    localStorage.setItem("cpc.passphrase", "wrong");
    storeEntry(STORED, 60_000);
    answer(401, { detail: "bad passphrase" });
    render(<Analyzer target={apiTarget} finderOn={false} />);

    expect(await screen.findByText("That passphrase is wrong.")).toBeTruthy();
    expect(screen.getByRole("dialog")).toBeTruthy();
    expect(localStorage.getItem("cpc.passphrase")).toBeNull();
  });

  it("drops a stored pick when the fresh roster no longer has the player", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    storeEntry(
      [
        { ...ROSTERS[0], players: [player("p1", "Ana One"), player("p2", "Ana Two")] },
        ROSTERS[1],
      ],
      60_000,
    );
    const release = answerLater({ teams: ROSTERS });
    render(<Analyzer target={apiTarget} finderOn={false} />);
    await formReady();

    await pickTrade();
    expect(screen.getByRole("button", { name: "Remove Ana One" })).toBeTruthy();
    expect(submit().disabled).toBe(false);

    // The fresh roster lost Ana One in a trade.
    release();
    await waitFor(() => expect(screen.queryByRole("button", { name: "Remove Ana One" })).toBeNull());
    expect(screen.queryByRole("button", { name: "Remove Ana Two" })).toBeNull();
    expect(screen.getByRole("button", { name: "Remove Ben One" })).toBeTruthy();
    // My side gives nobody now, so the form cannot submit.
    expect(submit().disabled).toBe(true);
  });

  it("clears the store and fetches the teams again on a 422 from analyze", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    answer(200, { teams: ROSTERS });
    render(<Analyzer target={apiTarget} finderOn={false} />);
    await formReady();
    expect(sessionStorage.getItem(STORE_KEY)).not.toBeNull();

    await pickTrade();
    answer(422, { detail: { message: "Ana Two is not on that roster.", player_id: "p2" } });
    const release = answerLater({ teams: ROSTERS });
    fireEvent.click(submit());

    expect(await screen.findByText("Ana Two is not on that roster.")).toBeTruthy();
    await waitFor(() => expect(fetchStub).toHaveBeenCalledTimes(3));
    expect(fetchStub.mock.calls[2][0]).toContain("/teams?season=2026");
    expect(sessionStorage.getItem(STORE_KEY)).toBeNull();

    release();
    await waitFor(() => expect(sessionStorage.getItem(STORE_KEY)).not.toBeNull());
    // The form keeps its error line while the fresh rosters arrive.
    expect(screen.getByText("Ana Two is not on that roster.")).toBeTruthy();
  });

  it("shows a retry button when the API fails, and the button fetches again", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    answer(500);
    render(<Analyzer target={apiTarget} finderOn={false} />);
    expect(await screen.findByText("The API did not answer. Try again.")).toBeTruthy();

    answer(200, TEAMS);
    fireEvent.click(screen.getByRole("button", { name: "Try Again" }));
    await formReady();
  });

  it("puts the hero, the teams row, the cards in order, and the line before the grade bar", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    answer(200, { teams: ROSTERS });
    render(<Analyzer target={apiTarget} finderOn={false} />);
    await formReady();
    await pickTeam("Your Team", "Gridiron Ghosts");
    await pickTeam("Team Two", "Blitz Bakers");

    // The two-column grid of the tablet tier places one card per column, so the document order stays the phone order.
    const parts = [
      screen.getByRole("heading", { level: 1, name: "Trade Analyzer" }),
      screen.getByRole("list", { name: "Teams in the trade" }),
      screen.getByRole("region", { name: "Your Team gets" }),
      screen.getByRole("region", { name: "Team Two gets" }),
      screen.getByText("Each team gives and gets at least one player."),
      submit(),
    ];
    for (let i = 1; i < parts.length; i++) {
      expect(parts[i - 1].compareDocumentPosition(parts[i]) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    }
  });

  it("dims the team that the other side holds in its team sheet", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    answer(200, TEAMS);
    render(<Analyzer target={apiTarget} finderOn={false} />);
    await formReady();

    await pickTeam("Your Team", "Gridiron Ghosts");
    expect(await teamNames("Team Two")).toEqual(["Blitz BakersBen", "Punt PunksCy"]);

    await pickTeam("Team Two", "Blitz Bakers");
    expect(await teamNames("Your Team")).toEqual(["Gridiron GhostsAna", "Punt PunksCy"]);
  });
});
