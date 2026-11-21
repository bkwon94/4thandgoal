/**
 * Tests for the Trade block strip of Find mode, with the real week 10 roster of Bo Girds: the players it lists, a tap
 * on and off, the cap of 3, the find body, and the life of the block. fetch is a test stub that sends a real stream.
 */
import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import "@cpc/design/ui/sheet-jsdom";
import { apiTarget, findResponse, teamBoGirds } from "../lib/fixtures/api";
import type { Team } from "../lib/api";
import { TradeFinder } from "./trade-finder";

/* Bo Girds is roster 6. Two more teams give the strip another roster for a team change and a partner to pick. */
const OTHER: Team = {
  roster_id: 10,
  team: "Lil Fridge",
  manager: "TeamJu",
  avatar: null,
  players: [{ player_id: "4984", name: "Josh Allen", position: "QB", nfl_team: "BUF", headshot: "https://sleepercdn.com/content/nfl/players/4984.jpg" }],
};
const THIRD: Team = { roster_id: 2, team: "All You Need Is Love", manager: "wsh5022", avatar: null, players: [] };
const TEAMS: Team[] = [THIRD, teamBoGirds, OTHER];

const fetchStub = vi.fn();

/* One part of the find stream as a `data:` line. */
const line = (part: unknown) => new TextEncoder().encode(`data: ${JSON.stringify(part)}\n\n`);

/* A find stream that sends its first step and holds, so the find still runs while the test taps. */
function heldStream() {
  let controller!: ReadableStreamDefaultController<Uint8Array>;
  const body = new ReadableStream<Uint8Array>({ start: (c) => void (controller = c) });
  fetchStub.mockResolvedValueOnce(new Response(body, { headers: { "content-type": "text/event-stream" } }));
  return {
    end: (doc: unknown) => {
      controller.enqueue(line({ type: "data-answer", data: { kind: "find", document: doc } }));
      controller.close();
    },
  };
}
const noop = () => {};

function renderFinder(asker: number) {
  return render(
    <TradeFinder teams={TEAMS} target={apiTarget} asker={asker} onAsker={noop} passphrase="localtest" onUnauthorized={noop} onOpen={noop} />,
  );
}

const findButton = () => screen.getByRole("button", { name: "Find a Trade" });
/* The body of each find that the page posted. */
const bodies = () => fetchStub.mock.calls.map(([, init]) => JSON.parse(init.body));

/* Picks a row of the partner sheet by its name, and waits for the sheet to close. */
async function pickPartner(name: RegExp) {
  fireEvent.click(screen.getByRole("button", { name: /Trade with/ }));
  const rows = within(await screen.findByRole("list", { name: "Partners" })).getAllByRole("button");
  fireEvent.click(rows.find((row) => name.test(row.textContent ?? "")) as HTMLElement);
  await waitFor(() => expect(screen.queryByRole("list", { name: "Partners" })).toBeNull());
}

const strip = () => screen.getByRole("group", { name: "Trade block" });
/* One toggle of the strip by its accessible name, such as "Kenneth Walker III, RB". */
const toggle = (name: string) => within(strip()).getByRole("button", { name });
/* The accessible names of the toggles of the strip, in the order of the strip. */
const names = () => within(strip()).getAllByRole("button").map((button) => button.getAttribute("aria-label"));

