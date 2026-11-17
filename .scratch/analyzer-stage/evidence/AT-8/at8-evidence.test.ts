/**
 * Evidence of AT-8 only: the 12 stage lines of trade T and of trade B, built from the real cpc teams route of 2026-11-17.
 * It prints each list and checks the count, the first and last line, and the banned words.
 */
import { describe, expect, it } from "vitest";
import { stageLines, type StageTrade } from "./stage-lines";

const TRADE_T: StageTrade = [
  { team: "Bo Girds", manager: "bkwon", gets: [{ name: "Tee Higgins", position: "WR" }, { name: "Bhayshul Tuten", position: "RB" }] },
  { team: "Teehee", manager: "pdurkim", gets: [{ name: "Kenneth Walker III", position: "RB" }] },
];
const TRADE_B: StageTrade = [
  { team: "The Blue Tent", manager: "tjhong0104", gets: [{ name: "Caleb Williams", position: "QB" }, { name: "Travis Kelce", position: "TE" }, { name: "Stefon Diggs", position: "WR" }, { name: "Derrick Henry", position: "RB" }, { name: "Christian McCaffrey", position: "RB" }] },
  { team: "Lil Fridge", manager: "TeamJu", gets: [{ name: "Bucky Irving", position: "RB" }, { name: "Ashton Jeanty", position: "RB" }, { name: "Jeremiyah Love", position: "RB" }] },
  { team: "All You Need Is Love", manager: "wsh5022", gets: [{ name: "Rashee Rice", position: "WR" }, { name: "Brock Bowers", position: "TE" }] },
];
const BANNED = /\b(jev|advisor|finder|front door|rival|done|finished)\b/i;

describe.each([["trade T", TRADE_T], ["trade B", TRADE_B]])("AT-8 stage lines of %s", (name, trade) => {
  const lines = stageLines(trade);
  it("prints the 12 lines and keeps the rules", () => {
    console.log(`${name}:\n${lines.map((l, i) => `  ${i + 1}. ${l}`).join("\n")}`);
    expect(lines).toHaveLength(12);
    expect(lines[0]).toBe("Weighing the sides");
    expect(lines[11]).toBe("Weighing it all together");
    for (const line of lines) expect(line).not.toMatch(BANNED);
  });
});
