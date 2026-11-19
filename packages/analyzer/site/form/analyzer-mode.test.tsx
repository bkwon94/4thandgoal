/**
 * Tests for the switch of the analyzer hero, Grade a trade and Find a trade: the mode of the link, the Find hero with its
 * partner choice and position chips, the find body of a chip, and the deadline eyebrow. fetch is a test stub.
 */
import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import "@cpc/design/ui/sheet-jsdom";
import { apiTarget, findResponse } from "../lib/fixtures/api";
import { setPassphrase } from "../lib/passphrase";
import { Analyzer } from "./analyzer";

/* Twelve teams, as in the league. Roster 6 is the asker of the find tests. */
const TEAMS = {
  teams: Array.from({ length: 12 }, (_, i) => ({
    roster_id: i + 1,
    team: i === 5 ? "Bo Girds" : `Team ${i + 1}`,
    manager: `Manager ${i + 1}`,
    avatar: null,
    players: [],
  })),
};

/* The Lock of client cpc: 00:00 Eastern on Tue 2026-11-24. */
const LOCK = Date.parse("2026-11-24T05:00:00Z");

const fetchStub = vi.fn();

function answer(status: number, body: unknown) {
  fetchStub.mockResolvedValueOnce(new Response(JSON.stringify(body), { status }));
}

/* The page at the address of a link, with the passphrase stored and the teams answer queued. */
function open(search: string, props: { finderOn?: boolean; lock?: number } = {}) {
  window.history.replaceState(null, "", `/analyze/${search}`);
  answer(200, TEAMS);
  render(<Analyzer target={apiTarget} finderOn={props.finderOn ?? true} lock={props.lock} />);
}

const modeSwitch = () => screen.getByRole("radiogroup", { name: "Mode" });
const half = (name: string) => within(modeSwitch()).getByRole("radio", { name });
const checked = (name: string) => half(name).getAttribute("aria-checked") === "true";
const eyebrow = () => document.querySelector('[data-hero-slot="eyebrow"]')?.textContent;

beforeEach(() => {
  localStorage.clear();
  sessionStorage.clear();
  setPassphrase("localtest");
  fetchStub.mockReset();
  vi.stubGlobal("fetch", fetchStub);
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.useRealTimers();
  window.history.replaceState(null, "", "/");
});

describe("The analyzer switch", () => {
  it("opens Grade mode from a link with the Grade mode", async () => {
    open("?mode=grade");
    await waitFor(() => expect(checked("Grade a trade")).toBe(true));
    expect(checked("Find a trade")).toBe(false);
    expect(screen.getByRole("heading", { level: 1, name: "Trade Analyzer" })).toBeTruthy();
  });

  it("opens Find mode from a link with the Find mode, with the title and the line of Find", async () => {
    open("?mode=find");
    await waitFor(() => expect(checked("Find a trade")).toBe(true));
    expect(screen.getByRole("heading", { level: 1, name: "Trade Ideas" })).toBeTruthy();
    expect(screen.getByText("Who has a trade for you?")).toBeTruthy();
    // The form of the grade hides while Find shows.
    expect(screen.queryByRole("button", { name: "Grade the Trade" })).toBeNull();
  });

  it("shows no switch and opens Grade while the finder flag is off", async () => {
    open("?mode=find", { finderOn: false });
    expect(await screen.findByRole("heading", { level: 1, name: "Trade Analyzer" })).toBeTruthy();
    expect(screen.queryByRole("radiogroup", { name: "Mode" })).toBeNull();
  });

  it("moves to Find on a tap and names the mode in the address", async () => {
    open("");
    await waitFor(() => expect(checked("Grade a trade")).toBe(true));
    fireEvent.click(half("Find a trade"));
    expect(await screen.findByRole("heading", { level: 1, name: "Trade Ideas" })).toBeTruthy();
    expect(window.location.search).toBe("?mode=find");
    // The pill of the new hero moves to Find one frame after the swap.
    await waitFor(() => expect(checked("Find a trade")).toBe(true));
    fireEvent.click(half("Grade a trade"));
    expect(await screen.findByRole("heading", { level: 1, name: "Trade Analyzer" })).toBeTruthy();
    expect(window.location.search).toBe("?mode=grade");
  });
  it("slides the pill from the old half and keeps focus on the switch after a swap of heroes", async () => {
    open("");
    await waitFor(() => expect(checked("Grade a trade")).toBe(true));
    half("Find a trade").focus();
    fireEvent.click(half("Find a trade"));
    await screen.findByRole("heading", { level: 1, name: "Trade Ideas" });
    await waitFor(() => expect(checked("Find a trade")).toBe(true));
    await waitFor(() => expect(document.activeElement).toBe(half("Find a trade")));
  });
});