beforeEach(() => {
  fetchStub.mockReset();
  vi.stubGlobal("fetch", fetchStub);
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("Trade block", () => {
  it("lists only the QB, RB, WR, and TE of the asker, in that position order and then by name", () => {
    renderFinder(6);
    expect(names()).toEqual([
      "Aaron Rodgers, QB",
      "Fernando Mendoza, QB",
      "Lamar Jackson, QB",
      "Blake Corum, RB",
      "Kenneth Walker III, RB",
      "Kyren Williams, RB",
      "Mike Washington Jr., RB",
      "Antonio Williams, WR",
      "Chimere Dike, WR",
      "CJ Daniels, WR",
      "Matthew Golden, WR",
      "Parker Washington, WR",
      "Zay Flowers, WR",
      "Trey McBride, TE",
    ]);
    // Each item shows the headshot, the last name, and the position.
    const walker = toggle("Kenneth Walker III, RB");
    expect(walker.querySelector("img")?.getAttribute("src")).toBe("https://sleepercdn.com/content/nfl/players/8151.jpg");
    expect(walker.textContent).toBe("Walker IIIRB");
  });

  it("puts a tapped player on the block with a ring and a check at the front, and a second tap takes him off", () => {
    renderFinder(6);
    expect(screen.getByText("0 of 3")).toBeTruthy();
    fireEvent.click(toggle("Kenneth Walker III, RB"));
    expect(names()[0]).toBe("Kenneth Walker III, RB");
    expect(toggle("Kenneth Walker III, RB").getAttribute("aria-pressed")).toBe("true");
    expect(toggle("Kenneth Walker III, RB").querySelector("img")?.className).toContain("ring-accent");
    expect(toggle("Kenneth Walker III, RB").querySelector("[data-check]")?.getAttribute("data-check")).toBe("true");
    expect(screen.getByText("1 of 3")).toBeTruthy();
    expect(screen.getByText("Trade block · tap to add")).toBeTruthy();

    fireEvent.click(toggle("Kenneth Walker III, RB"));
    expect(toggle("Kenneth Walker III, RB").getAttribute("aria-pressed")).toBe("false");
    expect(names()[4]).toBe("Kenneth Walker III, RB");
    expect(screen.getByText("0 of 3")).toBeTruthy();
  });

  it("leads the strip with the picks in the order of the taps", () => {
    renderFinder(6);
    fireEvent.click(toggle("Zay Flowers, WR"));
    fireEvent.click(toggle("Kenneth Walker III, RB"));
    expect(names().slice(0, 3)).toEqual(["Zay Flowers, WR", "Kenneth Walker III, RB", "Aaron Rodgers, QB"]);
  });

  it("scrolls the strip back to its start when a pick from the scrolled end lands at the front", () => {
    const { container } = renderFinder(6);
    const viewport = container.querySelector<HTMLElement>("[data-slot=scroll-area-viewport]") as HTMLElement;
    viewport.scrollLeft = 600;
    fireEvent.click(toggle("Parker Washington, WR"));
    expect(names()[0]).toBe("Parker Washington, WR");
    expect(viewport.scrollLeft).toBe(0);
  });

  it("shows the empty line while no one is on the block", () => {
    renderFinder(6);
    const EMPTY = "No one on the block. The search can offer any of your players.";
    expect(screen.getByText(EMPTY)).toBeTruthy();
    fireEvent.click(toggle("Kenneth Walker III, RB"));
    expect(screen.queryByText(EMPTY)).toBeNull();
  });

  it("adds no one on a 4th tap, scrolls the strip back to the picks, and says why", () => {
    const { container } = renderFinder(6);
    const FULL = "Your block holds 3 players. Take one off to add another.";
    for (const name of ["Kenneth Walker III, RB", "Zay Flowers, WR", "Blake Corum, RB"]) fireEvent.click(toggle(name));
    expect(screen.getByText("3 of 3")).toBeTruthy();
    expect(screen.getByText("Trade block · tap a pick to take it off")).toBeTruthy();
    expect(screen.queryByText(FULL)).toBeNull();

    // The reader has scrolled to the end of the roster before the 4th tap.
    const viewport = container.querySelector<HTMLElement>("[data-slot=scroll-area-viewport]") as HTMLElement;
    viewport.scrollLeft = 600;
    fireEvent.click(toggle("Lamar Jackson, QB"));
    expect(toggle("Lamar Jackson, QB").getAttribute("aria-pressed")).toBe("false");
    expect(names().slice(0, 3)).toEqual(["Kenneth Walker III, RB", "Zay Flowers, WR", "Blake Corum, RB"]);
    expect(screen.getByText("3 of 3")).toBeTruthy();
    expect(screen.getByText(FULL)).toBeTruthy();
    expect(viewport.scrollLeft).toBe(0);

    // A pick taken off frees a place, and the reason goes.
    fireEvent.click(toggle("Zay Flowers, WR"));
    expect(screen.queryByText(FULL)).toBeNull();
    expect(screen.getByText("2 of 3")).toBeTruthy();
  });

  it("sends the block in the find body, in the order of the taps, and no block while it is empty", async () => {
    renderFinder(6);
    const first = heldStream();
    fireEvent.click(findButton());
    first.end(findResponse);
    await waitFor(() => expect(screen.getByRole("group", { name: "Trade block" })).toBeTruthy());
    fireEvent.click(toggle("Kenneth Walker III, RB"));
    fireEvent.click(toggle("Zay Flowers, WR"));
    const second = heldStream();
    fireEvent.click(findButton());
    second.end(findResponse);
    await waitFor(() => expect(fetchStub).toHaveBeenCalledTimes(2));
    expect(bodies()).toEqual([
      { season: 2026, asker: 6 },
      { season: 2026, asker: 6, trade_block: ["8151", "9997"] },
    ]);
  });

  it("clears the block on a change of Your team, and keeps it on a change of the partner or the chip", async () => {
    const view = renderFinder(6);
    fireEvent.click(toggle("Kenneth Walker III, RB"));
    fireEvent.click(toggle("Zay Flowers, WR"));

    await pickPartner(/Lil Fridge/);
    fireEvent.click(screen.getByRole("radio", { name: "RB" }));
    expect(names().slice(0, 2)).toEqual(["Kenneth Walker III, RB", "Zay Flowers, WR"]);
    expect(screen.getByText("2 of 3")).toBeTruthy();

    view.rerender(<TradeFinder teams={TEAMS} target={apiTarget} asker={10} onAsker={noop} passphrase="localtest" onUnauthorized={noop} onOpen={noop} />);
    expect(names()).toEqual(["Josh Allen, QB"]);
    expect(screen.getByText("0 of 3")).toBeTruthy();

    // A pick of the first team again starts from an empty block too.
    view.rerender(<TradeFinder teams={TEAMS} target={apiTarget} asker={6} onAsker={noop} passphrase="localtest" onUnauthorized={noop} onOpen={noop} />);
    expect(screen.getByText("0 of 3")).toBeTruthy();
    expect(within(strip()).queryAllByRole("button", { pressed: true })).toHaveLength(0);
  });

  it("locks the strip during a find, so a tap there changes nothing", async () => {
    renderFinder(6);
    fireEvent.click(toggle("Kenneth Walker III, RB"));
    const stream = heldStream();
    fireEvent.click(findButton());
    // The wait takes the place of the hero, so no toggle of the strip takes a tap while the find runs.
    await waitFor(() => expect(screen.queryByRole("group", { name: "Trade block" })).toBeNull());
    stream.end(findResponse);
    await waitFor(() => expect(screen.getByRole("group", { name: "Trade block" })).toBeTruthy());
    expect(within(strip()).getAllByRole("button", { pressed: true }).map((b) => b.getAttribute("aria-label"))).toEqual(["Kenneth Walker III, RB"]);
  });

  it("turns each toggle off while a grade runs", () => {
    render(<TradeFinder teams={TEAMS} target={apiTarget} asker={6} onAsker={noop} passphrase="localtest" onUnauthorized={noop} onOpen={noop} locked />);
    // A toggle of the group stays in the tab order while it is off, so a screen reader still finds it, and says it is off.
    within(strip()).getAllByRole("button").forEach((button) => expect(button.getAttribute("aria-disabled")).toBe("true"));
    fireEvent.click(toggle("Kenneth Walker III, RB"));
    expect(screen.getByText("0 of 3")).toBeTruthy();
  });

  it("never says anchor in the copy of Find mode", () => {
    renderFinder(6);
    fireEvent.click(toggle("Kenneth Walker III, RB"));
    expect(document.body.textContent).not.toMatch(/anchor/i);
  });
});
