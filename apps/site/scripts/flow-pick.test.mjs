/**
 * Tests of the flow pick of the verify skill on the real flow list: the globs of a diff pick the flows.
 * A diff of one app folder picks its flow, a diff of the pipeline picks none, and a shared part picks each flow.
 */
import { describe, expect, it } from "bun:test";
import { describePick, FLOW_LIST, pickFlows, readFlowGlobs } from "./flow-pick.mjs";

const flows = readFlowGlobs(FLOW_LIST);
const ALL = [
  "Front door",
  "Passphrase",
  "Week report",
  "Manager page",
  "Analyzer",
  "Power rankings",
  "Midseason report",
];

describe("the flow pick", () => {
  it("picks only Analyzer for a diff of the analyzer site folder", () => {
    expect(pickFlows(flows, ["apps/site/src/app/_routes/analyzer/home.tsx"]).flows).toEqual([
      "Analyzer",
    ]);
  });

  it("picks only Analyzer for a diff of the site side of the analyzer package", () => {
    expect(pickFlows(flows, ["packages/analyzer/site/form/trade-form.tsx"]).flows).toEqual([
      "Analyzer",
    ]);
  });

  it("picks no flow for a diff of the pipeline only, and says that the rebuild covers it", () => {
    const pick = pickFlows(flows, ["apps/pipeline/src/cornerstone/build.py"]);
    expect(pick.flows).toEqual([]);
    expect(describePick(pick)).toBe(
      "No flow: the diff touches the pipeline only, and the base and head rebuild covers it.",
    );
  });

  it("picks all seven flows for a diff of the design package", () => {
    const pick = pickFlows(flows, ["packages/design/site/ui/button.tsx"]);
    expect(pick.flows).toEqual(ALL);
    expect(describePick(pick)).toBe(ALL.join("\n"));
  });

  it("picks all seven flows for a diff of the shell of the site", () => {
    expect(pickFlows(flows, ["apps/site/src/app/layout.tsx"]).flows).toEqual(ALL);
  });

  it("picks no flow for a diff of records only, and says that no glob matches", () => {
    const pick = pickFlows(flows, [".scratch/trusted-green/PRD.md", "docs/adr/0001.md"]);
    expect(pick.flows).toEqual([]);
    expect(describePick(pick)).toBe(
      "No flow: no file of the diff matches a glob of the flow list.",
    );
  });

  it("picks the flows of each file of a mixed diff, in the order of the flow list", () => {
    const files = [
      "apps/site/src/app/_routes/rankings/page.tsx",
      "apps/pipeline/x.py",
      "packages/week/site/hero.tsx",
    ];
    expect(pickFlows(flows, files).flows).toEqual(["Week report", "Power rankings"]);
  });

  it("names no route of the egg board in the flow list", () => {
    for (const flow of flows) expect(flow.route).not.toMatch(/\/eggs\//);
    expect(flows.flatMap((flow) => flow.globs).filter((glob) => glob.includes("eggs"))).toEqual([]);
  });
});
