/**
 * Tests for the state of Deadline week and the countdown text, from the time and the Lock.
 * Each test reads one fixed time at an edge: more than a day, the last 3 hours, the Lock, and one day after it.
 */
import { describe, expect, it } from "vitest";
import { deadlineState } from "./deadline";

/* The Lock of client cpc: 00:00 Eastern on Tue 2026-11-24. */
const LOCK = Date.parse("2026-11-24T05:00:00Z");
const HOUR = 3600 * 1000;

describe("deadlineState", () => {
  it("gives open with days, hours, and minutes more than 3 h before the Lock", () => {
    // 09:55:00 Eastern on Sat 2026-11-21.
    expect(deadlineState(Date.parse("2026-11-21T14:55:00Z"), LOCK)).toEqual({ state: "open", countdown: "~2d 14h 05m" });
  });

  it("drops the days under one day and pads the minutes", () => {
    expect(deadlineState(LOCK - (5 * HOUR + 7 * 60 * 1000), LOCK)).toEqual({ state: "open", countdown: "~5h 07m" });
  });

  it("gives last-hours with seconds at 3 h before the Lock and under", () => {
    expect(deadlineState(LOCK - 3 * HOUR, LOCK)).toEqual({ state: "last-hours", countdown: "~3h 00m 00s" });
    expect(deadlineState(LOCK - (2 * HOUR + 41 * 60 * 1000 + 10 * 1000), LOCK)).toEqual({ state: "last-hours", countdown: "~2h 41m 10s" });
  });

  it("gives closed at the Lock and until one day after it", () => {
    expect(deadlineState(LOCK, LOCK)).toEqual({ state: "closed", countdown: null });
    expect(deadlineState(LOCK + 24 * HOUR - 1, LOCK)).toEqual({ state: "closed", countdown: null });
  });

  it("gives ended one day after the Lock", () => {
    expect(deadlineState(LOCK + 24 * HOUR, LOCK)).toEqual({ state: "ended", countdown: null });
  });
});
