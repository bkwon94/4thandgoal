/**
 * Tests for the read of a finder card: the analyze document that the analyzer shows when a card opens, with no second grade.
 * The input is the shared finder fixture, the document that the find route sends.
 */
import { describe, expect, it } from "vitest";
import { findResponse } from "./fixtures/api";
import { analyzeResponseSchema } from "./schemas/api";
import { finderRead } from "./finder-read";

describe("finderRead", () => {
  const [trade] = findResponse.trades;

  it("gives an analyze document with the Lean and the Case of the card, for the asker of the find", () => {
    const read = finderRead(trade, findResponse)!;
    expect(analyzeResponseSchema.safeParse(read).success).toBe(true);
    expect(read.lean).toBe("Lean yes");
    expect(read.case).toBe("If Roschon Johnson keeps his role, you get a steady starter and the other manager gets the receiver he needs.");
    expect(read.trade).toEqual({ asker: 2, sides: trade.sides });
  });

  it("puts the Bullets of the card on the side of the asker, because each Bullet speaks to the asker", () => {
    const read = finderRead(trade, findResponse)!;
    // The partner side has no Bullet, but it stays, so the trade on the stage shows both teams.
    expect(read.sides).toEqual([
      { roster_id: 2, bullets: trade.bullets, week_lines: [] },
      { roster_id: 10, bullets: [], week_lines: [] },
    ]);
  });

  it("keeps the as-of stamps of the find, so the read names the same data", () => {
    const read = finderRead(trade, findResponse)!;
    expect(read.as_of).toEqual(findResponse.as_of);
    expect(read.missing).toEqual(findResponse.missing);
    expect(read.stale).toEqual(findResponse.stale);
  });

  it("gives no read for a trade of a fallback, which has no Lean", () => {
    expect(finderRead({ ...trade, lean: null, case: null, bullets: [] }, findResponse)).toBeNull();
  });
});
