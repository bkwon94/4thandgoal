/**
 * Tests for the Topics of the front door: the order of the day, the Suggestions, and the Topics that a client with
 * Trades closed leaves out. The time is a parameter of each function, so no test waits for a date.
 */
import { describe, expect, it } from "bun:test";
import { TOPICS, dayOrder, openTopics, pickSuggestions } from "./topics";

const TRADE = ["sell_high", "trade_ideas", "trade_check"];

describe("a client with Trades closed", () => {
  it("lists no trade Topic in More, and keeps leaders_trades (AT-6, AT-12)", () => {
    const keys = openTopics(true).map((topic) => topic.key);
    for (const key of TRADE) expect(keys).not.toContain(key);
    expect(keys).toContain("leaders_trades");
    expect(keys.length).toBe(TOPICS.length - TRADE.length);
  });

  it("lists every Topic in More while trades are open", () => {
    expect(openTopics(false)).toEqual([...TOPICS]);
  });

  it("leaves each trade Topic out of the order of every day", () => {
    for (let day = 0; day < 7; day += 1) {
      const order = dayOrder(day, true);
      for (const key of TRADE) expect(order).not.toContain(key);
      expect(order).toContain("leaders_trades");
    }
  });

  it("keeps the trade Topics in the order of Thursday while trades are open", () => {
    expect(dayOrder(4).slice(0, 4)).toEqual([
      "start_sit",
      "next_matchup",
      "trade_ideas",
      "sell_high",
    ]);
  });

  it("picks no trade Topic as a Suggestion, also with a fact and as urgent", () => {
    const facts = Object.fromEntries(TOPICS.map((topic) => [topic.key, "a fact"]));
    const picks = pickSuggestions(4, facts, {}, ["sell_high"], true);
    expect(picks.length).toBe(3);
    for (const key of TRADE) expect(picks).not.toContain(key);
    expect(pickSuggestions(4, facts, {}, ["sell_high"])[0]).toBe("sell_high");
  });
});
