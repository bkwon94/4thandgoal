/**
 * Tests for the analyzer: the passphrase dialog, the teams fetch, and the two sides of the form.
 * fetch is a test stub. Each test reads the screen, the stored passphrase, and the stored teams.
 */
import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
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

/* The team picker of a side is named by the side's heading. */
const teamTrigger = (side: "Your Team" | "Team Two") => screen.getByRole("combobox", { name: side });

/* Opens a picker and returns its list. The popup renders in a portal, so the test finds it on the screen. */
async function openPicker(trigger: HTMLElement) {
  fireEvent.click(trigger);
  return screen.findByRole("listbox");
}

async function closePicker(list: HTMLElement) {
  fireEvent.keyDown(list, { key: "Escape" });
  await waitFor(() => expect(screen.queryByRole("listbox")).toBeNull());
}

/* The names in a side's team picker. The test opens the picker, reads the names, and closes it. */
async function teamNames(side: "Your Team" | "Team Two") {
  const list = await openPicker(teamTrigger(side));
  const names = within(list).getAllByRole("option").map((o) => o.textContent);
  await closePicker(list);
  return names;
}

/* Base UI commits a mouse pick only for a press that starts on the item, so the test sends the pointer down first. */
async function choose(trigger: HTMLElement, name: string) {
  const list = await openPicker(trigger);
  const option = within(list).getByRole("option", { name: new RegExp(name) });
  fireEvent.pointerDown(option, { pointerType: "mouse" });
  fireEvent.click(option);
  if (screen.queryByRole("listbox")) await closePicker(list);
}

