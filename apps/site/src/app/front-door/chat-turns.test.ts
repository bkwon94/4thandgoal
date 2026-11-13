/**
 * Tests for the turns of the Thread that each typed question carries: the question and the shown answer text of each
 * earlier item, oldest first, with the oldest cut first past the limit and no item in flight.
 */
import { describe, expect, it } from "vitest";
import type { DoorAnswer } from "@/lib/data/front-door-data";
import type { ThreadItem } from "./ask-thread";
import { TURNS_MAX_CHARS, TURN_ANSWER_MAX, TURN_QUESTION_MAX, threadTurns, turnsBefore } from "./chat-turns";

const LIL_FRIDGE = 3;
const BO_GIRDS = 6;
const teamName = (team: number) => (team === BO_GIRDS ? "Bo Girds" : undefined);
const block = { kind: "rows" as const, topic: "weak_spots" as const, team: LIL_FRIDGE, fact: "RB is your weakest spot", stats: [], rows: [] };
const recap: DoorAnswer = { topic: "week_recap", fact: "Bo Girds scored 150", stats: [], rows: [], text: ["Bo Girds won.", "The median was 110."], href: null };
const answers: Record<number, DoorAnswer[]> = { [LIL_FRIDGE]: [recap] };

const free = (question: string, text: string): ThreadItem => ({ kind: "free", question, result: { steps: ["Reading the standings"], text, suggestion: null } });

describe("threadTurns", () => {
  it("sends the question and the shown answer of each earlier turn, oldest first and newest last", () => {
    const items: ThreadItem[] = [
      free("who has the best roster", "Bo Girds has the best roster."),
      free("who is second", "Lil Fridge is second."),
    ];
    expect(threadTurns(items, answers, teamName)).toEqual([
      { question: "who has the best roster", answer: "Bo Girds has the best roster." },
      { question: "who is second", answer: "Lil Fridge is second." },
    ]);
  });

  it("sends the plain text only, with no data block, step line, or key", () => {
    const items: ThreadItem[] = [
      { kind: "personal", key: "weak_spots", team: LIL_FRIDGE, question: "where am i weak", result: { block, text: "RB is your weakest spot.", key: "k1" } },
      { kind: "topic", key: "week_recap", team: LIL_FRIDGE, question: null },
    ];
    const turns = threadTurns(items, answers, teamName);
    expect(turns).toEqual([
      { question: "where am i weak", answer: "RB is your weakest spot." },
      { question: "Week recap", answer: "Bo Girds won. The median was 110." },
    ]);
    for (const turn of turns) expect(Object.keys(turn).sort()).toEqual(["answer", "question"]);
  });

  it("names a tapped personal Topic by its name as the question", () => {
    const items: ThreadItem[] = [{ kind: "personal", key: "stack_up", team: BO_GIRDS, question: null, result: { block, text: "Bo Girds ranks first.", key: "k2" } }];
    const [turn] = threadTurns(items, answers, teamName);
    expect(turn.question).toContain("Bo Girds");
    expect(turn.answer).toBe("Bo Girds ranks first.");
  });

  it("leaves out each item in flight", () => {
    const items: ThreadItem[] = [
      { kind: "pending", question: "q" },
      { kind: "passphrase", question: "q", wrong: false },
      { kind: "free", question: "q", result: null },
      { kind: "personal", key: "weak_spots", team: LIL_FRIDGE, question: "q", result: null },
      { kind: "trade", mode: "check", question: "q", steps: ["Read both rosters"], answer: null },
    ];
    expect(threadTurns(items, answers, teamName)).toEqual([]);
  });

  it("keeps a miss and a note as a turn with their line", () => {
    const items: ThreadItem[] = [
      { kind: "miss", question: "who won last year", closest: ["playoff_race"] },
      { kind: "note", question: "a poem", line: "Not a question here.", topic: null, team: null, retry: false },
    ];
    const turns = threadTurns(items, answers, teamName);
    expect(turns.map((turn) => turn.question)).toEqual(["who won last year", "a poem"]);
    expect(turns[1].answer).toBe("Not a question here.");
    expect(turns[0].answer.length).toBeGreaterThan(0);
  });

  it("cuts each turn to the caps of the API", () => {
    const items: ThreadItem[] = [free("q".repeat(TURN_QUESTION_MAX + 50), "a".repeat(TURN_ANSWER_MAX + 50))];
    const [turn] = threadTurns(items, answers, teamName);
    expect(turn.question.length).toBe(TURN_QUESTION_MAX);
    expect(turn.answer.length).toBe(TURN_ANSWER_MAX);
  });

  it("drops the oldest turns first past the limit and keeps the newest last", () => {
    const items: ThreadItem[] = Array.from({ length: 40 }, (_, i) => free(`question ${i}`, "x".repeat(TURN_ANSWER_MAX)));
    const turns = threadTurns(items, answers, teamName);
    const size = turns.reduce((sum, turn) => sum + turn.question.length + turn.answer.length, 0);
    expect(size).toBeLessThanOrEqual(TURNS_MAX_CHARS);
    expect(turns.length).toBeLessThan(40);
    expect(turns.at(-1)?.question).toBe("question 39");
    expect(turns.map((turn) => turn.question)).toEqual(Array.from({ length: turns.length }, (_, i) => `question ${40 - turns.length + i}`));
  });
});

