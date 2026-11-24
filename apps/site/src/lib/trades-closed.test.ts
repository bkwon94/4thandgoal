/**
 * Tests of Trades closed: closed at the Lock and after it, open before it, and never closed with no Lock.
 */
import { describe, expect, it } from "bun:test";
import { tradesClosed } from "./trades-closed";

const LOCK = Date.parse("2026-11-24T00:00:00-05:00");

describe("tradesClosed", () => {
  it("is never closed for a client with no Lock (AT-23)", () => {
    expect(tradesClosed(null, Date.parse("2026-11-24T12:00:00-05:00"))).toBe(false);
    expect(tradesClosed(null, Date.parse("2027-06-01T12:00:00-04:00"))).toBe(false);
  });

  it("is open 1 s before the Lock and closed at the Lock", () => {
    expect(tradesClosed(LOCK, LOCK - 1000)).toBe(false);
    expect(tradesClosed(LOCK, LOCK)).toBe(true);
    expect(tradesClosed(LOCK, LOCK + 1000)).toBe(true);
  });
});
