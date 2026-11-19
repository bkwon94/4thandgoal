/**
 * Tests of the Deadline week clock: the phase and the countdown text from the time and the Lock.
 * The Lock is the real Lock of CPC, 00:00 Eastern on Tue 2026-11-24. Each expected text comes from the spec.
 */
import { describe, expect, it } from "vitest";
import { deadlineOf } from "./deadline";

const LOCK = Date.parse("2026-11-24T00:00:00-05:00");
const at = (iso: string) => Date.parse(iso);
const HOUR = 3600 * 1000;
const DAY = 24 * HOUR;

describe("deadlineOf", () => {
  it("counts days, hours, and minutes with a tilde while the trade deadline is open (AT-1)", () => {
    expect(deadlineOf(at("2026-11-21T09:55:00-05:00"), LOCK)).toEqual({ phase: "open", countdown: "~2d 14h 05m" });
  });

  it("drops one minute when the clock moves on 60 s (AT-2)", () => {
    expect(deadlineOf(at("2026-11-21T09:56:00-05:00"), LOCK).countdown).toBe("~2d 14h 04m");
    // A part of a minute left counts as a whole minute, so the text changes on the minute, as a countdown does.
    expect(deadlineOf(at("2026-11-21T09:55:01-05:00"), LOCK).countdown).toBe("~2d 14h 05m");
    expect(deadlineOf(at("2026-11-21T09:55:59.999-05:00"), LOCK).countdown).toBe("~2d 14h 05m");
  });

  it("leaves out the days with less than one day left", () => {
    expect(deadlineOf(LOCK - (14 * HOUR + 5 * 60 * 1000), LOCK)).toEqual({ phase: "open", countdown: "~14h 05m" });
  });

  it("stays open at exactly 3 h to the Lock, and turns to the last hours with seconds under 3 h", () => {
    expect(deadlineOf(LOCK - 3 * HOUR, LOCK)).toEqual({ phase: "open", countdown: "~3h 00m" });
    expect(deadlineOf(LOCK - 3 * HOUR + 1000, LOCK)).toEqual({ phase: "last-hours", countdown: "~2h 59m 59s" });
  });

  it("shows hours, minutes, and seconds in the last hours (AT-3, AT-50)", () => {
    expect(deadlineOf(at("2026-11-23T21:18:50-05:00"), LOCK)).toEqual({ phase: "last-hours", countdown: "~2h 41m 10s" });
    expect(deadlineOf(LOCK - HOUR, LOCK)).toEqual({ phase: "last-hours", countdown: "~1h 00m 00s" });
    expect(deadlineOf(LOCK - 41_000, LOCK).countdown).toBe("~41s");
    expect(deadlineOf(LOCK - (5 * 60 + 9) * 1000, LOCK).countdown).toBe("~5m 09s");
    // A part of a second left counts as a whole second.
    expect(deadlineOf(at("2026-11-23T21:18:50.400-05:00"), LOCK).countdown).toBe("~2h 41m 10s");
  });

  it("closes at the Lock, with no countdown (AT-9)", () => {
    expect(deadlineOf(LOCK, LOCK)).toEqual({ phase: "closed", countdown: null });
    expect(deadlineOf(at("2026-11-24T00:00:01-05:00"), LOCK)).toEqual({ phase: "closed", countdown: null });
  });

  it("stays closed until one day after the Lock, then ends (AT-10)", () => {
    expect(deadlineOf(LOCK + DAY - 1000, LOCK).phase).toBe("closed");
    expect(deadlineOf(LOCK + DAY, LOCK)).toEqual({ phase: "ended", countdown: null });
    expect(deadlineOf(at("2026-11-25T00:00:01-05:00"), LOCK).phase).toBe("ended");
  });
});
