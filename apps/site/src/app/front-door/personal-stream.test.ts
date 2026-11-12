/**
 * Tests for the data part of a personal Topic as the Thread reads it. The part is the one that the API recorded in a
 * live run of Weak spots, with and without the `kind` that the API now adds.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { UIMessage } from "ai";
import { describe, expect, it } from "vitest";
import { personalResultSchema, personalViewOf } from "./personal-stream";

/* The data of the `data-block` part of the recorded stream of Weak spots, which predates the kind. */
function recordedBlock(): Record<string, unknown> {
  const stream = readFileSync(join(__dirname, "..", "..", "fixtures", "personal-answer", "weak-spots.sse"), "utf8");
  return stream
    .split("\n")
    .filter((line) => line.startsWith("data: {"))
    .map((line) => JSON.parse(line.slice("data: ".length)))
    .find((chunk) => chunk.type === "data-block").data;
}

const messageWith = (data: unknown): UIMessage => ({ id: "a", role: "assistant", parts: [{ type: "data-block", data } as UIMessage["parts"][number]] });

describe("the data part of a personal Topic", () => {
  it("carries the kind rows, and never reads as the block of a free answer", () => {
    const view = personalViewOf(messageWith({ kind: "rows", ...recordedBlock() }));
    expect(view.block?.kind).toBe("rows");
    expect(view.block?.topic).toBe("weak_spots");
    expect(view.answerBlock).toBeNull();
  });

  it("reads a part kept with no kind as the kind rows, so an Answer kept in the browser still shows", () => {
    expect(personalViewOf(messageWith(recordedBlock())).block?.kind).toBe("rows");
    expect(personalResultSchema.parse({ block: recordedBlock(), text: "Kept.", key: "k" }).block.kind).toBe("rows");
  });

  it("drops a part with a kind of no personal block", () => {
    expect(personalViewOf(messageWith({ ...recordedBlock(), kind: "list" })).block).toBeNull();
  });
});
