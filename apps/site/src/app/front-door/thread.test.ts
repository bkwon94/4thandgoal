/**
 * Tests for the name of a personal Topic in the Thread: the typed question, else the Topic name, with the team after
 * it when it is not Your team. Also the request of Refresh for a trade Answer, and the request of a typed question
 * of trade ideas.
 */
import { describe, expect, it } from "bun:test";
import { type AskAnswer, askAnswerSchema } from "./ask-api";
import { ideasRequestOf, itemOfRoute, tradeRequestOf } from "./ask-thread";
import ideasStream from "./fixtures/trade-ideas-stream.json";
import { personalName } from "./thread";
import type { TradeAnswer } from "./trade-api";

describe("personalName", () => {
  it("gives a typed question as is, and a tapped Topic its name with the team after it when it is not Your team", () => {
    expect(personalName({ key: "weak_spots", question: null }, "Bo Girds")).toBe(
      "Weak spots: Bo Girds",
    );
    expect(personalName({ key: "weak_spots", question: null }, undefined)).toBe("Weak spots");
    expect(personalName({ key: "weak_spots", question: "where am I weak" }, "Bo Girds")).toBe(
      "where am I weak",
    );
  });
});

describe("tradeRequestOf", () => {
  const ideas = ideasStream.find((part) => part.type === "data-answer")?.data as TradeAnswer;

  it("sends the typed question of trade ideas again on Refresh, and no question for a tapped Topic", () => {
    expect(
      tradeRequestOf(
        { mode: "ideas", question: "trade ideas for kenneth walker", answer: ideas },
        3,
      ),
    ).toEqual({
      mode: "ideas",
      roster_id: 3,
      partner: null,
      question: "trade ideas for kenneth walker",
    });
    expect(tradeRequestOf({ mode: "ideas", question: "Trade ideas", answer: ideas }, 3)).toEqual({
      mode: "ideas",
      roster_id: 3,
      partner: null,
    });
  });
});

describe("ideasRequestOf", () => {
  const turns = [
    {
      question: "Trade ideas",
      answer: "1 offer. Offer 1: Bo Girds gives Zay Flowers. Teehee gives Jalen Hurts.",
    },
  ];

  it("sends the typed follow-up and the turns of the Thread, so the limit reads from the whole chat", () => {
    expect(ideasRequestOf({ team: null }, "id rather not trade a WR", 6, turns)).toEqual({
      mode: "ideas",
      roster_id: 6,
      partner: null,
      question: "id rather not trade a WR",
      turns,
    });
  });

  it("keeps the team that the question names as the partner, and never Your team", () => {
    expect(ideasRequestOf({ team: 2 }, "trade ideas with teehee", 6, [])).toMatchObject({
      partner: 2,
      turns: [],
    });
    expect(ideasRequestOf({ team: 6 }, "trade ideas for me", 6, [])).toMatchObject({
      partner: null,
    });
  });
});

describe("itemOfRoute with Trades closed", () => {
  const CLOSED_LINE = "The trade deadline has passed. Trades open again next season.";
  const route = (fields: Record<string, unknown>): AskAnswer =>
    askAnswerSchema.parse({ topic: null, team: null, closest: [], suggestion: null, ...fields });

  it("shows the closed line of the API as the answer, never the refusal (AT-7)", () => {
    const item = itemOfRoute(
      route({ route: "closed", line: CLOSED_LINE }),
      "Who should I trade for at RB?",
      1,
      {},
    );
    expect(item).toEqual({
      kind: "note",
      question: "Who should I trade for at RB?",
      line: CLOSED_LINE,
      topic: null,
      team: null,
      retry: false,
    });
  });

  it("leaves each trade Topic out of the closest Topics of a miss and of a cap", () => {
    const closest = ["trade_ideas", "weak_spots", "sell_high", "trade_check", "power_rankings"];
    expect(itemOfRoute(route({ route: "miss", closest }), "q", 1, {}, true)).toEqual({
      kind: "miss",
      question: "q",
      closest: ["weak_spots", "power_rankings"],
    });
    expect(itemOfRoute(route({ route: "cap", line: "Stop.", closest }), "q", 1, {}, true)).toEqual({
      kind: "cap",
      question: "q",
      line: "Stop.",
      closest: ["weak_spots", "power_rankings"],
    });
    expect(itemOfRoute(route({ route: "miss", closest }), "q", 1, {})).toEqual({
      kind: "miss",
      question: "q",
      closest,
    });
  });
});
