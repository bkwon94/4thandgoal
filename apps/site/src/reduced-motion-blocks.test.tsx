/**
 * Tests that every block of an Answer and each open row show at once with the reduced-motion media query on (AT-39).
 * Each block comes from real data: the week 9 topics.json of cpc and the streams that real runs of the API recorded.
 */
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { cleanup, fireEvent, render, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { type AnswerBlock, BlockView, answerBlockOf, answerBlockSchema } from "@/app/front-door/answer-block";

/* matchMedia is a stub that matches the reduced-motion query. Framer Motion reads it when the first part mounts. */
vi.stubGlobal(
  "matchMedia",
  (query: string) =>
    ({
      // Framer Motion asks for "(prefers-reduced-motion)" with no value, so the stub matches the feature name.
      matches: query.includes("prefers-reduced-motion"),
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as MediaQueryList,
);

afterEach(() => cleanup());

const FIXTURES = join(__dirname, "fixtures");
const STREAMS = join(__dirname, "app", "front-door", "fixtures");

/* Each object with a `kind` inside a value that reads as an answer block. A personal stream nests its block under the
   rows part, and a trade stream nests it under its answer, so the walk reads every level. */
function blocksOf(value: unknown, found: AnswerBlock[] = []): AnswerBlock[] {
  if (Array.isArray(value)) for (const each of value) blocksOf(each, found);
  else if (value && typeof value === "object") {
    const block = "kind" in value ? answerBlockOf(value) : null;
    if (block) found.push(block);
    else for (const each of Object.values(value)) blocksOf(each, found);
  }
  return found;
}

/* The parts of a recorded event stream, one JSON value per data line. */
const partsOf = (path: string) =>
  readFileSync(path, "utf8")
    .split("\n")
    .filter((line) => line.startsWith("data: {"))
    .map((line) => JSON.parse(line.slice("data: ".length)) as unknown);

/* The fullest block of each kind in the recorded data, so a block with no rows, such as a trade card of no offer, never
   stands for its kind. */
function recordedBlocks(): Map<string, AnswerBlock> {
  const sources: unknown[] = [JSON.parse(readFileSync(join(FIXTURES, "recap", "cpc", "public", "2026", "week-09", "topics.json"), "utf8"))];
  for (const folder of ["personal-answer", "free-answer"]) {
    for (const name of readdirSync(join(FIXTURES, folder)).filter((file) => file.endsWith(".sse"))) sources.push(partsOf(join(FIXTURES, folder, name)));
  }
  for (const name of readdirSync(STREAMS).filter((file) => file.endsWith(".json"))) sources.push(JSON.parse(readFileSync(join(STREAMS, name), "utf8")));
  const byKind = new Map<string, AnswerBlock>();
  const size = (block?: AnswerBlock) => (block ? JSON.stringify(block).length : 0);
  for (const block of blocksOf(sources)) if (size(block) > size(byKind.get(block.kind))) byKind.set(block.kind, block);
  return byKind;
}

const BLOCKS = recordedBlocks();
const KINDS = answerBlockSchema.options.map((option) => option.shape.kind.value);

/* No part moves or blurs. A digit column of the lineup total sits at its digit with a translate, which is a place and no
   move, so it must carry the class that drops its roll under reduced motion. */
function expectNoMove(root: HTMLElement) {
  for (const part of [root, ...root.querySelectorAll<HTMLElement>("*")]) {
    expect(part.style.filter).not.toMatch(/blur/);
    if (part.closest("[data-total]")) {
      if (part.style.transform) expect(part.className).toContain("motion-reduce:transition-none");
      continue;
    }
    expect(part.style.transform).not.toMatch(/translate|scale/);
  }
}

/* Every part ends at full view: no part stays at opacity 0. */
async function expectShown(root: HTMLElement) {
  await waitFor(() => {
    for (const part of [root, ...root.querySelectorAll<HTMLElement>("*")]) expect(part.style.opacity).not.toBe("0");
  });
}

describe("Reduced motion on the blocks of an Answer (AT-39)", () => {
  it("has recorded data for every block kind", () => {
    expect([...BLOCKS.keys()].sort()).toEqual([...KINDS].sort());
  });

  it.each(KINDS)("shows the %s block at once, with no slide and no blur", async (kind) => {
    const { container } = render(<BlockView block={BLOCKS.get(kind)!} live />);
    const block = container.querySelector<HTMLElement>("[data-block]")!;
    expect(block.getAttribute("data-block")).toBe(kind);
    expectNoMove(container);
    await expectShown(container);
    expectNoMove(container);
  });

  it.each(["lineup", "waiver_list", "sell_list", "trade"])("opens a row of the %s block at once, with no slide and no blur", async (kind) => {
    const { container } = render(<BlockView block={BLOCKS.get(kind)!} live />);
    await expectShown(container);
    const row = Array.from(container.querySelectorAll<HTMLElement>("button[aria-expanded]")).find((button) => button.getAttribute("aria-expanded") === "false")!;
    expect(row).toBeTruthy();
    fireEvent.click(row);
    expect(row.getAttribute("aria-expanded")).toBe("true");
    const detail = document.getElementById(row.getAttribute("aria-controls") ?? "")!;
    // The detail shows in the same tap: no hidden panel, and an Open card waits on no timer.
    expect(detail.hasAttribute("hidden")).toBe(false);
    const card = detail.closest<HTMLElement>(".open-card");
    if (card) expect(card.style.getPropertyValue("--oc-dur")).toBe("0s");
    expectNoMove(container);
    await expectShown(detail);
  });
});
