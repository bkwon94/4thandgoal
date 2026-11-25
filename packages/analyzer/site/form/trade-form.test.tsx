/**
 * Tests for the trade form, the Stack: the teams row, the cards, the sheets, the grade bar, the post body, and each error state.
 * fetch is a test stub, and each test reads the screen. A test opens a sheet with a click on its button.
 */
import { act, cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { useState } from "react";
import { afterEach, beforeEach, describe, expect, it, mock, spyOn } from "bun:test";
import "@cpc/design/ui/sheet-jsdom";
import { apiTarget, analyzeResponse as fixtureJson } from "../lib/fixtures/api";
import { findResponse as findJson } from "../lib/fixtures/api";
import type { Team } from "../lib/api";
import type { AnalyzerMode } from "../lib/mode";
import {
  addPlayer,
  chooseTeam,
  pickPlayers,
  pickTeam,
  pickTrade,
  slot,
  type SideTitle,
} from "./form-steps";
import { TradeForm } from "./trade-form";

// The finder flag is a prop from the page, so each render passes the flag the test sets.
let finderOn = false;

const player = (id: string, name: string, position = "WR") => ({
  player_id: id,
  name,
  position,
  nfl_team: "NYJ",
  headshot: `https://cdn.test/${id}.png`,
});

const TEAMS: Team[] = [
  {
    roster_id: 4,
    team: "Pukancun on 3",
    manager: "Ana",
    avatar: "https://cdn.test/ana.png",
    players: [player("p1", "Ana One"), player("p2", "Ana Two", "QB")],
  },
  {
    roster_id: 12,
    team: "Blitz Bakers",
    manager: "Ben",
    avatar: null,
    players: [player("p3", "Ben One", "RB"), player("p4", "Ben Two")],
  },
  {
    roster_id: 7,
    team: "Punt Punks",
    manager: "Cy",
    avatar: null,
    players: [player("p5", "Cy One")],
  },
];

/* A clock for `setTimeout` and `clearTimeout` only. The fake timers of `bun:test` drop a timer that is still pending when
   they end, and a frame would then wait for ever. The preload keeps its frame timer on the real `setTimeout`. The spies end
   with the test. */
function fakeTimeouts() {
  let now = 0;
  let lastId = 0;
  const pending = new Map<number, { at: number; run: () => void }>();
  spyOn(globalThis, "setTimeout").mockImplementation(((run: () => void, delay = 0) => {
    lastId += 1;
    pending.set(lastId, { at: now + delay, run });
    return lastId;
  }) as unknown as typeof setTimeout);
  spyOn(globalThis, "clearTimeout").mockImplementation(((id: number) => {
    pending.delete(id);
  }) as unknown as typeof clearTimeout);
  return {
    // Runs each timer that falls due within `ms`, in order, as the timers that they set may fall due too.
    advance(ms: number) {
      const end = now + ms;
      for (;;) {
        const due = [...pending]
          .filter(([, timer]) => timer.at <= end)
          .sort((a, b) => a[1].at - b[1].at)[0];
        if (!due) break;
        pending.delete(due[0]);
        now = due[1].at;
        due[1].run();
      }
      now = end;
    },
  };
}

const fetchStub = mock();
const onUnauthorized = mock();

function answer(status: number, body: unknown = {}, headers: Record<string, string> = {}) {
  fetchStub.mockResolvedValueOnce(new Response(JSON.stringify(body), { status, headers }));
}

/* The card of a side, named by its heading. */
const card = (side: SideTitle) => screen.getByRole("region", { name: `${side} gets` });
const submit = () => screen.getByRole("button", { name: "Grade the Trade" }) as HTMLButtonElement;
const sheet = () => screen.getByRole("dialog");
const regrade = () =>
  within(screen.getByRole("dialog", { name: "Edit the trade" })).getByRole("button", {
    name: "Regrade the Trade",
  }) as HTMLButtonElement;
/* A result hides the form, so a test taps Edit in the header of The Sides to change the trade. */
const edit = () => fireEvent.click(screen.getByRole("button", { name: "Edit the trade" }));
/* The elements that asked to scroll into view. jsdom does no layout and has no scrollIntoView, so each test records them. */
let scrolled: Element[] = [];

/* Adds a side with a team through "+". */
async function addTeam(team: string) {
  fireEvent.click(screen.getByRole("button", { name: "Add a team" }));
  await chooseTeam(team);
}

/* The filled hero slots of a hero, in the order of the markup. */
const slotsOf = (hero: HTMLElement) =>
  [...hero.querySelectorAll("[data-hero-slot]")].map((slot) => slot.getAttribute("data-hero-slot"));
const slotText = (hero: HTMLElement, slot: string) =>
  hero.querySelector(`[data-hero-slot=${slot}]`)?.textContent;

/* The row of a team on the stage of a hero, and the src of each player headshot in it. The team avatar is not a headshot. */
const stageRow = (hero: HTMLElement, team: string) =>
  [...hero.querySelectorAll("[data-mesh-anchor]")].find(
    (row) => row.querySelector("[data-stage-team]")?.textContent === team,
  ) as HTMLElement;
const stageHeadshots = (el: HTMLElement) =>
  [...el.querySelectorAll("img")]
    .map((img) => img.getAttribute("src") ?? "")
    .filter((src) => /\/(p\d+\.png|players\/)/.test(src));

const removeButton = (name: string) =>
  screen.getByRole("button", { name: `Remove ${name}` }) as HTMLButtonElement;

/* The text of each row of a card. */
const rowsOf = (side: SideTitle) =>
  within(screen.getByRole("list", { name: `Players ${side} gets` }))
    .queryAllByRole("listitem")
    .map((item) => item.textContent);

/* The main trade of p1 for p4: my team gets Ben Two, and the other team gets Ana One. */
const TRADE = {
  mine: "Pukancun on 3",
  other: "Blitz Bakers",
  mineGets: "Ben Two",
  otherGets: "Ana One",
};

beforeEach(() => {
  scrolled = [];
  Element.prototype.scrollIntoView = function (this: Element) {
    scrolled.push(this);
  };
  fetchStub.mockReset();
  onUnauthorized.mockReset();
  spyOn(globalThis, "fetch").mockImplementation(fetchStub as unknown as typeof fetch);
  render(
    <TradeForm
      teams={TEAMS}
      target={apiTarget}
      finderOn={finderOn}
      passphrase="localtest"
      onUnauthorized={onUnauthorized}
    />,
  );
});

afterEach(() => {
  cleanup();
});

/* A find stream that sends the first step and the document, then ends, as the find stream of the API does. */
function findStream(doc: unknown) {
  const encoded = (part: unknown) => new TextEncoder().encode(`data: ${JSON.stringify(part)}\n\n`);
  const body = new ReadableStream<Uint8Array>({
    start(controller) {
      controller.enqueue(
        encoded({ type: "data-step", data: { line: "Reading their roster", live: true } }),
      );
      controller.enqueue(encoded({ type: "data-answer", data: { kind: "find", document: doc } }));
      controller.close();
    },
  });
  fetchStub.mockResolvedValueOnce(
    new Response(body, { headers: { "content-type": "text/event-stream" } }),
  );
}

describe("TradeForm", () => {
  it("edits the captured trade in a sheet, restores it on Cancel, and submits changed picks", async () => {
    cleanup();
    const captured = fixtureJson.trade.sides;
    const teams = captured.map((side) => ({
      roster_id: side.roster_id,
      team: side.team,
      manager: side.team,
      avatar: null,
      players: side.gives,
    }));
    const prefill = captured.map((side, id) => ({
      id,
      rosterId: side.roster_id,
      gets: side.gets.map((player) => ({
        playerId: player.player_id,
        fromSide: captured.findIndex((other) => other.roster_id === player.from),
      })),
    }));
    render(
      <TradeForm
        teams={teams}
        target={apiTarget}
        finderOn={false}
        passphrase="localtest"
        onUnauthorized={onUnauthorized}
        prefill={prefill}
      />,
    );
    answer(200, fixtureJson);
    fireEvent.click(submit());
    const result = await screen.findByRole("region", { name: "The Read" });
    const trigger = screen.getByRole("button", { name: "Edit the trade" });
    trigger.focus();
    fireEvent.click(trigger);
    const editor = screen.getByRole("dialog", { name: "Edit the trade" });
    expect(result.isConnected).toBe(true);
    expect(scrolled).toEqual([]);
    expect(within(editor).getByRole("button", { name: "Remove Garrett Wilson" })).toBeTruthy();
    fireEvent.click(within(editor).getByRole("button", { name: "Remove Garrett Wilson" }));
    expect(result.isConnected).toBe(true);
    fireEvent.click(within(editor).getByRole("button", { name: "Cancel" }));
    await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
    expect(screen.getByRole("region", { name: "The Read" })).toBe(result);
    expect(document.activeElement).toBe(trigger);
    for (const close of ["Close", "Escape"]) {
      fireEvent.click(trigger);
      const draft = screen.getByRole("dialog", { name: "Edit the trade" });
      expect(within(draft).getByRole("button", { name: "Remove Garrett Wilson" })).toBeTruthy();
      fireEvent.click(within(draft).getByRole("button", { name: "Remove Garrett Wilson" }));
      if (close === "Escape") fireEvent.keyDown(document, { key: "Escape" });
      else fireEvent.click(within(draft).getByRole("button", { name: close }));
      await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
      expect(screen.getByRole("region", { name: "The Read" })).toBe(result);
      expect(document.activeElement).toBe(trigger);
    }
    fireEvent.click(trigger);
    const reopened = screen.getByRole("dialog", { name: "Edit the trade" });
    expect(within(reopened).getByRole("button", { name: "Remove Garrett Wilson" })).toBeTruthy();
    fireEvent.click(within(reopened).getByRole("button", { name: "Add a player Your Team gets" }));
    const picker = screen.getByRole("dialog", { name: "Your Team gets" });
    fireEvent.click(within(picker).getByRole("checkbox", { name: /Garrett Wilson/ }));
    fireEvent.click(within(picker).getByRole("button", { name: /^Done/ }));
    await waitFor(() =>
      expect(screen.queryByRole("dialog", { name: "Your Team gets" })).toBeNull(),
    );
    expect(result.isConnected).toBe(true);
    expect(screen.getByRole("dialog", { name: "Edit the trade" })).toBe(reopened);
    answer(200, fixtureJson);
    fireEvent.click(regrade());
    await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
    await screen.findByRole("region", { name: "The Read" });
    expect(result.isConnected).toBe(false);
    expect(fetchStub).toHaveBeenCalledTimes(2);
    expect(fetchStub).toHaveBeenLastCalledWith(
      "https://api.example.test/clients/cpc/analyze",
      expect.objectContaining({
        body: JSON.stringify({
          season: 2026,
          asker: 4,
          sides: [
            { roster_id: 4, gives: [{ player_id: "7569", to: 12 }] },
            { roster_id: 12, gives: [{ player_id: "10236", to: 4 }] },
          ],
        }),
      }),
    );
    expect(screen.queryByRole("button", { name: "Remove Garrett Wilson" })).toBeNull();
  });

  it("shows the empty Stack: the title, two slots, 2 of 4, two empty cards, the line, and the bar turned off", () => {
    expect(screen.getByRole("heading", { level: 1, name: "Trade Analyzer" })).toBeTruthy();
    expect(screen.getByText("Who gets what?")).toBeTruthy();
    const row = screen.getByRole("list", { name: "Teams in the trade" });
    expect(within(row).getByRole("button", { name: "Pick Your Team" })).toBeTruthy();
    expect(within(row).getByRole("button", { name: "Pick Team Two" })).toBeTruthy();
    expect(within(row).getByRole("button", { name: "Add a team" })).toBeTruthy();
    expect(within(row).getByText("2 of 4")).toBeTruthy();
    expect(screen.getAllByRole("heading", { level: 3 }).map((h) => h.textContent)).toEqual([
      "Your Team gets",
      "Team Two gets",
    ]);
    expect(rowsOf("Your Team")).toEqual([]);
    expect(rowsOf("Team Two")).toEqual([]);
    expect(screen.getByText("Each team gives and gets at least one player.")).toBeTruthy();
    expect(submit().disabled).toBe(true);
    // No card can add a player before both sides have a team.
    expect(addPlayer("Your Team").disabled).toBe(true);
  });

  it("keeps the bar off until the teams arrive, so a grade never starts with an empty stage (AT-29)", () => {
    cleanup();
    // A link fills the Stack before the rosters arrive. The trade is complete, but the stage and the lines need the teams.
    const prefill = [
      { id: 0, rosterId: 4, gets: [{ playerId: "p4", fromSide: 1 }] },
      { id: 1, rosterId: 12, gets: [{ playerId: "p1", fromSide: 0 }] },
    ];
    const props = { target: apiTarget, finderOn, passphrase: "localtest", onUnauthorized, prefill };
    const { rerender } = render(<TradeForm teams={[]} {...props} />);
    expect(submit().disabled).toBe(true);
    rerender(<TradeForm teams={TEAMS} {...props} />);
    expect(submit().disabled).toBe(false);
  });

  it("shows each team with its avatar, name, and manager in the team sheet", async () => {
    fireEvent.click(slot("Your Team"));
    const rows = within(await screen.findByRole("list", { name: "Teams" })).getAllByRole("button");
    expect(rows.map((r) => r.textContent)).toEqual([
      "Pukancun on 3Ana",
      "Blitz BakersBen",
      "Punt PunksCy",
    ]);
    expect(rows[0].querySelector("img")!.getAttribute("src")).toBe("https://cdn.test/ana.png");
    // A team with no avatar shows the default image.
    expect(rows[1].querySelector("img")!.getAttribute("src")).toContain(
      "/images/avatar-default.svg",
    );
  });

  it("shows the picked team's avatar in its slot and its name on its card", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    expect(slot("Your Team").getAttribute("aria-label")).toBe(
      "Your Team: Pukancun on 3. Change the team",
    );
    expect(slot("Your Team").querySelector("img")!.getAttribute("src")).toBe(
      "https://cdn.test/ana.png",
    );
    expect(within(card("Your Team")).getByText("Pukancun on 3")).toBeTruthy();
  });

  it("swaps a failed avatar to the default image once", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    const img = slot("Your Team").querySelector("img")!;
    fireEvent.error(img);
    expect(img.getAttribute("src")).toContain("/images/avatar-default.svg");
  });

  it("dims a team that is in the trade in the team sheet", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    fireEvent.click(slot("Team Two"));
    const list = within(await screen.findByRole("list", { name: "Teams" }));
    expect(
      (list.getByRole("button", { name: /Pukancun on 3/ }) as HTMLButtonElement).disabled,
    ).toBe(true);
    expect(list.getByRole("button", { name: /Pukancun on 3/ }).textContent).toContain(
      "In the trade",
    );
    expect((list.getByRole("button", { name: /Blitz Bakers/ }) as HTMLButtonElement).disabled).toBe(
      false,
    );
  });

  it("opens the picker with a tab for each other team, a search field, and the position chips", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    await pickTeam("Team Two", "Blitz Bakers");
    fireEvent.click(addPlayer("Your Team"));
    const open = within(await screen.findByRole("dialog"));
    expect(open.getByRole("heading", { name: "Your Team gets" })).toBeTruthy();
    expect(open.getAllByRole("tab").map((t) => t.textContent)).toEqual(["Blitz Bakers"]);
    expect(open.getByRole("searchbox", { name: "Search players" })).toBeTruthy();
    expect(
      within(open.getByRole("group", { name: "Position" }))
        .getAllByRole("button")
        .map((b) => b.textContent),
    ).toEqual(["All", "QB", "RB", "WR", "TE", "DEF"]);
    const rows = open.getAllByRole("checkbox");
    expect(rows.map((r) => r.textContent)).toEqual(["Ben OneRB NYJ", "Ben TwoWR NYJ"]);
    expect(rows[0].querySelector("img")!.getAttribute("src")).toBe("https://cdn.test/p3.png");
  });

  it("filters the players by the search and by a position chip", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    await pickTeam("Team Two", "Blitz Bakers");
    fireEvent.click(addPlayer("Team Two"));
    const open = within(await screen.findByRole("dialog"));
    fireEvent.click(open.getByRole("button", { name: "QB" }));
    expect(open.getAllByRole("checkbox").map((r) => r.textContent)).toEqual(["Ana TwoQB NYJ"]);
    fireEvent.click(open.getByRole("button", { name: "All" }));
    fireEvent.change(open.getByRole("searchbox"), { target: { value: "one" } });
    expect(open.getAllByRole("checkbox").map((r) => r.textContent)).toEqual(["Ana OneWR NYJ"]);
  });

  it("toggles a check with a tap on a row, and the Done button counts the picks", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    await pickTeam("Team Two", "Blitz Bakers");
    fireEvent.click(addPlayer("Your Team"));
    const open = within(await screen.findByRole("dialog"));
    const benOne = open.getByRole("checkbox", { name: /Ben One/ });
    fireEvent.click(benOne);
    fireEvent.click(open.getByRole("checkbox", { name: /Ben Two/ }));
    expect(benOne.getAttribute("aria-checked")).toBe("true");
    expect(open.getByRole("button", { name: "Done · 2" })).toBeTruthy();
    fireEvent.click(benOne);
    expect(benOne.getAttribute("aria-checked")).toBe("false");
    expect(open.getByRole("button", { name: "Done · 1" })).toBeTruthy();
  });

  it("lists each picked player on the card with a from tag, after Done", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    await pickTeam("Team Two", "Blitz Bakers");
    await pickPlayers("Your Team", "Blitz Bakers", "Ben Two", "Ben One");
    expect(rowsOf("Your Team")).toEqual([
      "Ben TwoWR NYJ · from Blitz Bakers",
      "Ben OneRB NYJ · from Blitz Bakers",
    ]);
  });

  it("closes the picker with the close button and keeps the picks", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    await pickTeam("Team Two", "Blitz Bakers");
    fireEvent.click(addPlayer("Your Team"));
    fireEvent.click(
      within(await screen.findByRole("dialog")).getByRole("checkbox", { name: /Ben Two/ }),
    );
    fireEvent.click(within(sheet()).getByRole("button", { name: "Close" }));
    await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
    expect(rowsOf("Your Team")).toEqual(["Ben TwoWR NYJ · from Blitz Bakers"]);
  });

  it("closes the picker with a tap on the dim page and keeps the picks", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    await pickTeam("Team Two", "Blitz Bakers");
    fireEvent.click(addPlayer("Your Team"));
    fireEvent.click(
      within(await screen.findByRole("dialog")).getByRole("checkbox", { name: /Ben Two/ }),
    );
    const dim = document.querySelector<HTMLElement>('[data-slot="drawer-backdrop"]')!;
    // A tap is a press, a release, and a click, as in a browser. The press closes the sheet and removes the dim, so the click lands on the page.
    const mouse = { pointerId: 1, pointerType: "mouse", button: 0 };
    fireEvent.pointerDown(dim, mouse);
    fireEvent.pointerUp(dim, mouse);
    fireEvent.click(document.body);
    await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
    expect(rowsOf("Your Team")).toEqual(["Ben TwoWR NYJ · from Blitz Bakers"]);
  });

  it("removes a player from a card with its remove control", async () => {
    await pickTeam("Your Team", "Pukancun on 3");
    await pickTeam("Team Two", "Blitz Bakers");
    await pickPlayers("Your Team", "Blitz Bakers", "Ben Two", "Ben One");
    fireEvent.click(removeButton("Ben Two"));
    // The row animates out, so it leaves the page a moment after the click.
    await waitFor(() =>
      expect(screen.queryByRole("button", { name: "Remove Ben Two" })).toBeNull(),
    );
    expect(rowsOf("Your Team")).toEqual(["Ben OneRB NYJ · from Blitz Bakers"]);
  });

  it("keeps the bar off until each team gives and gets a player", async () => {
    expect(submit().disabled).toBe(true);
    await pickTeam("Your Team", "Pukancun on 3");
    await pickTeam("Team Two", "Blitz Bakers");
    await pickPlayers("Your Team", "Blitz Bakers", "Ben Two");
    expect(submit().disabled).toBe(true);
    await pickPlayers("Team Two", "Pukancun on 3", "Ana One");
    expect(submit().disabled).toBe(false);
    fireEvent.click(removeButton("Ben Two"));
    expect(submit().disabled).toBe(true);
  });

  it("brightens the Ready halo with each check, reaches full only when the bar can grade, and dims on a remove", async () => {
    // The halo is decoration, so it carries its level as data, and its opacity is the brightness the reader sees.
    const halo = () => document.querySelector<HTMLElement>("[data-halo]")!;
    const level = () => Number(halo().dataset.level);
    const orbit = () => document.querySelector("[data-orbit]");
    expect(level()).toBe(0);
    // The orbit sweep turns only above level 0, so the off button has none.
    expect(orbit()).toBeNull();
    await pickTeam("Your Team", "Pukancun on 3");
    await pickTeam("Team Two", "Blitz Bakers");
    // Two teams and no player: 2 of 6, brighter than no team and below full.
    expect(level()).toBeCloseTo(2 / 6, 2);
    expect(orbit()).not.toBeNull();
    expect(Number(halo().style.opacity)).toBeGreaterThan(0);
    await pickPlayers("Your Team", "Blitz Bakers", "Ben Two");
    expect(level()).toBeCloseTo(4 / 6, 2);
    expect(submit().disabled).toBe(true);
    await pickPlayers("Team Two", "Pukancun on 3", "Ana One");
    expect(level()).toBe(1);
    expect(halo().style.opacity).toBe("1");
    expect(submit().disabled).toBe(false);
    fireEvent.click(removeButton("Ben Two"));
    // The remove takes the get of Your Team and the give of Team Two: 4 of 6.
    expect(level()).toBeCloseTo(4 / 6, 2);
    expect(Number(halo().style.opacity)).toBeLessThan(1);
    expect(submit().disabled).toBe(true);
  });

  it("drops the players a side gives when its team changes, and keeps the players it gets", async () => {
    await pickTrade(TRADE);
    await pickTeam("Team Two", "Punt Punks");
    expect(submit().disabled).toBe(true);
    await waitFor(() =>
      expect(screen.queryByRole("button", { name: "Remove Ben Two" })).toBeNull(),
    );
    expect(rowsOf("Team Two")).toEqual(["Ana OneWR NYJ · from Pukancun on 3"]);
  });

  it("keeps the result behind the sheet when a side's team changes", async () => {
    answer(200, fixtureJson);
    await pickTrade(TRADE);
    fireEvent.click(submit());
    await screen.findByRole("heading", { level: 2, name: "Lean yes" });
    edit();
    const result = screen.getByRole("heading", { level: 2, name: "Lean yes", hidden: true });
    await pickTeam("Your Team", "Punt Punks");
    expect(result.isConnected).toBe(true);
  });

  it("posts the asker first, with the destination of each player, as main does", async () => {
    answer(200, fixtureJson);
    await pickTrade(TRADE);
    fireEvent.click(submit());
    await screen.findByRole("heading", { level: 2, name: "Lean yes" });

    const [url, init] = fetchStub.mock.calls[0];
    expect(url).toBe("https://api.example.test/clients/cpc/analyze");
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

  it("counts a grade event on submit", async () => {
    const count = mock();
    window.goatcounter = { count };
    answer(200, fixtureJson);
    await pickTrade(TRADE);
    fireEvent.click(submit());
    await screen.findByRole("heading", { level: 2, name: "Lean yes" });
    expect(count).toHaveBeenCalledWith({ path: "analyze-grade", event: true });
    delete window.goatcounter;
  });

  it("puts the title hero in the slots: the name of the tool, the title, and the line under it, with no empty slot", () => {
    const hero = screen.getByRole("region", { name: "Trade Analyzer" });
    expect(slotsOf(hero)).toEqual(["eyebrow", "title", "meta"]);
    expect(slotText(hero, "eyebrow")).toBe("Trade Analyzer");
    expect(within(hero).getByRole("heading", { level: 1 }).textContent).toBe("Trade Analyzer");
    expect(slotText(hero, "meta")).toBe("Who gets what?");
  });

  it("keeps the art layer and the brackets in the title hero before a grade, with no scene (AT-35, AT-44)", () => {
    const hero = screen.getByRole("region", { name: "Trade Analyzer" });
    expect(document.querySelectorAll("canvas[data-hero-scene]")).toHaveLength(0);
    // The art layer holds the mesh, which draws the grid and the glow, and the four brackets sit in the corners.
    expect(hero.querySelectorAll("[data-hero-art='texture']")).toHaveLength(1);
    expect(hero.querySelectorAll("[data-hero-art='bracket']")).toHaveLength(4);
  });

  it("draws no scene in the grading hero", async () => {
    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    await pickTrade(TRADE);
    fireEvent.click(submit());
    const hero = await screen.findByRole("region", { name: "Grading the Trade" });
    expect(hero.querySelector("canvas[data-hero-scene]")).toBeNull();
  });

  it("keeps the trade on the stage in the wait, with no sweep and no grey bars (AT-5)", async () => {
    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    await pickTrade(TRADE);
    fireEvent.click(submit());
    const hero = await screen.findByRole("region", { name: "Grading the Trade" });
    // The mesh weighs the sides, so each side and the players it gets stay on the stage through the wait.
    expect(stageRow(hero, TRADE.mine)).toBeTruthy();
    expect(stageRow(hero, TRADE.other)).toBeTruthy();
    expect(stageHeadshots(stageRow(hero, TRADE.mine))).toEqual(["https://cdn.test/p4.png"]);
    expect(stageHeadshots(stageRow(hero, TRADE.other))).toEqual(["https://cdn.test/p1.png"]);
    // The track of a sweep is aria-hidden, so the query includes hidden elements. An image with no alt is presentation too, so the query skips images.
    expect(
      within(hero)
        .queryAllByRole("presentation", { hidden: true })
        .filter((el) => el.tagName !== "IMG"),
    ).toEqual([]);
    expect(hero.querySelector(".animate-pulse")).toBeNull();
  });

  it("shows a row per side with a count and no headshot in idle, as the Stack shows each player (AT-2, AT-28)", async () => {
    await pickTeam("Your Team", TRADE.mine);
    await pickTeam("Team Two", TRADE.other);
    await pickPlayers("Your Team", TRADE.other, "Ben One", "Ben Two");
    await pickPlayers("Team Two", TRADE.mine, "Ana One");
    const hero = screen.getByRole("region", { name: "Trade Analyzer" });
    expect(within(stageRow(hero, TRADE.mine)).getByText("2 players")).toBeTruthy();
    expect(within(stageRow(hero, TRADE.other)).getByText("1 player")).toBeTruthy();
    expect(stageHeadshots(hero)).toEqual([]);
    expect(within(hero).queryByText("Ben One")).toBeNull();
  });

  it("puts the headshots of each side into its row on the tap of Grade (AT-29)", async () => {
    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    await pickTeam("Your Team", TRADE.mine);
    await pickTeam("Team Two", TRADE.other);
    await pickPlayers("Your Team", TRADE.other, "Ben One", "Ben Two");
    await pickPlayers("Team Two", TRADE.mine, "Ana One");
    fireEvent.click(submit());
    const hero = await screen.findByRole("region", { name: "Grading the Trade" });
    expect(stageHeadshots(stageRow(hero, TRADE.mine))).toEqual([
      "https://cdn.test/p3.png",
      "https://cdn.test/p4.png",
    ]);
    expect(stageHeadshots(stageRow(hero, TRADE.other))).toEqual(["https://cdn.test/p1.png"]);
    expect(within(hero).queryByText("2 players")).toBeNull();
  });

  it("puts the same rows on the result hero, one mesh anchor per side, asker first", async () => {
    answer(200, fixtureJson);
    await pickTrade(TRADE);
    fireEvent.click(submit());
    const heroRead = await screen.findByRole("region", { name: "The Read" });
    // The rows replace the empty columns, so the hero holds one anchor per side and the dip of the reveal sits under a row.
    const rows = [...heroRead.querySelectorAll("[data-mesh-anchor]")];
    expect(rows.map((row) => row.querySelector("[data-stage-team]")?.textContent)).toEqual([
      "Pukancun on 3",
      "Amon-Ra Dawg Your Team",
    ]);
    expect(stageHeadshots(rows[0] as HTMLElement)).toEqual([
      "https://sleepercdn.com/content/nfl/players/10236.jpg",
      "https://sleepercdn.com/content/nfl/players/8146.jpg",
    ]);
    expect(stageHeadshots(rows[1] as HTMLElement)).toEqual([
      "https://sleepercdn.com/content/nfl/players/7569.jpg",
    ]);
    // The avatar of a team comes from the teams of the league.
    expect(rows[0].querySelector("img")?.getAttribute("src")).toBe("https://cdn.test/ana.png");
  });

  it("puts the grading hero in the slots: the eyebrow of the page, the title, the line, and the loading state", async () => {
    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    await pickTrade(TRADE);
    fireEvent.click(submit());
    const hero = await screen.findByRole("region", { name: "Grading the Trade" });
    expect(slotsOf(hero)).toEqual(["eyebrow", "title", "meta", "feature"]);
    expect(slotText(hero, "eyebrow")).toBe("Trade Analyzer");
    expect(within(hero).getByRole("heading", { level: 2 }).textContent).toBe("Grading the Trade");
    expect(slotText(hero, "meta")).toBe("This can take up to a minute.");
    const feature = hero.querySelector("[data-hero-slot=feature]") as HTMLElement;
    expect(feature.querySelector("[aria-busy=true]")).not.toBeNull();
  });

  it("shows the loading line while the grade runs", async () => {
    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    await pickTrade(TRADE);
    fireEvent.click(submit());
    expect(await screen.findByText("Grading the Trade")).toBeTruthy();
    expect(screen.getByText("This can take up to a minute.")).toBeTruthy();
    expect(screen.queryByText(/chart/i)).toBeNull();
    // The label turns to Grading… while the grade runs, and the button stays pending instead of natively disabled.
    const busy = screen.getByRole("button", { name: "Grading…" }) as HTMLButtonElement;
    expect(busy.getAttribute("aria-busy")).toBe("true");
    expect(busy.disabled).toBe(false);
  });

  it("keeps focus on the grade button, with the label Grading…, through the wait (AT-4)", async () => {
    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    await pickTrade(TRADE);
    submit().focus();
    fireEvent.click(submit());
    await screen.findByRole("region", { name: "Grading the Trade" });
    const busy = screen.getByRole("button", { name: "Grading…" });
    expect(busy.getAttribute("aria-busy")).toBe("true");
    expect(busy.hasAttribute("data-pending")).toBe(true);
    expect(busy.getAttribute("aria-disabled")).toBe("true");
    expect(busy.textContent).toBe("Grading…");
    expect(document.activeElement).toBe(busy);
  });

  it("shows stage lines of the trade under the title, hidden from a screen reader, with one status label (AT-6, AT-9)", async () => {
    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    await pickTrade(TRADE);
    fireEvent.click(submit());
    const hero = await screen.findByRole("region", { name: "Grading the Trade" });
    const line = hero.querySelector(".t-think-text:last-child") as HTMLElement;
    expect(line.textContent).toBe("Weighing the sides");
    // The lines sit inside a part that a screen reader skips. The page holds one status, the pending announcement of
    // the grade button, so a screen reader hears one message.
    expect(line.closest("[aria-hidden=true]")).not.toBeNull();
    expect(within(hero).queryByRole("status")).toBeNull();
    await screen.findByText("Grading the trade", {}, { timeout: 2500 });
    const statuses = screen.getAllByRole("status");
    expect(statuses.map((status) => status.textContent)).toEqual(["Grading the trade"]);
    expect(statuses[0].hasAttribute("aria-label")).toBe(false);
    expect(
      within(hero).queryByText("Weighing the sides", { ignore: "[aria-hidden=true] *" }),
    ).toBeNull();
  });

  it("names a player, a team, or a manager of the trade in a stage line", async () => {
    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    await pickTrade(TRADE);
    // The clock starts after the picks, so the picks keep the real timers. The hero mounts in the click.
    const clock = fakeTimeouts();
    fireEvent.click(submit());
    const hero = screen.getByRole("region", { name: "Grading the Trade" });
    const seen: string[] = [];
    for (let i = 0; i < 12; i++) {
      seen.push(hero.querySelector(".t-think-text:last-child")?.textContent ?? "");
      await act(async () => void clock.advance(2500));
    }
    expect(
      seen.some((text) => /Ben Two|Ana One|Pukancun on 3|Blitz Bakers|Ana|Ben/.test(text)),
    ).toBe(true);
  });

  it("sends one POST to the analyze route with a JSON body and takes a JSON response (AT-26)", async () => {
    answer(200, fixtureJson);
    await pickTrade(TRADE);
    fireEvent.click(submit());
    await waitFor(() => expect(fetchStub).toHaveBeenCalledTimes(1));
    const [url, init] = fetchStub.mock.calls[0];
    expect(String(url)).toContain("/analyze");
    expect(init.method).toBe("POST");
    expect(() => JSON.parse(init.body)).not.toThrow();
    expect(new Headers(init.headers).get("content-type")).toContain("application/json");
  });

  it("hides the form, shows no fold line, and puts the grading hero in place of the title while the grade runs", async () => {
    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    await pickTrade(TRADE);
    fireEvent.click(submit());
    const hero = await screen.findByRole("region", { name: "Grading the Trade" });
    expect(hero.querySelector("[aria-busy=true]")).not.toBeNull();
    expect(screen.queryByRole("heading", { level: 1, name: "Trade Analyzer" })).toBeNull();
    expect(screen.queryByRole("region", { name: "Who gets what" })).toBeNull();
    // The stage of the hero shows the trade, so no fold line repeats it above the hero.
    expect(screen.queryByRole("group", { name: "The trade" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Edit the trade" })).toBeNull();
    expect(stageRow(hero, TRADE.mine)).toBeTruthy();
    expect(stageRow(hero, TRADE.other)).toBeTruthy();
  });

  it("fills the hero with the read and the fairness block, and keeps the form hidden with Edit in the header of The Sides", async () => {
    answer(200, fixtureJson);
    await pickTrade(TRADE);
    fireEvent.click(submit());
    const heroRead = await screen.findByRole("region", { name: "The Read" });
    expect(within(heroRead).getByText("The read for Pukancun on 3")).toBeTruthy();
    expect(within(heroRead).getByRole("heading", { level: 2, name: "Lean yes" })).toBeTruthy();
    expect(within(heroRead).getByText("Fairness")).toBeTruthy();
    // The read is the hero, so the title hero and the grading hero are gone.
    expect(screen.queryByRole("heading", { level: 1, name: "Trade Analyzer" })).toBeNull();
    expect(screen.queryByRole("region", { name: "Grading the Trade" })).toBeNull();
    expect(screen.queryByRole("region", { name: "Who gets what" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Grade the Trade" })).toBeNull();
    expect(screen.queryByRole("group", { name: "The trade" })).toBeNull();
    expect(screen.queryByRole("heading", { name: "The Trade" })).toBeNull();
    // Edit sits in the header of The Sides, after its heading and before the tabs of the sides.
    const sides = screen.getByRole("heading", { level: 2, name: "The Sides" });
    const header = sides.parentElement as HTMLElement;
    const editButton = within(header).getByRole("button", { name: "Edit the trade" });
    expect(editButton.textContent).toBe("Edit");
    expect(editButton.querySelector("svg[aria-hidden='true']")).not.toBeNull();
    expect(heroRead.compareDocumentPosition(sides) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(
      editButton.compareDocumentPosition(screen.getByRole("tablist", { name: "The sides" })) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
  });

  it("draws no scene under a folded result or after Edit, as each hero of the analyzer is static (AT-35, AT-44)", async () => {
    answer(200, fixtureJson);
    await pickTrade(TRADE);
    fireEvent.click(submit());
    const heroRead = await screen.findByRole("region", { name: "The Read" });
    expect(document.querySelectorAll("canvas[data-hero-scene]")).toHaveLength(0);
    // The static hero: the texture layer holds the grid and the glow, and the four brackets sit in the corners.
    expect(heroRead.querySelectorAll("[data-hero-art='texture']")).toHaveLength(1);
    expect(heroRead.querySelectorAll("[data-hero-art='bracket']")).toHaveLength(4);
    edit();
    expect(screen.getByRole("dialog", { name: "Edit the trade" })).toBeTruthy();
    expect(heroRead.isConnected).toBe(true);
    expect(document.querySelectorAll("canvas[data-hero-scene]")).toHaveLength(0);
  });

  it("opens the Stack in a sheet with the graded trade and keeps the result in place", async () => {
    answer(200, fixtureJson);
    await pickTrade(TRADE);
    fireEvent.click(submit());
    await screen.findByRole("heading", { level: 2, name: "Lean yes" });
    fireEvent.click(screen.getByRole("button", { name: "Edit the trade" }));
    const editor = screen.getByRole("dialog", { name: "Edit the trade" });
    expect(within(editor).getByRole("region", { name: "Who gets what" })).toBeTruthy();
    expect(scrolled).toEqual([]);
    expect(rowsOf("Your Team")).toEqual(["Ben TwoWR NYJ · from Blitz Bakers"]);
    expect(regrade().disabled).toBe(false);
    expect(screen.queryByRole("group", { name: "The trade" })).toBeNull();
    expect(screen.getByRole("region", { name: "The Read", hidden: true })).toBeTruthy();
  });

  it("locks the slots, the add buttons, and the remove controls while the grade runs, and unlocks them on the result", async () => {
    let finish!: (response: Response) => void;
    fetchStub.mockReturnValueOnce(new Promise<Response>((resolve) => (finish = resolve)));
    await pickTrade(TRADE);
    // The grade folds the form out of view, so the test holds each control before the tap.
    const controls = [
      slot("Your Team"),
      slot("Team Two"),
      addPlayer("Your Team"),
      addPlayer("Team Two"),
    ];
    const removeAnaOne = removeButton("Ana One");
    fireEvent.click(submit());
    await screen.findByText("Grading the Trade");

    expect(controls.every((c) => c.disabled)).toBe(true);
    fireEvent.click(controls[2]);
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(removeAnaOne.disabled).toBe(true);
    fireEvent.click(removeAnaOne);
    expect(removeAnaOne.isConnected).toBe(true);

    await act(async () => finish(new Response(JSON.stringify(fixtureJson), { status: 200 })));
    await screen.findByRole("heading", { level: 2, name: "Lean yes" });
    edit();
    expect(controls.some((c) => c.disabled)).toBe(false);
    expect(regrade().hasAttribute("aria-busy")).toBe(false);
    await pickPlayers("Team Two", "Pukancun on 3", "Ana Two");
    expect(removeButton("Ana Two")).toBeTruthy();
  });

  it("unlocks the form after a 422, so a tap fixes the trade", async () => {
    answer(422, { detail: { message: "Player p1 is not on the giving roster.", player_id: "p1" } });
    await pickTrade(TRADE);
    fireEvent.click(submit());
    await screen.findByText("Player p1 is not on the giving roster.");
    expect(removeButton("Ana One").disabled).toBe(false);
    fireEvent.click(removeButton("Ana One"));
    await waitFor(() =>
      expect(screen.queryByRole("button", { name: "Remove Ana One" })).toBeNull(),
    );
    expect(slot("Team Two").disabled).toBe(false);
  });

  it("unlocks the form after a 429", async () => {
    answer(429, { detail: "slow down" }, { "Retry-After": "12" });
    await pickTrade(TRADE);
    fireEvent.click(submit());
    await screen.findByText("Too many requests. Try again in 12 seconds.");
    await pickPlayers("Team Two", "Pukancun on 3", "Ana Two");
    expect(removeButton("Ana Two")).toBeTruthy();
  });

  it("clears the old result when a new submit starts", async () => {
    answer(200, fixtureJson);
    await pickTrade(TRADE);
    fireEvent.click(submit());
    await screen.findByRole("heading", { level: 2, name: "Lean yes" });
    edit();

    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    fireEvent.click(regrade());
    await screen.findByText("Grading the Trade");
    expect(screen.queryByRole("heading", { level: 2, name: "Lean yes" })).toBeNull();
  });

  it("shows the API message on a 422", async () => {
    answer(422, { detail: { message: "Player p1 is not on the giving roster.", player_id: "p1" } });
    await pickTrade(TRADE);
    fireEvent.click(submit());
    expect(await screen.findByText("Player p1 is not on the giving roster.")).toBeTruthy();
  });

  it.each([
    [
      "a 422",
      422,
      { detail: { message: "Player p1 is not on the giving roster.", player_id: "p1" } },
      {},
      "Player p1 is not on the giving roster.",
    ],
    [
      "a 429",
      429,
      { detail: "slow down" },
      { "Retry-After": "12" },
      "Too many requests. Try again in 12 seconds.",
    ],
    ["a 502", 502, { detail: "bad shape" }, {}, "The API sent an answer the site cannot read."],
    [
      "a 410 of a closed trade route (AT-15)",
      410,
      { closed: true, line: "The trade deadline has passed. Trades open again next season." },
      {},
      "The trade deadline has passed. Trades open again next season.",
    ],
  ])(
    "shows Try Again under the line of toErrorLine on %s",
    async (_name, status, body, headers, line) => {
      answer(status, body, headers);
      await pickTrade(TRADE);
      fireEvent.click(submit());
      const box = await screen.findByRole("group", { name: "The grade failed" });
      expect(within(box).getByRole("alert").textContent).toBe(line);
      expect(within(box).getByRole("button", { name: "Try Again" })).toBeTruthy();
    },
  );

  it("shows the wait time on a 429", async () => {
    answer(429, { detail: "slow down" }, { "Retry-After": "12" });
    await pickTrade(TRADE);
    fireEvent.click(submit());
    expect(await screen.findByText("Too many requests. Try again in 12 seconds.")).toBeTruthy();
  });

  it("shows the down line and a retry button on a 503 with no detail", async () => {
    answer(503);
    await pickTrade(TRADE);
    fireEvent.click(submit());
    expect(
      await screen.findByText("The analyzer is down for the moment. Try again in a few minutes."),
    ).toBeTruthy();
    expect(screen.getByRole("button", { name: "Try Again" })).toBeTruthy();
  });

  it("unlocks the form and puts the message, the alert icon, and Try Again in one box above the bar", async () => {
    answer(500);
    await pickTrade(TRADE);
    fireEvent.click(submit());
    const box = await screen.findByRole("group", { name: "The grade failed" });
    expect(within(box).getByRole("alert").textContent).toBe("The API did not answer. Try again.");
    expect(box.querySelector("svg[aria-hidden='true']")).not.toBeNull();
    expect(within(box).getByRole("button", { name: "Try Again" })).toBeTruthy();
    expect(screen.getByRole("heading", { level: 1, name: "Trade Analyzer" })).toBeTruthy();
    expect(screen.queryByRole("group", { name: "The trade" })).toBeNull();
    expect(slot("Your Team").disabled).toBe(false);
    expect(box.compareDocumentPosition(submit()) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("shows the API reason on a 503 with a detail", async () => {
    answer(503, { detail: "The trade value chart is not ready." });
    await pickTrade(TRADE);
    fireEvent.click(submit());
    expect(await screen.findByText("The trade value chart is not ready.")).toBeTruthy();
  });

  it("shows the plain error of a failed read with Try Again, and no Lean (AT-49)", async () => {
    const message =
      "The read of this trade did not come through. Try again in a minute. This try does not count toward your grades.";
    answer(503, { detail: { message } });
    await pickTrade(TRADE);
    fireEvent.click(submit());
    expect(await screen.findByText(message)).toBeTruthy();
    expect(screen.getByRole("button", { name: "Try Again" })).toBeTruthy();
    for (const lean of ["Send it", "Lean yes", "Gut call", "Lean no", "Pass"]) {
      expect(screen.queryByText(lean)).toBeNull();
    }
    expect(screen.queryByRole("region", { name: "The Read" })).toBeNull();
  });

  it("asks for the passphrase again on a 401", async () => {
    answer(401, { detail: "bad passphrase" });
    await pickTrade(TRADE);
    fireEvent.click(submit());
    await waitFor(() => expect(onUnauthorized).toHaveBeenCalledTimes(1));
  });

  it("shows a retry button on another failure, and the button posts again", async () => {
    answer(500);
    await pickTrade(TRADE);
    fireEvent.click(submit());
    expect(await screen.findByText("The API did not answer. Try again.")).toBeTruthy();

    answer(200, fixtureJson);
    fireEvent.click(screen.getByRole("button", { name: "Try Again" }));
    await screen.findByRole("heading", { level: 2, name: "Lean yes" });
    expect(fetchStub).toHaveBeenCalledTimes(2);
  });

  it("aborts after 60 seconds, shows the timeout line, and the retry posts again", async () => {
    await pickTrade(TRADE);
    // Only the timeout is fake. A fake clock for frames would leave Framer Motion on a stale time, so a later exit would stall.
    const clock = fakeTimeouts();
    fetchStub.mockImplementationOnce(
      (_url: string, init: RequestInit) =>
        new Promise((_resolve, reject) => {
          init.signal!.addEventListener("abort", () =>
            reject(new DOMException("aborted", "AbortError")),
          );
        }),
    );
    fireEvent.click(submit());
    await act(async () => void clock.advance(60_000));

    expect(screen.getByText("The grade took too long.")).toBeTruthy();
    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    fireEvent.click(screen.getByRole("button", { name: "Try Again" }));
    expect(fetchStub).toHaveBeenCalledTimes(2);
    expect(fetchStub.mock.calls[1][1].body).toBe(fetchStub.mock.calls[0][1].body);
  });

  it("aborts a pending grade on unmount without an error or a state update", async () => {
    const errorSpy = spyOn(console, "error").mockImplementation(() => {});
    let signal: AbortSignal | undefined;
    fetchStub.mockImplementationOnce(
      (_url: string, init: RequestInit) =>
        new Promise((_resolve, reject) => {
          signal = init.signal!;
          signal.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")));
        }),
    );
    await pickTrade(TRADE);
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
    {
      roster_id: 9,
      team: "Draft Dodgers",
      manager: "Dee",
      avatar: null,
      players: [player("p6", "Dee One")],
    },
  ];

  beforeEach(() => {
    cleanup();
    render(
      <TradeForm
        teams={FOUR_TEAMS}
        target={apiTarget}
        finderOn={finderOn}
        passphrase="localtest"
        onUnauthorized={onUnauthorized}
      />,
    );
  });

  async function pickTwoTeams() {
    await pickTeam("Your Team", "Pukancun on 3");
    await pickTeam("Team Two", "Blitz Bakers");
  }

  it("adds a third team from the team sheet, with a card, a remove button, and 3 of 4", async () => {
    await pickTwoTeams();
    fireEvent.click(screen.getByRole("button", { name: "Add a team" }));
    const list = within(await screen.findByRole("list", { name: "Teams" }));
    // Every team shows, and the two teams of the trade are dimmed.
    expect(list.getAllByRole("button").map((b) => (b as HTMLButtonElement).disabled)).toEqual([
      true,
      true,
      false,
      false,
    ]);
    expect(within(sheet()).getByRole("heading", { name: "Pick Team Three" })).toBeTruthy();
    await chooseTeam("Punt Punks");
    expect(within(card("Team Three")).getByText("Punt Punks")).toBeTruthy();
    expect(removeButton("Team Three")).toBeTruthy();
    expect(screen.getByText("3 of 4")).toBeTruthy();
  });

  it("adds a fourth team, then shows no + slot", async () => {
    await pickTwoTeams();
    await addTeam("Punt Punks");
    await addTeam("Draft Dodgers");
    expect(screen.getAllByRole("heading", { level: 3 }).map((h) => h.textContent)).toEqual([
      "Your Team gets",
      "Team Two gets",
      "Team Three gets",
      "Team Four gets",
    ]);
    expect(screen.queryByRole("button", { name: "Add a team" })).toBeNull();
    expect(removeButton("Team Four")).toBeTruthy();
  });

  it("gives a remove control to the third and fourth sides only", async () => {
    await pickTwoTeams();
    await addTeam("Punt Punks");
    expect(screen.queryByRole("button", { name: "Remove Your Team" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Remove Team Two" })).toBeNull();
    expect(removeButton("Team Three")).toBeTruthy();
  });

  it("shows a tab for each other team in the picker", async () => {
    await pickTwoTeams();
    await addTeam("Punt Punks");
    fireEvent.click(addPlayer("Team Three"));
    const open = within(await screen.findByRole("dialog"));
    expect(open.getAllByRole("tab").map((t) => t.textContent)).toEqual([
      "Pukancun on 3",
      "Blitz Bakers",
    ]);
    fireEvent.click(open.getByRole("tab", { name: "Pukancun on 3" }));
    expect(open.getAllByRole("checkbox").map((r) => r.textContent)).toEqual([
      "Ana OneWR NYJ",
      "Ana TwoQB NYJ",
    ]);
  });

  it("dims a player that another team already gets", async () => {
    await pickTwoTeams();
    await addTeam("Punt Punks");
    await pickPlayers("Team Two", "Pukancun on 3", "Ana One");
    fireEvent.click(addPlayer("Team Three"));
    const open = within(await screen.findByRole("dialog"));
    fireEvent.click(open.getByRole("tab", { name: "Pukancun on 3" }));
    const anaOne = open.getByRole("checkbox", { name: /Ana One/ }) as HTMLButtonElement;
    expect(anaOne.disabled).toBe(true);
    expect(anaOne.textContent).toContain("to Blitz Bakers");
  });

  it("takes a removed team and the players it gives out of the trade, and the slot reads 2 of 4 again", async () => {
    await pickTwoTeams();
    await addTeam("Punt Punks");
    await pickPlayers("Your Team", "Punt Punks", "Cy One");
    fireEvent.click(removeButton("Team Three"));
    await waitFor(() =>
      expect(screen.queryByRole("region", { name: "Team Three gets" })).toBeNull(),
    );
    expect(rowsOf("Your Team")).toEqual([]);
    expect(screen.getByText("2 of 4")).toBeTruthy();
  });

  it("keeps the bar off until every team gives and gets a player", async () => {
    await pickTwoTeams();
    await addTeam("Punt Punks");
    await pickPlayers("Your Team", "Blitz Bakers", "Ben Two");
    await pickPlayers("Team Two", "Pukancun on 3", "Ana One");
    expect(submit().disabled).toBe(true);
    await pickPlayers("Team Three", "Pukancun on 3", "Ana Two");
    expect(submit().disabled).toBe(true);
    await pickPlayers("Your Team", "Punt Punks", "Cy One");
    expect(submit().disabled).toBe(false);
  });

  it("puts a trade of three teams on the stage of the wait, one row per team, with no fold line", async () => {
    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    await pickTwoTeams();
    await addTeam("Punt Punks");
    await pickPlayers("Team Two", "Pukancun on 3", "Ana One");
    await pickPlayers("Team Three", "Pukancun on 3", "Ana Two");
    await pickPlayers("Team Three", "Blitz Bakers", "Ben Two");
    await pickPlayers("Your Team", "Punt Punks", "Cy One");
    fireEvent.click(submit());
    const hero = await screen.findByRole("region", { name: "Grading the Trade" });
    expect(screen.queryByRole("group", { name: "The trade" })).toBeNull();
    for (const team of ["Pukancun on 3", "Blitz Bakers", "Punt Punks"])
      expect(stageRow(hero, team)).toBeTruthy();
  });

  it("posts every side in order with the destination of each player, as main does", async () => {
    answer(200, fixtureJson);
    await pickTwoTeams();
    await addTeam("Punt Punks");
    await pickPlayers("Team Two", "Pukancun on 3", "Ana One");
    await pickPlayers("Team Three", "Pukancun on 3", "Ana Two");
    await pickPlayers("Team Three", "Blitz Bakers", "Ben Two");
    await pickPlayers("Your Team", "Punt Punks", "Cy One");
    fireEvent.click(submit());
    await screen.findByRole("heading", { level: 2, name: "Lean yes" });
    expect(JSON.parse(fetchStub.mock.calls[0][1].body)).toEqual({
      season: 2026,
      asker: 4,
      sides: [
        {
          roster_id: 4,
          gives: [
            { player_id: "p1", to: 12 },
            { player_id: "p2", to: 7 },
          ],
        },
        { roster_id: 12, gives: [{ player_id: "p4", to: 7 }] },
        { roster_id: 7, gives: [{ player_id: "p5", to: 4 }] },
      ],
    });
  });
});

/* The finder cards hand their trade to the form. Each fixture finder trade is between roster 2 and one partner, so these tests render those teams.
   The page owns the mode of the switch, so the tests hold it in a small parent, as the page does. */
describe("TradeForm with the finder", () => {
  afterEach(() => {
    finderOn = false;
  });

  const [first] = findJson.trades;
  // The partner of every fixture trade, as a pattern of its team name.
  const partnerName = first.sides[1].team;
  const partnerRow = new RegExp(partnerName);
  const pairTeams: Team[] = [
    ...first.sides.map((side) => ({
      roster_id: side.roster_id,
      team: side.team,
      manager: `Manager ${side.roster_id}`,
      avatar: null,
      // Every player of the fixture trades is on the roster of the side that gives him.
      players: findJson.trades.flatMap(
        (t) => t.sides.find((s) => s.roster_id === side.roster_id)!.gives,
      ),
    })),
    // A third team lets a test add a third side.
    {
      roster_id: 99,
      team: "Third Wheel",
      manager: "Tess",
      avatar: null,
      players: [player("p99", "Tess One")],
    },
  ];

  function WithModes() {
    const [mode, setMode] = useState<AnalyzerMode>("grade");
    return (
      <TradeForm
        teams={pairTeams}
        target={apiTarget}
        finderOn={finderOn}
        passphrase="localtest"
        onUnauthorized={onUnauthorized}
        mode={mode}
        onModeChange={setMode}
      />
    );
  }

  const modeHalf = (name: string) =>
    within(screen.getByRole("radiogroup", { name: "Mode" })).getByRole("radio", { name });
  const partnerButton = () => screen.getByRole("button", { name: /Trade with/ });

  /* Taps "Find a trade" on the switch and waits for the Find hero. */
  async function toFind() {
    fireEvent.click(modeHalf("Find a trade"));
    await screen.findByRole("heading", { level: 1, name: "Trade Ideas" });
    // The pill of the new hero moves to Find one frame after the swap.
    await waitFor(() => expect(modeHalf("Find a trade").getAttribute("aria-checked")).toBe("true"));
  }

  /* Picks the fixture partner in the sheet of Find and waits for the sheet to close. */
  async function pickPartner() {
    fireEvent.click(partnerButton());
    const rows = within(await screen.findByRole("list", { name: "Partners" })).getAllByRole(
      "button",
    );
    fireEvent.click(rows.find((row) => partnerRow.test(row.textContent ?? "")) as HTMLElement);
    await waitFor(() => expect(screen.queryByRole("list", { name: "Partners" })).toBeNull());
  }

  beforeEach(() => {
    cleanup();
    finderOn = true;
    render(<WithModes />);
  });

  it("shows the switch on Grade a trade when the flag is on", () => {
    expect(modeHalf("Grade a trade").getAttribute("aria-checked")).toBe("true");
    expect(screen.getByRole("heading", { level: 1, name: "Trade Analyzer" })).toBeTruthy();
  });

  it("puts Find in the hero in place of the form, with no finder under the cards", async () => {
    await pickTeam("Your Team", "All You Need Is Love");
    expect(screen.queryByRole("button", { name: /Trade with/ })).toBeNull();
    await toFind();
    expect(partnerButton()).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Grade the Trade" })).toBeNull();
    fireEvent.click(modeHalf("Grade a trade"));
    expect(await screen.findByRole("heading", { level: 1, name: "Trade Analyzer" })).toBeTruthy();
    expect(card("Your Team")).toBeTruthy();
  });

  it("shows no switch when the flag is off", async () => {
    finderOn = false;
    cleanup();
    render(<WithModes />);
    await pickTeam("Your Team", "All You Need Is Love");
    expect(screen.queryByRole("radiogroup", { name: "Mode" })).toBeNull();
  });

  it("keeps Find on with a third side in Grade mode", async () => {
    await pickTeam("Your Team", "All You Need Is Love");
    await pickTeam("Team Two", partnerName);
    await addTeam("Third Wheel");
    await toFind();
    expect(
      (screen.getByRole("button", { name: "Find a Trade" }) as HTMLButtonElement).disabled,
    ).toBe(false);
  });

  it("keeps Find off until my team is picked, and Your team of Find picks the team of Grade", async () => {
    await toFind();
    expect(
      (screen.getByRole("button", { name: "Find a Trade" }) as HTMLButtonElement).disabled,
    ).toBe(true);
    fireEvent.click(screen.getByRole("button", { name: /Your team/ }));
    const rows = within(await screen.findByRole("list", { name: "Teams" })).getAllByRole("button");
    fireEvent.click(
      rows.find((row) => row.textContent?.includes("All You Need Is Love")) as HTMLElement,
    );
    await waitFor(() =>
      expect(
        (screen.getByRole("button", { name: "Find a Trade" }) as HTMLButtonElement).disabled,
      ).toBe(false),
    );
    fireEvent.click(modeHalf("Grade a trade"));
    await waitFor(() =>
      expect(slot("Your Team").getAttribute("aria-label")).toContain("All You Need Is Love"),
    );
  });

  /* Finds with the fixture partner and taps "See the Full Result" on a card. A card with a read shows it at once. A
     card of a fallback has no read, so the form grades it, and the analyze route answers with the analyze fixture. */
  async function openCard(finderDoc: typeof findJson, index: number) {
    await pickTeam("Your Team", "All You Need Is Love");
    await toFind();
    await pickPartner();
    findStream(finderDoc);
    fireEvent.click(screen.getByRole("button", { name: "Find a Trade" }));
    const cards = await screen.findAllByRole("article");
    const lean = finderDoc.trades[index].lean;
    if (lean === null) answer(200, fixtureJson);
    fireEvent.click(within(cards[index]).getByRole("button", { name: "See the Full Result" }));
    await screen.findByRole("heading", { level: 2, name: lean ?? "Lean yes" });
  }

  it("resets the partner and the cards when my team changes", async () => {
    await pickTeam("Your Team", "All You Need Is Love");
    await toFind();
    await pickPartner();
    findStream(findJson);
    fireEvent.click(screen.getByRole("button", { name: "Find a Trade" }));
    await screen.findAllByRole("article");

    fireEvent.click(screen.getByRole("button", { name: /Your team/ }));
    const rows = within(await screen.findByRole("list", { name: "Teams" })).getAllByRole("button");
    fireEvent.click(rows.find((row) => partnerRow.test(row.textContent ?? "")) as HTMLElement);
    await waitFor(() =>
      expect(screen.getByRole("button", { name: /Your team/ }).textContent).toContain(partnerName),
    );
    expect(screen.queryAllByRole("article")).toHaveLength(0);
    expect(partnerButton().textContent).toContain("Every team");
    // With no partner, the search runs over every other team, so Find stays on.
    expect(
      (screen.getByRole("button", { name: "Find a Trade" }) as HTMLButtonElement).disabled,
    ).toBe(false);
  });

  it("scrolls the result into view after a card opens its full result", async () => {
    // jsdom has no scrollIntoView, so the test supplies one.
    const scrollIntoView = mock();
    Element.prototype.scrollIntoView = scrollIntoView;
    await openCard(findJson, 1);
    await waitFor(() => expect(scrollIntoView).toHaveBeenCalledTimes(1));
    expect(scrollIntoView).toHaveBeenCalledWith({ behavior: "smooth", block: "start" });
  });

  it("grades a card of a fallback, which has no read, with the season of the finder document", async () => {
    Element.prototype.scrollIntoView = mock();
    const trades = findJson.trades.map((trade) => ({
      ...trade,
      lean: null,
      case: null,
      bullets: [],
      fact_lines: ["A fact."],
    }));
    await openCard({ ...findJson, season: 2025, fallback: true, trades }, 1);
    const [url, init] = fetchStub.mock.calls[1];
    expect(url).toBe("https://api.example.test/clients/cpc/analyze");
    expect(JSON.parse(init.body).season).toBe(2025);
  });

  it("opens the trade of a card with the read of the find, with no analyze request, and the form holds the trade", async () => {
    Element.prototype.scrollIntoView = mock();
    await openCard(findJson, 1);
    const trade = findJson.trades[1];
    const read = screen.getByRole("region", { name: "The Read" });
    expect(read.textContent).toContain(trade.case!);
    // The find stream is the one request. The read comes with the find.
    expect(fetchStub.mock.calls.map(([url]) => url)).toEqual([
      "https://api.example.test/clients/cpc/find-stream",
    ]);
    // The read of a card shows in Grade mode, so Find leaves the page.
    expect(screen.queryByRole("heading", { name: "Trade Ideas" })).toBeNull();
    // The form shows the trade of the card, so the picks match the read, and an edit grades it again.
    const [mine, theirs] = trade.sides;
    edit();
    expect(slot("Team Two").getAttribute("aria-label")).toContain(partnerName);
    expect(
      within(card("Team Two")).getByRole("button", { name: `Remove ${mine.gives[0].name}` }),
    ).toBeTruthy();
    expect(
      within(card("Your Team")).getByRole("button", { name: `Remove ${theirs.gives[0].name}` }),
    ).toBeTruthy();
  });

  it("locks the switch in the grade wait and shows the eyebrow of the page, not Live", async () => {
    fetchStub.mockReturnValueOnce(new Promise(() => {}));
    // Each player of the asker shows in each fixture trade, so the trade goes with the third team, whose one player is plain.
    await pickTeam("Your Team", "Third Wheel");
    await pickTeam("Team Two", partnerName);
    await pickPlayers("Your Team", partnerName, first.sides[1].gives[0].name);
    await pickPlayers("Team Two", "Third Wheel", "Tess One");
    fireEvent.click(screen.getByRole("button", { name: "Grade the Trade" }));
    const hero = await screen.findByRole("region", { name: "Grading the Trade" });
    expect(slotText(hero, "eyebrow")).toBe("Trade Analyzer");
    const toggle = within(hero).getByRole("radiogroup", { name: "Mode" });
    expect(
      within(toggle).getByRole("radio", { name: "Grade a trade" }).getAttribute("aria-checked"),
    ).toBe("true");
    expect(
      within(toggle).getByRole("radio", { name: "Find a trade" }).hasAttribute("disabled") ||
        toggle.getAttribute("aria-disabled") === "true",
    ).toBe(true);
  });
});
