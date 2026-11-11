/**
 * Tests for the prefill of the trade form: the query of a link of the front door, and the sides it fills.
 * A link names Your team, the partner, and only the players that the front door is sure of.
 */
import { describe, expect, it } from "vitest";
import { prefillQuery, prefillSides, readPrefill } from "./prefill";

describe("the prefill of the Trade page", () => {
  it("reads back the query that it writes", () => {
    const prefill = { team: 3, partner: 6, gives: ["5045"], gets: ["8151"] };
    expect(prefillQuery(prefill)).toBe("?team=3&with=6&give=5045&get=8151");
    expect(readPrefill(prefillQuery(prefill))).toEqual(prefill);
  });

  it("writes only Your team when the link names no partner and no player", () => {
    expect(prefillQuery({ team: 3, partner: null, gives: [], gets: [] })).toBe("?team=3");
  });

  it("reads no prefill from a query with no team or a bad team", () => {
    expect(readPrefill("")).toBeNull();
    expect(readPrefill("?team=abc")).toBeNull();
    expect(readPrefill("?with=6")).toBeNull();
  });

  it("drops a partner that is Your team", () => {
    expect(readPrefill("?team=3&with=3")?.partner).toBeNull();
  });

  it("gives Your team each player of the partner, and the partner each player that Your team gives", () => {
    expect(prefillSides({ team: 3, partner: 6, gives: ["5045"], gets: ["8151"] })).toEqual([
      { id: 0, rosterId: 3, gets: [{ playerId: "8151", fromSide: 1 }] },
      { id: 1, rosterId: 6, gets: [{ playerId: "5045", fromSide: 0 }] },
    ]);
  });
});
