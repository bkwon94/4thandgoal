/**
 * Tests for the compact stage of the analyzer hero: one row per side, the count of idle, the headshot tokens with "+N", and the initials of a failed headshot.
 * The sides are trade B and trade T of the spec, real cpc trades of 2026, and each test reads the screen.
 */
import { cleanup, fireEvent, render, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { TradeOnStage, type StageSide } from "./trade-on-stage";

const headshot = (id: string) => `https://sleepercdn.com/content/nfl/players/${id}.jpg`;
const players = (list: [string, string][]) => list.map(([id, name]) => ({ id, name, headshot: headshot(id) }));

/* Trade B: The Blue Tent gets 5 from Lil Fridge, All You Need Is Love gets 2, and Lil Fridge gets 3. */
const TRADE_B: StageSide[] = [
  {
    id: 0,
    team: "The Blue Tent",
    avatar: null,
    players: players([
      ["11560", "Caleb Williams"],
      ["1466", "Travis Kelce"],
      ["2449", "Stefon Diggs"],
      ["3198", "Derrick Henry"],
      ["4034", "Christian McCaffrey"],
    ]),
  },
  {
    id: 1,
    team: "All You Need Is Love",
    avatar: null,
    players: players([
      ["10229", "Rashee Rice"],
      ["11604", "Brock Bowers"],
    ]),
  },
  {
    id: 2,
    team: "Lil Fridge",
    avatar: null,
    players: players([
      ["12527", "Ashton Jeanty"],
      ["13287", "Jeremiyah Love"],
      ["11584", "Bucky Irving"],
    ]),
  },
];

/* Trade T: Bo Girds gets Tee Higgins and Bhayshul Tuten, and Teehee gets Kenneth Walker III. */
const TRADE_T: StageSide[] = [
  { id: 0, team: "Bo Girds", avatar: null, players: players([["6801", "Tee Higgins"], ["12490", "Bhayshul Tuten"]]) },
  { id: 1, team: "Teehee", avatar: null, players: players([["8151", "Kenneth Walker III"]]) },
];

/* The row of a team on the stage, and the headshot images in it. The team avatar is not a headshot. */
const rowOf = (container: HTMLElement, team: string) => within(container).getByText(team).closest("li") as HTMLElement;
const headshotsIn = (el: HTMLElement) => [...el.querySelectorAll("img")].filter((img) => img.src.includes("/players/"));

afterEach(cleanup);

describe("TradeOnStage", () => {
  it("shows one row per side in order, each with its team, its avatar, and gets", () => {
    const { container } = render(<TradeOnStage sides={TRADE_B} show="tokens" />);
    const rows = [...container.querySelectorAll("li")];
    expect(rows).toHaveLength(3);
    expect(rows.map((row) => row.querySelector("[data-stage-team]")?.textContent)).toEqual(["The Blue Tent", "All You Need Is Love", "Lil Fridge"]);
    for (const row of rows) expect(within(row).getByText("gets")).toBeTruthy();
    // Each row is the place of its side, so the mesh dips under the right row.
    expect(container.querySelectorAll("[data-mesh-anchor]")).toHaveLength(3);
  });

  it("shows 3 headshots and +2 for a side of 5 players (AT-27)", () => {
    const { container } = render(<TradeOnStage sides={TRADE_B} show="tokens" />);
    const tent = rowOf(container, "The Blue Tent");
    expect(headshotsIn(tent).map((img) => img.src)).toEqual([headshot("11560"), headshot("1466"), headshot("2449")]);
    expect(within(tent).getByText("+2")).toBeTruthy();
    // A side of 3 or fewer shows each headshot and no count.
    expect(headshotsIn(rowOf(container, "Lil Fridge"))).toHaveLength(3);
    expect(within(rowOf(container, "Lil Fridge")).queryByText(/^\+/)).toBeNull();
  });

  it("shows a count and no headshot in idle (AT-28)", () => {
    const { container } = render(<TradeOnStage sides={TRADE_T} show="count" />);
    expect(within(rowOf(container, "Bo Girds")).getByText("2 players")).toBeTruthy();
    expect(within(rowOf(container, "Teehee")).getByText("1 player")).toBeTruthy();
    expect(headshotsIn(container)).toHaveLength(0);
  });

  it("shows a dashed empty token for a side with no player, in idle and with tokens", () => {
    const sides = [TRADE_T[0], { ...TRADE_T[1], players: [] }];
    for (const show of ["count", "tokens"] as const) {
      const { container, unmount } = render(<TradeOnStage sides={sides} show={show} />);
      const row = rowOf(container, "Teehee");
      expect(row.querySelector("[data-stage-empty]")).not.toBeNull();
      expect(within(row).queryByText(/player/)).toBeNull();
      unmount();
    }
  });

  it("shows the initials of the player when his headshot fails to load", () => {
    const { container } = render(<TradeOnStage sides={TRADE_T} show="tokens" />);
    const teehee = rowOf(container, "Teehee");
    fireEvent.error(headshotsIn(teehee)[0]);
    expect(headshotsIn(teehee)).toHaveLength(0);
    // The suffix of a name is not an initial, so Kenneth Walker III reads KW.
    expect(within(teehee).getByText("KW")).toBeTruthy();
  });

  it("shows the initials of a player with no headshot at all", () => {
    const sides = [TRADE_T[0], { ...TRADE_T[1], players: [{ id: "8151", name: "Kenneth Walker III", headshot: "" }] }];
    const { container } = render(<TradeOnStage sides={sides} show="tokens" />);
    expect(within(rowOf(container, "Teehee")).getByText("KW")).toBeTruthy();
  });

  it("names each player of a token for the eye, and hides the stage from a screen reader", () => {
    const { container } = render(<TradeOnStage sides={TRADE_T} show="tokens" />);
    // The cards of the form say the same trade to a screen reader, so the stage is art.
    expect(container.querySelector("ul")?.getAttribute("aria-hidden")).toBe("true");
    expect(container.querySelector('[title="Kenneth Walker III"]')).not.toBeNull();
  });
});