/* Picks both teams, then Ana One or Ana Two on my side and Ben One on the other side. */
async function pickTrade() {
  await choose(teamTrigger("Your Team"), "Gridiron Ghosts");
  await choose(teamTrigger("Team Two"), "Blitz Bakers");
  const mine = screen.getByRole("combobox", { name: "Gridiron Ghosts Gives" });
  const list = await openPicker(mine);
  const hasAnaOne = within(list).queryByRole("option", { name: /Ana One/ }) !== null;
  await closePicker(list);
  await choose(mine, hasAnaOne ? "Ana One" : "Ana Two");
  await choose(screen.getByRole("combobox", { name: "Blitz Bakers Gives" }), "Ben One");
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
  it("shows the dialog and no pickers on first load", async () => {
    render(<Analyzer season={2026} finderOn={false} />);
    expect(await screen.findByRole("dialog")).toBeTruthy();
    expect(screen.queryByText("Your Team")).toBeNull();
    expect(fetchStub).not.toHaveBeenCalled();
  });

  it("fetches the teams with the header after a submit and shows both pickers", async () => {
    answer(200, TEAMS);
    render(<Analyzer season={2026} finderOn={false} />);
    await submitPassphrase("localtest");

    expect(await screen.findByText("Pick the Teams")).toBeTruthy();
    const [url, init] = fetchStub.mock.calls[0];
    expect(url).toContain("/teams?season=2026");
    expect(init.headers["X-League-Passphrase"]).toBe("localtest");
    expect(localStorage.getItem("cpc.passphrase")).toBe("localtest");
    expect(teamTrigger("Your Team").textContent).toContain("Pick a Team");
    expect(teamTrigger("Team Two").textContent).toContain("Pick a Team");
    expect(await teamNames("Your Team")).toEqual(["Gridiron GhostsAna", "Blitz BakersBen", "Punt PunksCy"]);
    expect(screen.queryByRole("dialog")).toBeNull();
  });

  it("skips the dialog when a passphrase is stored", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    answer(200, TEAMS);
    render(<Analyzer season={2026} finderOn={false} />);

    expect(await screen.findByText("Pick the Teams")).toBeTruthy();
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(fetchStub.mock.calls[0][1].headers["X-League-Passphrase"]).toBe("localtest");
  });

  it("clears the passphrase on a 401, shows the error, and fetches again after a new submit", async () => {
    localStorage.setItem("cpc.passphrase", "wrong");
    answer(401, { detail: "bad passphrase" });
    render(<Analyzer season={2026} finderOn={false} />);

    expect(await screen.findByText("That passphrase is wrong.")).toBeTruthy();
    expect(screen.getByRole("dialog")).toBeTruthy();
    expect(localStorage.getItem("cpc.passphrase")).toBeNull();

    answer(200, TEAMS);
    await submitPassphrase("localtest");
    expect(await screen.findByText("Pick the Teams")).toBeTruthy();
    expect(fetchStub).toHaveBeenCalledTimes(2);
  });

  it("shows the wait time on a 429", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    answer(429, { detail: "slow down" }, { "Retry-After": "30" });
    render(<Analyzer season={2026} finderOn={false} />);
    expect(await screen.findByText("Too many requests. Try again in 30 seconds.")).toBeTruthy();
  });

  it("shows the wait in hours on a 429 with a Retry-After over an hour", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    answer(429, { detail: "slow down" }, { "Retry-After": "50000" });
    render(<Analyzer season={2026} finderOn={false} />);
    expect(await screen.findByText("Too many requests. Try again in 14 hours.")).toBeTruthy();
  });

  it("shows skeleton rows before the teams arrive, then the pickers", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    const release = answerLater(TEAMS);
    render(<Analyzer season={2026} finderOn={false} />);

    expect(await screen.findByRole("status", { name: "Loading teams" })).toBeTruthy();
    expect(screen.queryByText("Pick the Teams")).toBeNull();

    release();
    expect(await screen.findByText("Pick the Teams")).toBeTruthy();
    expect(screen.queryByRole("status", { name: "Loading teams" })).toBeNull();
    expect(JSON.parse(sessionStorage.getItem(STORE_KEY)!).teams).toHaveLength(3);
  });

  it("shows stored teams at once, then replaces them with the fetch answer", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    storeEntry(STORED, 60_000);
    const release = answerLater(TEAMS);
    render(<Analyzer season={2026} finderOn={false} />);

    // The fetch has not answered, so the pickers come from the store.
    expect(await screen.findByText("Pick the Teams")).toBeTruthy();
    expect(await teamNames("Your Team")).toEqual(["Stored SlidersDee"]);
    expect(screen.queryByRole("status", { name: "Loading teams" })).toBeNull();
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
    render(<Analyzer season={2026} finderOn={false} />);

    expect(await screen.findByRole("status", { name: "Loading teams" })).toBeTruthy();
    expect(screen.queryByText("Stored Sliders")).toBeNull();

    release();
    expect(await screen.findByText("Pick the Teams")).toBeTruthy();
    expect(screen.queryByText("Stored Sliders")).toBeNull();
  });

  it("keeps the stored list with no error when the background fetch fails", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    storeEntry(STORED, 60_000);
    answer(500);
    render(<Analyzer season={2026} finderOn={false} />);

    expect(await screen.findByText("Pick the Teams")).toBeTruthy();
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
    render(<Analyzer season={2026} finderOn={false} />);

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
    render(<Analyzer season={2026} finderOn={false} />);
    await screen.findByText("Pick the Teams");

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
    render(<Analyzer season={2026} finderOn={false} />);
    await screen.findByText("Pick the Teams");
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
    render(<Analyzer season={2026} finderOn={false} />);
    expect(await screen.findByText("The API did not answer. Try again.")).toBeTruthy();

    answer(200, TEAMS);
    fireEvent.click(screen.getByRole("button", { name: "Try Again" }));
    expect(await screen.findByText("Pick the Teams")).toBeTruthy();
  });

  it("puts the sides in order, each with its pickers, and the grade button after the sides", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    answer(200, { teams: ROSTERS });
    render(<Analyzer season={2026} finderOn={false} />);
    await screen.findByText("Pick the Teams");
    await choose(teamTrigger("Your Team"), "Gridiron Ghosts");
    await choose(teamTrigger("Team Two"), "Blitz Bakers");

    // The two-column grid of the tablet tier places one side per column, so the document order stays the phone order.
    const parts = [
      screen.getByRole("group", { name: "Your Team" }),
      teamTrigger("Your Team"),
      screen.getByRole("combobox", { name: "Gridiron Ghosts Gives" }),
      screen.getByRole("group", { name: "Team Two" }),
      teamTrigger("Team Two"),
      screen.getByRole("combobox", { name: "Blitz Bakers Gives" }),
      submit(),
    ];
    for (let i = 1; i < parts.length; i++) {
      expect(parts[i - 1].compareDocumentPosition(parts[i]) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    }
  });

  it("leaves the team that the other side holds out of its picker", async () => {
    localStorage.setItem("cpc.passphrase", "localtest");
    answer(200, TEAMS);
    render(<Analyzer season={2026} finderOn={false} />);
    await screen.findByText("Pick the Teams");

    await choose(teamTrigger("Your Team"), "Gridiron Ghosts");
    expect(await teamNames("Team Two")).toEqual(["Blitz BakersBen", "Punt PunksCy"]);

    await choose(teamTrigger("Team Two"), "Blitz Bakers");
    expect(await teamNames("Your Team")).toEqual(["Gridiron GhostsAna", "Punt PunksCy"]);
  });
});
