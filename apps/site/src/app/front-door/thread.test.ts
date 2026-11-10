/**
 * Tests for the line of the fold of each item of the Thread that is not a league Topic: its question and one fact from
 * its own data. An item in flight has no line, so it never folds.
 */
import { describe, expect, it } from "vitest";
import checkStream from "./fixtures/trade-check-stream.json";
import ideasStream from "./fixtures/trade-ideas-stream.json";
import sellStream from "./fixtures/sell-high-stream.json";
import type { ThreadItem } from "./ask-thread";
import type { TradeAnswer } from "./trade-api";
import { foldLine, personalName } from "./thread";

const BO_GIRDS = 6;
const teamName = (team: number) => (team === BO_GIRDS ? "Bo Girds" : undefined);
/* The whole Answer of a recorded trade stream. */
const answerOf = (stream: { type: string; data?: unknown }[]) => stream.find((part) => part.type === "data-answer")!.data as TradeAnswer;
const block = { topic: "weak_spots" as const, team: 3, fact: "RB is your weakest spot", stats: [], rows: [] };

describe("foldLine", () => {
  it("gives no line to an item in flight", () => {
    const inFlight: Exclude<ThreadItem, { kind: "topic" }>[] = [
      { kind: "pending", question: "q" },
      { kind: "passphrase", question: "q", wrong: false },
      { kind: "trade", mode: "check", question: "q", steps: ["Read both rosters"], answer: null },
      { kind: "free", question: "q", result: null },
      { kind: "personal", key: "weak_spots", team: 3, question: null, result: null },
    ];
    for (const item of inFlight) expect(foldLine(item, teamName)).toBeNull();
  });

  it("gives a trade check its Lean", () => {
    const line = foldLine({ kind: "trade", mode: "check", question: "is it fair", steps: [], answer: answerOf(checkStream) }, teamName);
    expect(line).toEqual({ name: "is it fair", fact: "Send it" });
  });

  it("gives trade ideas the count of offers, and sell high the players to sell", () => {
    const ideas = answerOf(ideasStream);
    const count = ideas.kind === "ideas" ? ideas.document.trades.length : 0;
    expect(foldLine({ kind: "trade", mode: "ideas", question: "Trade ideas", steps: [], answer: ideas }, teamName)?.fact).toBe(count === 1 ? "1 offer" : `${count} offers`);
    const sell = answerOf(sellStream);
    const names = sell.kind === "sell" ? sell.document.picks.map((pick) => pick.player.name) : [];
    expect(foldLine({ kind: "trade", mode: "sell", question: "Sell high", steps: [], answer: sell }, teamName)?.fact).toBe(`Sell ${names.join(", ")}`);
  });

  it("gives a free answer the first sentence of its text", () => {
    const result = { steps: [], text: "Bo Girds scored 140.2. That led the week.", suggestion: null };
    expect(foldLine({ kind: "free", question: "who led", result }, teamName)?.fact).toBe("Bo Girds scored 140.2.");
  });

  it("gives a personal Answer the fact of its data block, with the team after a tapped Topic of another team", () => {
    const result = { block, text: "Text.", key: "k" };
    expect(foldLine({ kind: "personal", key: "weak_spots", team: BO_GIRDS, question: null, result }, teamName)).toEqual({
      name: "Weak spots: Bo Girds",
      fact: "RB is your weakest spot",
    });
    expect(personalName({ key: "weak_spots", question: null }, undefined)).toBe("Weak spots");
    expect(personalName({ key: "weak_spots", question: "where am I weak" }, "Bo Girds")).toBe("where am I weak");
  });

  it("gives a miss its closest Topic, and a cap line or a note its line", () => {
    expect(foldLine({ kind: "miss", question: "a poem", closest: ["week_recap"] }, teamName)?.fact).toBe("No answer · try Week recap");
    expect(foldLine({ kind: "cap", question: "q", line: "Free answers rest until Tuesday.", closest: [] }, teamName)?.fact).toBe("Free answers rest until Tuesday.");
    expect(foldLine({ kind: "note", question: "q", line: "Ask again.", topic: null, team: null, retry: true }, teamName)?.fact).toBe("Ask again.");
  });
});