describe("Find mode", () => {
  it("shows the partner choice of one team or every team, and the position chips", async () => {
    open("?mode=find&team=6");
    const partner = await screen.findByRole("button", { name: /Trade with/ });
    expect(partner.textContent).toContain("Every team");
    const chips = screen.getByRole("radiogroup", { name: "Position" });
    expect(within(chips).getAllByRole("radio").map((chip) => chip.textContent)).toEqual(["Any", "RB", "WR", "TE", "QB"]);
    expect(within(chips).getByRole("radio", { name: "Any" }).getAttribute("aria-checked")).toBe("true");
    expect(screen.getByRole("button", { name: "Find a Trade" })).toBeTruthy();
  });

  it("offers no choice of two or three teams", async () => {
    open("?mode=find&team=6");
    await screen.findByRole("radiogroup", { name: "Position" });
    expect(screen.queryByText(/three teams|3 teams|two teams|2 teams/i)).toBeNull();
    expect(screen.queryByRole("radio", { name: /team/i })).toBeNull();
  });

  it("picks one partner from the sheet, with Every team first", async () => {
    open("?mode=find&team=6");
    await waitFor(() => expect((screen.getByRole("button", { name: /Trade with/ }) as HTMLButtonElement).disabled).toBe(false));
    fireEvent.click(screen.getByRole("button", { name: /Trade with/ }));
    const rows = within(await screen.findByRole("list", { name: "Partners" })).getAllByRole("button");
    // Every team, then the eleven other teams. The asker is not a partner.
    expect(rows).toHaveLength(12);
    expect(rows[0].textContent).toContain("Every team");
    expect(rows.some((row) => row.textContent?.includes("Bo Girds"))).toBe(false);
    fireEvent.click(rows[3]);
    await waitFor(() => expect(screen.getByRole("button", { name: /Trade with/ }).textContent).toContain("Team 3"));
  });

  it("sends aim_position RB for the chip RB, the field that a typed question sets", async () => {
    open("?mode=find&team=6");
    await waitFor(() => expect((screen.getByRole("button", { name: "Find a Trade" }) as HTMLButtonElement).disabled).toBe(false));
    // The teams arrive after the first paint, and Find starts again for the asker, so the test reads the chips after them.
    const chips = screen.getByRole("radiogroup", { name: "Position" });
    fireEvent.click(within(chips).getByRole("radio", { name: "RB" }));
    await waitFor(() => expect(within(chips).getByRole("radio", { name: "RB" }).getAttribute("aria-checked")).toBe("true"));
    answer(200, findResponse);
    fireEvent.click(screen.getByRole("button", { name: "Find a Trade" }));
    await waitFor(() => expect(fetchStub).toHaveBeenCalledTimes(2));
    const [url, init] = fetchStub.mock.calls[1];
    expect(url).toBe("https://api.example.test/clients/cpc/find");
    expect(JSON.parse(init.body)).toEqual({ season: 2026, asker: 6, limit: { aim_position: "RB" } });
  });

  it("sends no limit for the chip Any", async () => {
    open("?mode=find&team=6");
    await waitFor(() => expect((screen.getByRole("button", { name: "Find a Trade" }) as HTMLButtonElement).disabled).toBe(false));
    answer(200, findResponse);
    fireEvent.click(screen.getByRole("button", { name: "Find a Trade" }));
    await waitFor(() => expect(fetchStub).toHaveBeenCalledTimes(2));
    expect(JSON.parse(fetchStub.mock.calls[1][1].body)).toEqual({ season: 2026, asker: 6 });
  });

  it("asks for Your team when no team is known, and keeps Find off until a pick", async () => {
    open("?mode=find");
    const you = await screen.findByRole("button", { name: /Your team/ });
    expect((screen.getByRole("button", { name: "Find a Trade" }) as HTMLButtonElement).disabled).toBe(true);
    fireEvent.click(you);
    const rows = within(await screen.findByRole("list", { name: "Teams" })).getAllByRole("button");
    fireEvent.click(rows.find((row) => row.textContent?.includes("Bo Girds")) as HTMLElement);
    await waitFor(() => expect(screen.getByRole("button", { name: /Your team/ }).textContent).toContain("Bo Girds"));
    expect((screen.getByRole("button", { name: "Find a Trade" }) as HTMLButtonElement).disabled).toBe(false);
  });
});

describe("The deadline eyebrow", () => {
  /* Only Date is fake, so the timers of waitFor still run. */
  function at(iso: string) {
    vi.useFakeTimers({ toFake: ["Date"] });
    vi.setSystemTime(new Date(iso));
  }

  it("reads the countdown during Deadline week", async () => {
    // 09:55:00 Eastern on Sat 2026-11-21.
    at("2026-11-21T14:55:00Z");
    open("", { lock: LOCK });
    await waitFor(() => expect(eyebrow()).toBe("Trade deadline ~2d 14h 05m"));
  });

  it("reads the passed line after the Lock, in both modes", async () => {
    // 00:00:01 Eastern on Tue 2026-11-24.
    at("2026-11-24T05:00:01Z");
    open("?mode=find", { lock: LOCK });
    await waitFor(() => expect(eyebrow()).toBe("The trade deadline has passed"));
    await waitFor(() => expect(checked("Find a trade")).toBe(true));
    fireEvent.click(half("Grade a trade"));
    await waitFor(() => expect(eyebrow()).toBe("The trade deadline has passed"));
  });

  it("reads the name of the tool one day after the Lock, and with no Lock", async () => {
    at("2026-11-25T05:00:00Z");
    open("", { lock: LOCK });
    await waitFor(() => expect(eyebrow()).toBe("Trade Analyzer"));
    cleanup();
    open("");
    await waitFor(() => expect(eyebrow()).toBe("Trade Analyzer"));
  });

  it("ticks the countdown each minute", async () => {
    at("2026-11-21T14:55:00Z");
    open("", { lock: LOCK });
    await waitFor(() => expect(eyebrow()).toBe("Trade deadline ~2d 14h 05m"));
    await act(async () => {
      vi.setSystemTime(new Date("2026-11-21T14:56:00Z"));
      window.dispatchEvent(new Event("focus"));
    });
    await waitFor(() => expect(eyebrow()).toBe("Trade deadline ~2d 14h 04m"), { timeout: 3000 });
  });
});
