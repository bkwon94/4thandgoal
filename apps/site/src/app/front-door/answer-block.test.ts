/**
 * Tests for the block contract of the site: one union over `kind`. The blocks are the data parts that the API recorded
 * in live free answers, so the free answer kinds list, table, and player still pass the union.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { answerBlockOf, answerBlockSchema, blockText } from "./answer-block";

/* The data of the `data-block` part of a recorded stream. */
function recordedBlock(name: string): unknown {
  const stream = readFileSync(join(__dirname, "..", "..", "fixtures", "free-answer", `${name}.sse`), "utf8");
  const part = stream
    .split("\n")
    .filter((line) => line.startsWith("data: {"))
    .map((line) => JSON.parse(line.slice("data: ".length)))
    .find((chunk) => chunk.type === "data-block");
  return part.data;
}

describe("the block union of the site", () => {
  it("is one union over kind", () => {
    expect(answerBlockSchema.def.type).toBe("union");
    expect(answerBlockSchema.def.discriminator).toBe("kind");
  });

  it.each([
    ["block-list", "list"],
    ["block-table", "table"],
    ["block-player", "player"],
    ["moves-feed", "feed"],
    ["moves-feed-week-6", "feed"],
  ])("passes the %s block of a recorded free answer as the kind %s", (name, kind) => {
    expect(answerBlockOf(recordedBlock(name))?.kind).toBe(kind);
  });

  it("passes no data part with a kind outside the union or with no kind", () => {
    expect(answerBlockOf({ kind: "chart", title: "Points" })).toBeNull();
    expect(answerBlockOf({ title: "Points", rows: [] })).toBeNull();
  });

  it("gives the feed one line of plain text with each move, for the turn of the Answer", () => {
    const feed = answerBlockOf(recordedBlock("moves-feed-week-6"))!;
    const line = blockText(feed);
    expect(line.startsWith("Week 6 moves: Wed Oct 21, waiver claim: Bo Girds added Terrance Ferguson and dropped Pat Freiermuth for $0;")).toBe(true);
    expect(line).toContain("trade: To Infinity and Bijan got Braelon Allen, Malik Nabers, Jared Goff, Breece Hall; Return of T Mac got");
    expect(line.endsWith("And 36 more.")).toBe(true);
  });
});
