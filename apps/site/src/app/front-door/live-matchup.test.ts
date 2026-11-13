/**
 * Tests for the live card of Your next matchup: the read of the API stream that the API test recorded over the live
 * Sleeper week 10 of cpc, and the line of its read time.
 */
import { describe, expect, it } from "vitest";
import stream from "./fixtures/next-matchup-stream.json";
import { liveMatchupOf, readTimeLine } from "./live-matchup";

/* The stream as the API sends it: one `data:` line per part, then [DONE]. */
const sse = [...stream.map((part) => `data: ${JSON.stringify(part)}`), "data: [DONE]"].join("\n\n");

describe("the live card of Your next matchup", () => {
  it("reads the matchup card of the stream with its projected totals, its odds, and its read time", () => {
    const card = liveMatchupOf(sse);
    expect(card).not.toBeNull();
    expect(card?.final).toBe(false);
    expect(card?.you.name).toBe("Bo Girds");
    expect(card?.you.score).toBeGreaterThan(card?.them.score ?? Infinity);
    expect(card?.odds).toBeGreaterThan(0.5);
    expect(card?.read_at).toBe("2026-11-12T07:53:00-05:00");
  });

  it("reads no card from a stream with no block, so the card of the weekly build stays", () => {
    expect(liveMatchupOf('data: {"type":"start"}\n\ndata: {"type":"finish","finishReason":"stop"}\n\ndata: [DONE]')).toBeNull();
  });

  it("says when the live projections were read, in the time zone of the browser", () => {
    expect(readTimeLine("2026-11-12T07:53:00-05:00", "America/New_York")).toBe("Live projections as of 7:53 AM");
  });
});
