/**
 * Tests for the stats-through segments that the analyze page and the finder page share.
 * The cases follow the as-of block of the result document.
 */
import { describe, expect, it } from "vitest";
import type { AsOf } from "./analyze-types";
import { knownGamesSegments } from "./known-games-segments";

const base: AsOf = { chart_week: 7, stats_through: 6, rosters_fetched: "2026-10-26T09:30:00-04:00" };
const known = (over: Partial<NonNullable<AsOf["known_games"]>>): AsOf => ({
  ...base,
  stats_through: 7,
  completed_through: 6,
  known_games: { week: 7, games: 13, in_progress: 0, pending: {}, ...over },
});

describe("knownGamesSegments", () => {
  it("shows the stats week alone when the document has no block", () => {
    expect(knownGamesSegments(base)).toEqual(["Stats through week 6"]);
  });

  it("shows the stats week alone when the block is null", () => {
    expect(knownGamesSegments({ ...base, known_games: null })).toEqual(["Stats through week 6"]);
  });

  it("shows the stats week alone when no games are read", () => {
    expect(knownGamesSegments({ ...known({ games: 0 }), stats_through: 6 })).toEqual(["Stats through week 6"]);
  });

  it("stops after the games count when nothing is in progress or pending", () => {
    expect(knownGamesSegments(known({}))).toEqual(["Stats through week 6, plus 13 week 7 games"]);
  });

  it("falls back to the week before the stats week when completed_through is absent", () => {
    const { completed_through: _c, ...asOf } = known({});
    expect(knownGamesSegments(asOf)).toEqual(["Stats through week 6, plus 13 week 7 games"]);
  });

  it("uses the singular for one game", () => {
    expect(knownGamesSegments(known({ games: 1 }))).toEqual(["Stats through week 6, plus 1 week 7 game"]);
  });

  it("adds the in-progress count", () => {
    expect(knownGamesSegments(known({ in_progress: 2 }))).toEqual(["Stats through week 6, plus 13 week 7 games, 2 in progress"]);
  });

  it("adds one segment per pending name", () => {
    const line = knownGamesSegments(known({ in_progress: 2, pending: { snaps: 9, usage: 1 } }));
    expect(line).toEqual([
      "Stats through week 6, plus 13 week 7 games, 2 in progress",
      "Snaps pending for 9 games",
      "Usage pending for 1 game",
    ]);
  });
});
