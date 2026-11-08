/**
 * Tests for the trade of the Stack: the body of POST /analyze that a set of picks builds, the gate of the grade, and the halo level.
 * The bodies on the right are the bodies that the form on main sends for the same trade, from its own tests.
 */
import { describe, expect, it } from "vitest";
import { analyzeRequest, everySideTrades, haloLevel, type Sides } from "./trade";

describe("analyzeRequest", () => {
  it("builds the body of main for a trade of two teams", () => {
    // Your Team (4) gets p4 from Team Two (12), and Team Two gets p1 from Your Team.
    const sides: Sides = [
      { id: 0, rosterId: 4, gets: [{ playerId: "p4", fromSide: 1 }] },
      { id: 1, rosterId: 12, gets: [{ playerId: "p1", fromSide: 0 }] },
    ];
    // main: "posts the asker first, with the destination of each player".
    expect(analyzeRequest(sides, 2026)).toEqual({
      season: 2026,
      asker: 4,
      sides: [
        { roster_id: 4, gives: [{ player_id: "p1", to: 12 }] },
        { roster_id: 12, gives: [{ player_id: "p4", to: 4 }] },
      ],
    });
  });

  it("builds the body of main for a trade of three teams", () => {
    // Your Team gives p1 to Team Two and p2 to Team Three. Team Two gives p4 to Team Three. Team Three gives p5 to Your Team.
    const sides: Sides = [
      { id: 0, rosterId: 4, gets: [{ playerId: "p5", fromSide: 2 }] },
      { id: 1, rosterId: 12, gets: [{ playerId: "p1", fromSide: 0 }] },
      {
        id: 2,
        rosterId: 7,
        gets: [
          { playerId: "p2", fromSide: 0 },
          { playerId: "p4", fromSide: 1 },
        ],
      },
    ];
    // main: "posts every side in order with the destination of each player".
    expect(analyzeRequest(sides, 2026)).toEqual({
      season: 2026,
      asker: 4,
      sides: [
        { roster_id: 4, gives: [{ player_id: "p1", to: 12 }, { player_id: "p2", to: 7 }] },
        { roster_id: 12, gives: [{ player_id: "p4", to: 7 }] },
        { roster_id: 7, gives: [{ player_id: "p5", to: 4 }] },
      ],
    });
  });

  it("returns null until each side has a team", () => {
    const sides: Sides = [
      { id: 0, rosterId: 4, gets: [] },
      { id: 1, rosterId: null, gets: [] },
    ];
    expect(analyzeRequest(sides, 2026)).toBeNull();
  });
});

describe("everySideTrades", () => {
  it("holds only when each side gives and gets a player", () => {
    const gets: Sides = [
      { id: 0, rosterId: 4, gets: [{ playerId: "p4", fromSide: 1 }] },
      { id: 1, rosterId: 12, gets: [] },
    ];
    expect(everySideTrades(gets)).toBe(false);
    expect(everySideTrades([gets[0], { ...gets[1], gets: [{ playerId: "p1", fromSide: 0 }] }])).toBe(true);
  });
});

describe("haloLevel", () => {
  it("is 0 of 6 for two sides with no team", () => {
    const sides: Sides = [
      { id: 0, rosterId: null, gets: [] },
      { id: 1, rosterId: null, gets: [] },
    ];
    expect(haloLevel(sides)).toBe(0);
  });

  it("is 2 of 6 for two teams and no player, below full", () => {
    const sides: Sides = [
      { id: 0, rosterId: 4, gets: [] },
      { id: 1, rosterId: 12, gets: [] },
    ];
    expect(haloLevel(sides)).toBeCloseTo(2 / 6);
    expect(everySideTrades(sides)).toBe(false);
  });

  it("is 4 of 6 when one player moves, because one side gets and the other gives", () => {
    const sides: Sides = [
      { id: 0, rosterId: 4, gets: [{ playerId: "p4", fromSide: 1 }] },
      { id: 1, rosterId: 12, gets: [] },
    ];
    expect(haloLevel(sides)).toBeCloseTo(4 / 6);
  });

  it("is full at 6 of 6, and only when the ready rule passes", () => {
    const sides: Sides = [
      { id: 0, rosterId: 4, gets: [{ playerId: "p4", fromSide: 1 }] },
      { id: 1, rosterId: 12, gets: [{ playerId: "p1", fromSide: 0 }] },
    ];
    expect(everySideTrades(sides)).toBe(true);
    expect(haloLevel(sides)).toBe(1);
  });

  it("counts three checks for each side of a trade of three teams", () => {
    // Team Three has a team and gets a player but gives none: 8 of 9, so the halo stays below full.
    const sides: Sides = [
      { id: 0, rosterId: 4, gets: [{ playerId: "p4", fromSide: 1 }] },
      { id: 1, rosterId: 12, gets: [{ playerId: "p1", fromSide: 0 }] },
      { id: 2, rosterId: 7, gets: [{ playerId: "p2", fromSide: 0 }] },
    ];
    expect(everySideTrades(sides)).toBe(false);
    expect(haloLevel(sides)).toBeCloseTo(8 / 9);
  });
});
