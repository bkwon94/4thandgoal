/**
 * Tests for the stage lines: the 12 lines that one trade on the stage gives, and the rules that each list keeps.
 * Trade T is the real trade of the acceptance tests, and the second trade is the real three-side fixture.
 */
import { describe, expect, it } from "bun:test";
import { analyzeResponseThree } from "./fixtures/api";
import { stageLines, type StageTrade } from "./stage-lines";

/* Trade T: Bo Girds gives Kenneth Walker III to Teehee for Tee Higgins and Bhayshul Tuten. */
const TRADE_T: StageTrade = [
  {
    team: "Pukancun on 3",
    manager: "Bo Girds",
    gets: [
      { name: "Tee Higgins", position: "WR" },
      { name: "Bhayshul Tuten", position: "RB" },
    ],
  },
  { team: "Teehee", manager: "Teehee", gets: [{ name: "Kenneth Walker III", position: "RB" }] },
];

/* The sides of the three-side fixture. The fixture has no manager, so the test gives each side one. */
const MANAGERS = ["Ana", "Ben", "Cy"];
const TRADE_THREE: StageTrade = analyzeResponseThree.trade.sides.map((side, i) => ({
  team: side.team,
  manager: MANAGERS[i],
  gets: side.gets.map((get) => ({ name: get.name, position: get.position })),
}));

const BANNED =
  /\b(jev|advisor|finder|front door|rival|done|finished|complete|completed)\b|\d+\s*%/i;

describe.each([
  ["trade T", TRADE_T],
  ["a real trade of three sides", TRADE_THREE],
])("stageLines of %s", (_name, trade) => {
  const lines = stageLines(trade);

  it("gives 12 distinct lines", () => {
    expect(lines).toHaveLength(12);
    expect(new Set(lines).size).toBe(12);
  });

  it("fixes the first and the last line", () => {
    expect(lines[0]).toBe("Weighing the sides");
    expect(lines[11]).toBe("Weighing it all together");
  });

  it("names no internal part, no rival, and no finished step", () => {
    for (const line of lines) expect(line).not.toMatch(BANNED);
  });

  it("names a player, a team, or a manager of the trade", () => {
    const names = trade.flatMap((side) => [
      side.team,
      side.manager,
      ...side.gets.map((get) => get.name),
    ]);
    expect(lines.some((line) => names.some((name) => line.includes(name)))).toBe(true);
  });
});

describe("stageLines", () => {
  it("names the players, the teams, and the managers of trade T", () => {
    const text = stageLines(TRADE_T).join("\n");
    expect(text).toMatch(/Tee Higgins|Bhayshul Tuten|Kenneth Walker III/);
    expect(text).toMatch(/Teehee|Pukancun on 3/);
    expect(text).toMatch(/Bo Girds/);
  });

  it("still gives 12 lines when a side gets no player", () => {
    const lines = stageLines([
      { team: "A", manager: "Ana", gets: [] },
      { team: "B", manager: "Ben", gets: [{ name: "P One", position: "QB" }] },
    ]);
    expect(lines).toHaveLength(12);
    expect(new Set(lines).size).toBe(12);
  });
});
