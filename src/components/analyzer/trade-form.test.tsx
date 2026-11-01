/**
 * Tests for the trade form: the team and player pickers, the submit gate, the post body, and each error state.
 * fetch is a test stub, and each test reads the screen. A test opens a picker with a click on its trigger.
 */
import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import fixtureJson from "../../../.scratch/site-react/fixtures/analyze-response.json";
import findJson from "../../../.scratch/site-react/fixtures/find-response.json";
import type { Team } from "@/lib/api";
import { TradeForm } from "./trade-form";

// The finder flag is a prop from the page, so each render passes the flag the test sets.
let finderOn = false;

const player = (id: string, name: string) => ({
  player_id: id,
  name,
  position: "WR",
  nfl_team: "NYJ",
  headshot: `https://cdn.test/${id}.png`,
});

const TEAMS: Team[] = [
  { roster_id: 4, team: "Pukancun on 3", manager: "Ana", avatar: "https://cdn.test/ana.png", players: [player("p1", "Ana One"), player("p2", "Ana Two")] },
  { roster_id: 12, team: "Blitz Bakers", manager: "Ben", avatar: null, players: [player("p3", "Ben One"), player("p4", "Ben Two")] },
  { roster_id: 7, team: "Punt Punks", manager: "Cy", avatar: null, players: [player("p5", "Cy One")] },
];

const fetchStub = vi.fn();
const onUnauthorized = vi.fn();

function answer(status: number, body: unknown = {}, headers: Record<string, string> = {}) {
  fetchStub.mockResolvedValueOnce(new Response(JSON.stringify(body), { status, headers }));
}

const group = (name: string) => screen.getByRole("group", { name });
type SideTitle = "Your Team" | "Team Two" | "Team Three" | "Team Four";
/* The team picker of a side is named by the side's heading. */
const teamTrigger = (side: SideTitle) => screen.getByRole("combobox", { name: side });
const playerTrigger = (team: string) => screen.getByRole("combobox", { name: `${team} Gives` });
const submit = () => screen.getByRole("button", { name: "Grade the Trade" }) as HTMLButtonElement;

/* Opens a picker and returns its list. The popup renders in a portal, so the test finds it on the screen. */
async function openPicker(trigger: HTMLElement) {
  fireEvent.click(trigger);
  return screen.findByRole("listbox");
}

/* Base UI commits a mouse pick only for a press that starts on the item, so the test sends the pointer down first. */
function choose(option: HTMLElement) {
  fireEvent.pointerDown(option, { pointerType: "mouse" });
  fireEvent.click(option);
}

async function closePicker(list: HTMLElement) {
  fireEvent.keyDown(list, { key: "Escape" });
  await waitFor(() => expect(screen.queryByRole("listbox")).toBeNull());
}

async function pickTeam(side: SideTitle, team: string) {
  const list = await openPicker(teamTrigger(side));
  choose(within(list).getByRole("option", { name: new RegExp(team) }));
  await waitFor(() => expect(screen.queryByRole("listbox")).toBeNull());
}

async function pickPlayers(team: string, ...names: string[]) {
  const list = await openPicker(playerTrigger(team));
  for (const name of names) choose(within(list).getByRole("option", { name: new RegExp(name) }));
  await closePicker(list);
}

const removeButton = (name: string) => screen.getByRole("button", { name: `Remove ${name}` }) as HTMLButtonElement;

const addButton = () => screen.queryByRole("button", { name: "Add a Team" });

/* The row of a picked player, found by the list of the team that gives him. */
const row = (team: string, name: string) =>
  within(screen.getByRole("list", { name: `Players ${team} Gives` }))
    .getAllByRole("listitem")
    .find((item) => item.textContent!.includes(name))!;
const toTrigger = (team: string, name: string) => within(row(team, name)).getByRole("combobox", { name: "To" });

/* Picks my team and the other team, then one player on each side. */
async function pickTrade() {
  await pickTeam("Your Team", "Pukancun on 3");
  await pickTeam("Team Two", "Blitz Bakers");
  await pickPlayers("Pukancun on 3", "Ana One");
  await pickPlayers("Blitz Bakers", "Ben Two");
}

