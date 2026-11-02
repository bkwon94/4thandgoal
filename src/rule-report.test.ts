/**
 * Holds the report of a rule test to the house shape of ADR 0006, byte for byte.
 * Every rule test prints its offenses through this helper.
 */
import { describe, expect, it } from "vitest";
import { type Offense, report } from "./rule-report";

const OFFENSE: Offense = {
  path: "src/components/week/standings.tsx",
  line: 4,
  ruleId: "components/no-loader",
  what: "standings.tsx imports @/lib/data/week-data.",
  rule: "a component takes data and returns markup",
  adr: "docs/adr/0004-a-component-takes-data-and-returns-markup.md",
  fix: "call the loader in src/app/ and pass the value to the component as a prop.",
};

const SHAPE = `src/components/week/standings.tsx:4  components/no-loader
  standings.tsx imports @/lib/data/week-data.
  Rule: a component takes data and returns markup (docs/adr/0004-a-component-takes-data-and-returns-markup.md).
  Fix: call the loader in src/app/ and pass the value to the component as a prop.`;

describe("report", () => {
  it("prints one offense in the house shape", () => {
    expect(report([OFFENSE])).toBe(`1 offense.\n\n${SHAPE}`);
  });

  it("starts with the count and puts a blank line between two offenses", () => {
    expect(report([OFFENSE, OFFENSE])).toBe(`2 offenses.\n\n${SHAPE}\n\n${SHAPE}`);
  });
});