const player = (name: string) => ({ player_id: name, name, position: "WR", nfl_team: "SEA", headshot: "" });
const side = (roster_id: number, team: string, gives: string[], gets: string[]) => ({ roster_id, team, gives: gives.map(player), gets: gets.map(player) });
const offer = (n: number) => ({ offer_id: `o${n}`, sides: [side(1, "Bo Girds", [`Give ${n}`], [`Get ${n}`]), side(2, "Lil Fridge", [`Get ${n}`], [`Give ${n}`])], headline: null, bullets: [], fact_lines: [] });

describe("threadTurns of a trade Answer", () => {
  const tradeItem = (mode: "check" | "ideas", answer: unknown): ThreadItem =>
    ({ kind: "trade", mode, question: "q", steps: [], answer }) as ThreadItem;

  it("names the players of each side of a trade check, after the lean", () => {
    const document = { lean: "Lean yes", trade: { asker: 1, sides: [side(1, "Bo Girds", ["Ann", "Bob"], ["Cy"]), side(2, "Lil Fridge", ["Cy"], ["Ann", "Bob"])] } };
    const [turn] = threadTurns([tradeItem("check", { kind: "check", document })], answers, teamName);
    expect(turn.answer).toBe("Lean yes. Bo Girds gives Ann, Bob. Lil Fridge gives Cy.");
  });

  it("names the sides of the top 3 offers of a trade ideas list at most", () => {
    const document = { trades: [1, 2, 3, 4].map(offer), near: [] };
    const [turn] = threadTurns([tradeItem("ideas", { kind: "ideas", document })], answers, teamName);
    expect(turn.answer).toContain("4 offers");
    for (const n of [1, 2, 3]) expect(turn.answer).toContain(`Bo Girds gives Give ${n}`);
    expect(turn.answer).not.toContain("Give 4");
  });

  it("names the near ideas and the reason of each, so a follow-up can point at one (H21)", () => {
    const near = [1, 2].map((n) => ({ offer_id: `n${n}`, sides: offer(n).sides, reason: `Reason ${n}.` }));
    const document = { trades: [], near, empty: "No offer helps enough." };
    const [turn] = threadTurns([tradeItem("ideas", { kind: "ideas", document })], answers, teamName);
    expect(turn.answer).toBe(
      "No clear offer. No offer helps enough. Idea 1: Bo Girds gives Give 1. Lil Fridge gives Get 1. Why not: Reason 1. " +
        "Idea 2: Bo Girds gives Give 2. Lil Fridge gives Get 2. Why not: Reason 2.",
    );
  });

  it("names the near ideas after the offers", () => {
    const document = { trades: [offer(1)], near: [{ offer_id: "n2", sides: offer(2).sides, reason: "Reason 2." }], empty: null };
    const [turn] = threadTurns([tradeItem("ideas", { kind: "ideas", document })], answers, teamName);
    expect(turn.answer).toBe("1 offer. Offer 1: Bo Girds gives Give 1. Lil Fridge gives Get 1. Idea 2: Bo Girds gives Give 2. Lil Fridge gives Get 2. Why not: Reason 2.");
  });
});

describe("turnsBefore", () => {
  const entries = [
    { ...free("first", "One."), id: 1 },
    { ...free("second", "Two."), id: 2 },
    { kind: "pending" as const, question: "third", id: 3 },
  ];

  it("sends only the turns before the item of the question", () => {
    expect(turnsBefore(entries, 2, answers, teamName)).toEqual([{ question: "first", answer: "One." }]);
  });

  it("sends every turn for a new question with no place yet", () => {
    expect(turnsBefore(entries, 99, answers, teamName).map((turn) => turn.question)).toEqual(["first", "second"]);
  });
});

describe("the block of a free answer as a turn (H27)", () => {
  it("carries a list, a table, and a player card as short text after the lead, so a follow-up has context", () => {
    const withBlock = (question: string, shown: NonNullable<Extract<ThreadItem, { kind: "free" }>["result"]>["block"]): ThreadItem => ({
      kind: "free",
      question,
      result: { steps: [], text: "Here they are.", suggestion: null, block: shown },
    });
    const items: ThreadItem[] = [
      withBlock("order my players", { kind: "list", title: "Season points", rows: [{ rank: 1, name: "Kenneth Walker III", tag: "RB", value: "183.4" }, { rank: 2, name: "Lamar Jackson", tag: "QB", value: "80.08", note: "On IR" }] }),
      withBlock("compare", { kind: "table", title: "Bo Girds vs Teehee", columns: ["Stat", "Bo Girds", "Teehee"], rows: [["Record", "11-7", "8-10"]] }),
      withBlock("lamar", { kind: "player", name: "Lamar Jackson", position: "QB", nfl_team: "BAL", fantasy_team: "Bo Girds", can_play_now: false, status: "on IR", stats: [{ label: "Season points", value: "80.08" }], note: "Out since week 4." }),
    ];
    expect(threadTurns(items, answers, teamName).map((turn) => turn.answer)).toEqual([
      "Here they are. Season points: 1. Kenneth Walker III, RB, 183.4; 2. Lamar Jackson, QB, 80.08 (On IR).",
      "Here they are. Bo Girds vs Teehee: Stat | Bo Girds | Teehee; Record | 11-7 | 8-10.",
      "Here they are. Lamar Jackson, QB, BAL, Bo Girds, can't play now (on IR). Season points 80.08. Out since week 4.",
    ]);
  });
});