beforeEach(() => {
  fetchStub.mockReset();
  onUnauthorized.mockReset();
  vi.stubGlobal("fetch", fetchStub);
  render(<TradeForm teams={TEAMS} season={2026} finderOn={finderOn} passphrase="localtest" onUnauthorized={onUnauthorized} />);
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

describe("TradeForm", () => {
  it("shows each team with its avatar and name in the team picker", async () => {
    expect(teamTrigger("Your Team").textContent).toContain("Pick a Team");
    const list = await openPicker(teamTrigger("Your Team"));
    const options = within(list).getAllByRole("option");
    expect(options.map((o) => o.textContent)).toEqual(["Pukancun on 3Ana", "Blitz BakersBen", "Punt PunksCy"]);
    expect(options[0].querySelector("img")!.getAttribute("src")).toBe("https://cdn.test/ana.png");
    // A team with no avatar shows the default image.
    expect(options[1].querySelector("img")!.getAttribute("src")).toContain("/images/avatar-default.svg");
  });

  it("shows the picked team's avatar and name in the trigger", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    const trigger = teamTrigger("Your Team");
    expect(trigger.textContent).toContain("Pukancun on 3");
    expect(trigger.querySelector("img")!.getAttribute("src")).toBe("https://cdn.test/ana.png");
  });

  it("closes the player list on Escape and keeps the picks", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    const list = await openPicker(playerTrigger("Pukancun on 3"));
    choose(within(list).getByRole("option", { name: /Ana One/ }));
    choose(within(list).getByRole("option", { name: /Ana Two/ }));
    // A pick keeps the multi-select open, so Escape is one way out.
    expect(screen.getByRole("listbox")).toBeTruthy();
    fireEvent.keyDown(list, { key: "Escape" });
    await waitFor(() => expect(screen.queryByRole("listbox")).toBeNull());
    expect(playerTrigger("Pukancun on 3").textContent).toContain("2 Players");
    expect(row("Pukancun on 3", "Ana One")).toBeTruthy();
    expect(row("Pukancun on 3", "Ana Two")).toBeTruthy();
  });

  it("swaps a failed avatar to the default image once", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    const img = teamTrigger("Your Team").querySelector("img")!;
    fireEvent.error(img);
    expect(img.getAttribute("src")).toContain("/images/avatar-default.svg");
  });

  it("leaves a team picked on one side out of the other side's picker", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    const list = await openPicker(teamTrigger("Team Two"));
    const names = within(list).getAllByRole("option").map((o) => o.textContent);
    expect(names).toEqual(["Blitz BakersBen", "Punt PunksCy"]);
  });

  it("titles each side in title case, with my side first", () => {
    const headings = screen.getAllByRole("heading", { level: 3 }).map((h) => h.textContent);
    expect(headings).toEqual(["Your Team", "Team Two"]);
    expect(group("Your Team")).toBeTruthy();
    expect(group("Team Two")).toBeTruthy();
  });

  it("shows the player picker once the side has a team, with each player's headshot, name, position, and NFL team", async () => {
    expect(screen.queryByRole("combobox", { name: "Pukancun on 3 Gives" })).toBeNull();
    await pickTeam("Your Team", "Pukancun on 3");
    expect(playerTrigger("Pukancun on 3").textContent).toContain("Pick Players");
    const list = await openPicker(playerTrigger("Pukancun on 3"));
    const options = within(list).getAllByRole("option");
    expect(options.map((o) => o.textContent)).toEqual(["Ana OneWR NYJ", "Ana TwoWR NYJ"]);
    expect(options[0].querySelector("img")!.getAttribute("src")).toBe("https://cdn.test/p1.png");
  });

  it("swaps a failed headshot to the default image once", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    const list = await openPicker(playerTrigger("Pukancun on 3"));
    const img = within(list).getAllByRole("option")[0].querySelector("img")!;
    fireEvent.error(img);
    expect(img.getAttribute("src")).toContain("/images/headshot-default.svg");
  });

  it("shows the picked players as rows with a remove control, and the count in the trigger", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    await pickPlayers("Pukancun on 3", "Ana Two", "Ana One");
    expect(playerTrigger("Pukancun on 3").textContent).toContain("2 Players");
    const rows = within(screen.getByRole("list", { name: "Players Pukancun on 3 Gives" })).getAllByRole("listitem");
    expect(rows.map((r) => r.textContent)).toEqual(["Ana TwoWR NYJ", "Ana OneWR NYJ"]);
    expect(rows[0].querySelector("img")!.getAttribute("src")).toBe("https://cdn.test/p2.png");

    fireEvent.click(removeButton("Ana Two"));
    // The row animates out, so it leaves the page a moment after the click.
    await waitFor(() => expect(screen.queryByRole("button", { name: "Remove Ana Two" })).toBeNull());
    expect(playerTrigger("Pukancun on 3").textContent).toContain("1 Player");
  });

  it("keeps submit off until each side gives a player", async () => {
    expect(submit().disabled).toBe(true);
    await pickTeam("Your Team", "Pukancun on 3");
    await pickTeam("Team Two", "Blitz Bakers");
    await pickPlayers("Pukancun on 3", "Ana One");
    expect(submit().disabled).toBe(true);
    await pickPlayers("Blitz Bakers", "Ben Two");
    expect(submit().disabled).toBe(false);
    fireEvent.click(removeButton("Ben Two"));
    expect(submit().disabled).toBe(true);
  });

  it("clears the picks of a side when its team changes, and keeps the other side's picks", async () => {
    await pickTrade();
    await pickTeam("Team Two", "Punt Punks");
    expect(submit().disabled).toBe(true);
    await waitFor(() => expect(screen.queryByRole("button", { name: "Remove Ben Two" })).toBeNull());
    expect(playerTrigger("Punt Punks").textContent).toContain("Pick Players");
    expect(removeButton("Ana One")).toBeTruthy();
  });

  it("clears the result when a side's team changes", async () => {
    answer(200, fixtureJson);
    await pickTrade();
    fireEvent.click(submit());
    await screen.findByText("Not as is");
    await pickTeam("Your Team", "Punt Punks");
    expect(screen.queryByText("Not as is")).toBeNull();
  });

  it("posts the asker first, with the destination of each player", async () => {
    answer(200, fixtureJson);
    await pickTrade();
    fireEvent.click(submit());
    await screen.findByText("Not as is");

    const [url, init] = fetchStub.mock.calls[0];
    expect(url).toContain("/analyze");
    expect(init.method).toBe("POST");
    expect(init.headers["X-League-Passphrase"]).toBe("localtest");
    expect(init.headers["Content-Type"]).toBe("application/json");
    expect(JSON.parse(init.body)).toEqual({
      season: 2026,
      asker: 4,
      sides: [
        { roster_id: 4, gives: [{ player_id: "p1", to: 12 }] },
        { roster_id: 12, gives: [{ player_id: "p4", to: 4 }] },
      ],
    });
  });

  it("points my picks at the other side's new team", async () => {
    answer(200, fixtureJson);
    await pickTeam("Your Team", "Pukancun on 3");
    await pickTeam("Team Two", "Blitz Bakers");
    await pickPlayers("Pukancun on 3", "Ana One");
    await pickTeam("Team Two", "Punt Punks");
    await pickPlayers("Punt Punks", "Cy One");
    fireEvent.click(submit());
    await screen.findByText("Not as is");
    expect(JSON.parse(fetchStub.mock.calls[0][1].body).sides).toEqual([
      { roster_id: 4, gives: [{ player_id: "p1", to: 7 }] },
      { roster_id: 7, gives: [{ player_id: "p5", to: 4 }] },
    ]);
  });

  it("counts a grade event on submit", async () => {
    const count = vi.fn();
    window.goatcounter = { count };
    answer(200, fixtureJson);
    await pickTrade();
    fireEvent.click(submit());
    await screen.findByText("Not as is");
    expect(count).toHaveBeenCalledWith({ path: "analyze-grade", event: true });
    delete window.goatcounter;
  });

  it("shows the loading line while the grade runs", async () => {
    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    await pickTrade();
    fireEvent.click(submit());
    expect(await screen.findByText("Grading the Trade")).toBeTruthy();
    expect(screen.getByText("This can take up to a minute on a new chart week.")).toBeTruthy();
    const busy = screen.getByRole("button", { name: "Grading…" }) as HTMLButtonElement;
    expect(busy.disabled).toBe(true);
    expect(busy.getAttribute("aria-busy")).toBe("true");
  });

  it("locks the pickers and the remove controls while the grade runs, and unlocks them on the result", async () => {
    let finish!: (response: Response) => void;
    fetchStub.mockReturnValueOnce(new Promise<Response>((resolve) => (finish = resolve)));
    await pickTrade();
    fireEvent.click(submit());
    await screen.findByText("Grading the Trade");

    const triggers = [teamTrigger("Your Team"), teamTrigger("Team Two"), playerTrigger("Pukancun on 3"), playerTrigger("Blitz Bakers")];
    expect(triggers.every((t) => (t as HTMLButtonElement).disabled)).toBe(true);
    fireEvent.click(playerTrigger("Pukancun on 3"));
    expect(screen.queryByRole("listbox")).toBeNull();
    expect(removeButton("Ana One").disabled).toBe(true);
    fireEvent.click(removeButton("Ana One"));
    expect(removeButton("Ana One")).toBeTruthy();

    await act(async () => finish(new Response(JSON.stringify(fixtureJson), { status: 200 })));
    await screen.findByText("Not as is");
    expect(triggers.some((t) => (t as HTMLButtonElement).disabled)).toBe(false);
    expect(submit().hasAttribute("aria-busy")).toBe(false);
    await pickPlayers("Pukancun on 3", "Ana Two");
    expect(removeButton("Ana Two")).toBeTruthy();
  });

  it("unlocks the pickers after a 422, so a tap fixes the trade", async () => {
    answer(422, { detail: { message: "Player p1 is not on the giving roster.", player_id: "p1" } });
    await pickTrade();
    fireEvent.click(submit());
    await screen.findByText("Player p1 is not on the giving roster.");
    expect(removeButton("Ana One").disabled).toBe(false);
    fireEvent.click(removeButton("Ana One"));
    await waitFor(() => expect(screen.queryByRole("button", { name: "Remove Ana One" })).toBeNull());
    expect((teamTrigger("Team Two") as HTMLButtonElement).disabled).toBe(false);
  });

  it("unlocks the pickers after a 429", async () => {
    answer(429, { detail: "slow down" }, { "Retry-After": "12" });
    await pickTrade();
    fireEvent.click(submit());
    await screen.findByText("Too many requests. Try again in 12 seconds.");
    await pickPlayers("Pukancun on 3", "Ana Two");
    expect(removeButton("Ana Two")).toBeTruthy();
  });

  it("clears the old result when a new submit starts", async () => {
    answer(200, fixtureJson);
    await pickTrade();
    fireEvent.click(submit());
    await screen.findByText("Not as is");

    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    fireEvent.click(submit());
    await screen.findByText("Grading the Trade");
    expect(screen.queryByText("Not as is")).toBeNull();
  });

  it("shows the API message on a 422", async () => {
    answer(422, { detail: { message: "Player p1 is not on the giving roster.", player_id: "p1" } });
    await pickTrade();
    fireEvent.click(submit());
    expect(await screen.findByText("Player p1 is not on the giving roster.")).toBeTruthy();
  });

  it("shows the wait time on a 429", async () => {
    answer(429, { detail: "slow down" }, { "Retry-After": "12" });
    await pickTrade();
    fireEvent.click(submit());
    expect(await screen.findByText("Too many requests. Try again in 12 seconds.")).toBeTruthy();
  });

  it("shows the down line and a retry button on a 503 with no detail", async () => {
    answer(503);
    await pickTrade();
    fireEvent.click(submit());
    expect(await screen.findByText("The analyzer is down for the moment. Try again in a few minutes.")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Try Again" })).toBeTruthy();
  });

  it("shows the API reason on a 503 with a detail", async () => {
    answer(503, { detail: "The trade value chart is not ready." });
    await pickTrade();
    fireEvent.click(submit());
    expect(await screen.findByText("The trade value chart is not ready.")).toBeTruthy();
  });

  it("asks for the passphrase again on a 401", async () => {
    answer(401, { detail: "bad passphrase" });
    await pickTrade();
    fireEvent.click(submit());
    await waitFor(() => expect(onUnauthorized).toHaveBeenCalledTimes(1));
  });

  it("shows a retry button on another failure, and the button posts again", async () => {
    answer(500);
    await pickTrade();
    fireEvent.click(submit());
    expect(await screen.findByText("The API did not answer. Try again.")).toBeTruthy();

    answer(200, fixtureJson);
    fireEvent.click(screen.getByRole("button", { name: "Try Again" }));
    await screen.findByText("Not as is");
    expect(fetchStub).toHaveBeenCalledTimes(2);
  });

  it("aborts after 60 seconds, shows the timeout line, and the retry posts again", async () => {
    await pickTrade();
    // Only the timeout is fake. A fake clock for frames would leave Framer Motion on a stale time, so a later exit would stall.
    vi.useFakeTimers({ toFake: ["setTimeout", "clearTimeout"] });
    fetchStub.mockImplementationOnce(
      (_url: string, init: RequestInit) =>
        new Promise((_resolve, reject) => {
          init.signal!.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")));
        }),
    );
    fireEvent.click(submit());
    await act(() => vi.advanceTimersByTimeAsync(60_000));

    expect(screen.getByText("The grade took too long.")).toBeTruthy();
    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    fireEvent.click(screen.getByRole("button", { name: "Try Again" }));
    expect(fetchStub).toHaveBeenCalledTimes(2);
    expect(fetchStub.mock.calls[1][1].body).toBe(fetchStub.mock.calls[0][1].body);
  });

  it("aborts a pending grade on unmount without an error or a state update", async () => {
    const errorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    let signal: AbortSignal | undefined;
    fetchStub.mockImplementationOnce(
      (_url: string, init: RequestInit) =>
        new Promise((_resolve, reject) => {
          signal = init.signal!;
          signal.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")));
        }),
    );
    await pickTrade();
    fireEvent.click(submit());
    await screen.findByText("Grading the Trade");

    cleanup();
    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(signal!.aborted).toBe(true);
    expect(errorSpy).not.toHaveBeenCalled();
    errorSpy.mockRestore();
  });
});

