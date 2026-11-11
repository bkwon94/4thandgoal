/**
 * Tests for the name of a personal Topic in the Thread: the typed question, else the Topic name, with the team after
 * it when it is not Your team. Also the request of Refresh for a trade Answer.
 */
import { describe, expect, it } from "vitest";
import { tradeRequestOf } from "./ask-thread";
import ideasStream from "./fixtures/trade-ideas-stream.json";
import { personalName } from "./thread";
import type { TradeAnswer } from "./trade-api";

describe("personalName", () => {
  it("gives a typed question as is, and a tapped Topic its name with the team after it when it is not Your team", () => {
    expect(personalName({ key: "weak_spots", question: null }, "Bo Girds")).toBe("Weak spots: Bo Girds");
    expect(personalName({ key: "weak_spots", question: null }, undefined)).toBe("Weak spots");
    expect(personalName({ key: "weak_spots", question: "where am I weak" }, "Bo Girds")).toBe("where am I weak");
  });
});

describe("tradeRequestOf", () => {
  const ideas = ideasStream.find((part) => part.type === "data-answer")?.data as TradeAnswer;

  it("sends the typed question of trade ideas again on Refresh, and no question for a tapped Topic", () => {
    expect(tradeRequestOf({ mode: "ideas", question: "trade ideas for kenneth walker", answer: ideas }, 3)).toEqual({ mode: "ideas", roster_id: 3, partner: null, question: "trade ideas for kenneth walker" });
    expect(tradeRequestOf({ mode: "ideas", question: "Trade ideas", answer: ideas }, 3)).toEqual({ mode: "ideas", roster_id: 3, partner: null });
  });
});
