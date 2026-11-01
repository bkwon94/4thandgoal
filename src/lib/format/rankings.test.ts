/**
 * Tests for the pure rankings helpers. They change the movements of the last fixture week and read the pick.
 * They need no render and no file reads.
 */
import { describe, expect, it } from "vitest";
import { rankings } from "@/components/rankings/fixture";
import { biggestMover } from "./rankings";

const lastWeek = rankings.weeks.at(-1)!;

describe("biggestMover", () => {
  /* The last fixture week with new movements, so each test sets only the case it needs. */
  function weekWith(movements: (number | null)[]) {
    const week = { week: lastWeek.week, rows: lastWeek.rows.map((row, index) => ({ ...row, movement: index < movements.length ? movements[index] : 0 })) };
    return biggestMover(week);
  }

  it("picks the largest movement, up or down", () => {
    expect(weekWith([1, -3, 2])?.rank).toBe(2);
  });

  it("picks the higher ranked team on a tie", () => {
    expect(weekWith([0, 0, -2, 2])?.rank).toBe(3);
  });

  it("returns null when every movement is null or zero", () => {
    expect(weekWith([null, 0, null])).toBeNull();
    expect(weekWith(Array(12).fill(null))).toBeNull();
  });
});