/* A trade of three or four sides. A fourth team lets the trade fill every side. */
describe("TradeForm with three or four sides", () => {
  const FOUR_TEAMS: Team[] = [
    ...TEAMS,
    { roster_id: 9, team: "Draft Dodgers", manager: "Dee", avatar: null, players: [player("p6", "Dee One")] },
  ];

  beforeEach(() => {
    cleanup();
    render(<TradeForm teams={FOUR_TEAMS} season={2026} finderOn={finderOn} passphrase="localtest" onUnauthorized={onUnauthorized} />);
  });

  /* Picks a team on each of the first three sides and one player on each. */
  async function pickThreeSides() {
    await pickTeam("Your Team", "Pukancun on 3");
    await pickTeam("Team Two", "Blitz Bakers");
    fireEvent.click(addButton()!);
    await pickTeam("Team Three", "Punt Punks");
    await pickPlayers("Pukancun on 3", "Ana One");
    await pickPlayers("Blitz Bakers", "Ben Two");
    await pickPlayers("Punt Punks", "Cy One");
  }

  async function pickDestination(team: string, name: string, destination: string) {
    const list = await openPicker(toTrigger(team, name));
    choose(within(list).getByRole("option", { name: new RegExp(destination) }));
    await waitFor(() => expect(screen.queryByRole("listbox")).toBeNull());
  }

  it("shows Add a Team only when every side has a team and the trade has fewer than four sides", async () => {
    expect(addButton()).toBeNull();
    await pickTeam("Your Team", "Pukancun on 3");
    expect(addButton()).toBeNull();
    await pickTeam("Team Two", "Blitz Bakers");
    fireEvent.click(addButton()!);
    expect(group("Team Three")).toBeTruthy();
    expect(addButton()).toBeNull();
    await pickTeam("Team Three", "Punt Punks");
    fireEvent.click(addButton()!);
    expect(group("Team Four")).toBeTruthy();
    await pickTeam("Team Four", "Draft Dodgers");
    expect(addButton()).toBeNull();
    const headings = screen.getAllByRole("heading", { level: 3 }).map((h) => h.textContent);
    expect(headings).toEqual(["Your Team", "Team Two", "Team Three", "Team Four"]);
  });

  it("gives a remove control to the third and fourth sides only", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    await pickTeam("Team Two", "Blitz Bakers");
    fireEvent.click(addButton()!);
    await pickTeam("Team Three", "Punt Punks");
    fireEvent.click(addButton()!);
    expect(removeButton("Team Three")).toBeTruthy();
    expect(removeButton("Team Four")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Remove Your Team" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Remove Team Two" })).toBeNull();

    fireEvent.click(removeButton("Team Four"));
    await waitFor(() => expect(screen.queryByRole("group", { name: "Team Four" })).toBeNull());
    expect(addButton()).toBeTruthy();
  });

  it("shows no To picker at two sides", async () => {
    await pickTrade();
    expect(screen.queryByRole("combobox", { name: "To" })).toBeNull();
  });

  it("shows a To picker on each row at three sides, with the next side as the default", async () => {
    await pickThreeSides();
    expect(toTrigger("Pukancun on 3", "Ana One").textContent).toContain("Blitz Bakers");
    expect(toTrigger("Blitz Bakers", "Ben Two").textContent).toContain("Punt Punks");
    // The last side sends to the first side.
    expect(toTrigger("Punt Punks", "Cy One").textContent).toContain("Pukancun on 3");
    expect(row("Pukancun on 3", "Ana One").textContent).toContain("To");

    const list = await openPicker(toTrigger("Pukancun on 3", "Ana One"));
    expect(within(list).getAllByRole("option").map((o) => o.textContent)).toEqual(["Blitz Bakers", "Punt Punks"]);
  });

  it("points every pick at the next side when a third side joins, so the grade button turns on", async () => {
    await pickTrade();
    fireEvent.click(addButton()!);
    await pickTeam("Team Three", "Punt Punks");
    expect(toTrigger("Pukancun on 3", "Ana One").textContent).toContain("Blitz Bakers");
    expect(toTrigger("Blitz Bakers", "Ben Two").textContent).toContain("Punt Punks");
    expect(submit().disabled).toBe(true);
    await pickPlayers("Punt Punks", "Cy One");
    expect(submit().disabled).toBe(false);
  });

  it("keeps a destination when that side changes its team", async () => {
    await pickThreeSides();
    await pickDestination("Pukancun on 3", "Ana One", "Punt Punks");
    await pickTeam("Team Three", "Draft Dodgers");
    expect(toTrigger("Pukancun on 3", "Ana One").textContent).toContain("Draft Dodgers");
  });

  it("drops a removed side's players and sends the players bound for it to the default", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    await pickTeam("Team Two", "Blitz Bakers");
    fireEvent.click(addButton()!);
    await pickTeam("Team Three", "Punt Punks");
    fireEvent.click(addButton()!);
    await pickTeam("Team Four", "Draft Dodgers");
    await pickPlayers("Pukancun on 3", "Ana One");
    await pickPlayers("Punt Punks", "Cy One");
    await pickPlayers("Draft Dodgers", "Dee One");
    await pickDestination("Pukancun on 3", "Ana One", "Draft Dodgers");
    // Team Three sends to Team Four by default.
    expect(toTrigger("Punt Punks", "Cy One").textContent).toContain("Draft Dodgers");

    fireEvent.click(removeButton("Team Four"));
    await waitFor(() => expect(screen.queryByRole("button", { name: "Remove Dee One" })).toBeNull());
    expect(toTrigger("Pukancun on 3", "Ana One").textContent).toContain("Blitz Bakers");
    expect(toTrigger("Punt Punks", "Cy One").textContent).toContain("Pukancun on 3");
  });

  it("keeps the grade button off until every side gives and gets a player", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    await pickTeam("Team Two", "Blitz Bakers");
    fireEvent.click(addButton()!);
    await pickTeam("Team Three", "Punt Punks");
    await pickPlayers("Pukancun on 3", "Ana One");
    await pickPlayers("Blitz Bakers", "Ben Two");
    expect(submit().disabled).toBe(true);
    await pickPlayers("Punt Punks", "Cy One");
    expect(submit().disabled).toBe(false);
    // Punt Punks now gets no player.
    await pickDestination("Blitz Bakers", "Ben Two", "Pukancun on 3");
    expect(submit().disabled).toBe(true);
  });

  it("posts every side in order with the destination of each player", async () => {
    answer(200, fixtureJson);
    await pickThreeSides();
    await pickPlayers("Pukancun on 3", "Ana Two");
    await pickDestination("Pukancun on 3", "Ana Two", "Punt Punks");
    fireEvent.click(submit());
    await screen.findByText("Not as is");
    expect(JSON.parse(fetchStub.mock.calls[0][1].body)).toEqual({
      season: 2026,
      asker: 4,
      sides: [
        { roster_id: 4, gives: [{ player_id: "p1", to: 12 }, { player_id: "p2", to: 7 }] },
        { roster_id: 12, gives: [{ player_id: "p4", to: 7 }] },
        { roster_id: 7, gives: [{ player_id: "p5", to: 4 }] },
      ],
    });
  });
});

/* The finder cards hand their trade to the form. The fixture finder pair is roster 2 and roster 3, so these tests render those teams. */
describe("TradeForm with the finder", () => {
  afterEach(() => {
    finderOn = false;
  });

  const [first] = findJson.trades;
  const pairTeams: Team[] = first.sides.map((side) => ({
    roster_id: side.roster_id,
    team: side.team,
    manager: `Manager ${side.roster_id}`,
    avatar: null,
    // Every player of the fixture trades is on the roster of the side that gives him.
    players: findJson.trades.flatMap((t) => t.sides.find((s) => s.roster_id === side.roster_id)!.gives),
  }));

  beforeEach(() => {
    cleanup();
    finderOn = true;
    render(<TradeForm teams={pairTeams} season={2026} finderOn={finderOn} passphrase="localtest" onUnauthorized={onUnauthorized} />);
  });

  it("shows the finder when the flag is on", async () => {
    await pickTeam("Your Team", "All You Need Is Love");
    expect(screen.getByRole("group", { name: "Trade Partner" })).toBeTruthy();
  });

  it("titles the finder in title case and puts it after the grade button", async () => {
    await pickTeam("Your Team", "All You Need Is Love");
    const heading = screen.getByRole("heading", { level: 2, name: "Find a Trade" });
    const grade = screen.getByRole("button", { name: "Grade the Trade" });
    expect(grade.compareDocumentPosition(heading) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("hides the finder when the flag is off, with my team picked", async () => {
    finderOn = false;
    cleanup();
    render(<TradeForm teams={pairTeams} season={2026} finderOn={finderOn} passphrase="localtest" onUnauthorized={onUnauthorized} />);
    await pickTeam("Your Team", "All You Need Is Love");
    expect(screen.queryByRole("group", { name: "Trade Partner" })).toBeNull();
  });

  it("hides the finder once the trade has a third side, and shows it again at two", async () => {
    await pickTeam("Your Team", "All You Need Is Love");
    await pickTeam("Team Two", "Lil Fridge");
    fireEvent.click(screen.getByRole("button", { name: "Add a Team" }));
    expect(screen.queryByRole("group", { name: "Trade Partner" })).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Remove Team Three" }));
    await waitFor(() => expect(screen.getByRole("group", { name: "Trade Partner" })).toBeTruthy());
  });

  it("shows no finder until my team is picked", async () => {
    expect(screen.queryByRole("group", { name: "Trade Partner" })).toBeNull();
    await pickTeam("Your Team", "All You Need Is Love");
    expect(screen.getByRole("group", { name: "Trade Partner" })).toBeTruthy();
  });

  /* Finds with the fixture partner and taps "See the Full Result" on a card. */
  async function openCard(finderDoc: unknown, index: number) {
    await pickTeam("Your Team", "All You Need Is Love");
    answer(200, finderDoc);
    fireEvent.click(within(group("Trade Partner")).getByRole("radio", { name: /Lil Fridge/ }));
    fireEvent.click(screen.getByRole("button", { name: "Find a Trade" }));
    const cards = await screen.findAllByRole("article");
    answer(200, fixtureJson);
    fireEvent.click(within(cards[index]).getByRole("button", { name: "See the Full Result" }));
    await screen.findByText("Not as is");
  }

  it("resets the partner and the cards when my team changes", async () => {
    await pickTeam("Your Team", "All You Need Is Love");
    answer(200, findJson);
    fireEvent.click(within(group("Trade Partner")).getByRole("radio", { name: /Lil Fridge/ }));
    fireEvent.click(screen.getByRole("button", { name: "Find a Trade" }));
    await screen.findAllByRole("article");

    await pickTeam("Your Team", "Lil Fridge");
    expect(screen.queryAllByRole("article")).toHaveLength(0);
    const partners = within(group("Trade Partner")).getAllByRole("radio") as HTMLInputElement[];
    expect(partners.every((p) => !p.checked)).toBe(true);
    expect((screen.getByRole("button", { name: "Find a Trade" }) as HTMLButtonElement).disabled).toBe(true);
  });

  it("scrolls the result into view after a card opens its full result", async () => {
    // jsdom has no scrollIntoView, so the test supplies one.
    const scrollIntoView = vi.fn();
    Element.prototype.scrollIntoView = scrollIntoView;
    await openCard(findJson, 1);
    await waitFor(() => expect(scrollIntoView).toHaveBeenCalledTimes(1));
    expect(scrollIntoView).toHaveBeenCalledWith({ behavior: "smooth", block: "start" });
  });

  it("grades the trade of a card with the season of the finder document", async () => {
    Element.prototype.scrollIntoView = vi.fn();
    await openCard({ ...findJson, season: 2025 }, 1);
    expect(JSON.parse(fetchStub.mock.calls[1][1].body).season).toBe(2025);
  });

  it("grades the trade of a card through the analyze route and shows the full result", async () => {
    Element.prototype.scrollIntoView = vi.fn();
    await pickTeam("Your Team", "All You Need Is Love");
    answer(200, findJson);
    fireEvent.click(within(group("Trade Partner")).getByRole("radio", { name: /Lil Fridge/ }));
    fireEvent.click(screen.getByRole("button", { name: "Find a Trade" }));
    const cards = await screen.findAllByRole("article");
    expect(cards).toHaveLength(3);

    answer(200, fixtureJson);
    fireEvent.click(within(cards[1]).getByRole("button", { name: "See the Full Result" }));
    await screen.findByText("Not as is");

    const [url, init] = fetchStub.mock.calls[1];
    expect(url).toContain("/analyze");
    expect(JSON.parse(init.body)).toEqual({
      season: 2026,
      asker: 2,
      sides: [
        { roster_id: 2, gives: [{ player_id: "12527", to: 3 }] },
        { roster_id: 3, gives: [{ player_id: "11560", to: 2 }, { player_id: "5947", to: 2 }] },
      ],
    });
    // The form shows the trade of the card, so the picks match the result.
    expect(teamTrigger("Team Two").textContent).toContain("Lil Fridge");
    expect(within(group("Your Team")).getByRole("button", { name: "Remove Ashton Jeanty" })).toBeTruthy();
    expect(within(group("Team Two")).getByRole("button", { name: "Remove Caleb Williams" })).toBeTruthy();
  });
});
