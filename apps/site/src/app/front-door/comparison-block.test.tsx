/**
 * Tests for the comparison block of a typed "Start A or B?": a pair of bars for each fact, the winning side in red, a dot
 * on each cited fact, and the pick, from the stream that the API recorded for "Start Golden or Mumpfield?".
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { UIMessage } from "ai";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

/* The test sets the reduced-motion switch for each case. */
const motion = vi.hoisted(() => ({ off: false }));
vi.mock("@cpc/design/hooks/use-motion-off", () => ({ useMotionOff: () => motion.off }));

const { ComparisonView, comparisonText } = await import("./comparison-block");
const { answerBlockOf, blockText } = await import("./answer-block");
const { personalViewOf, shownBlock } = await import("./personal-stream");

/* The `data-block` parts of the recorded stream: the block from code first, then the block after the check. */
function recordedParts() {
  return readFileSync(join(__dirname, "..", "..", "fixtures", "personal-answer", "start-sit-compare.sse"), "utf8")
    .split("\n")
    .filter((line) => line.startsWith("data: {"))
    .map((line) => JSON.parse(line.slice("data: ".length)))
    .filter((chunk) => chunk.type === "data-block")
    .map((chunk) => chunk.data);
}

function checked() {
  const block = answerBlockOf(recordedParts().at(-1));
  if (block?.kind !== "comparison") throw new Error("the recorded stream holds no comparison block");
  return block;
}

/* The style of each box of the block that moves, blurs, or scales as it enters. */
function moved(root: HTMLElement) {
  return [root, ...root.querySelectorAll<HTMLElement>("*")].filter((box) => /blur\((?!0)|translate|scale/.test(`${box.style.filter} ${box.style.transform}`));
}

beforeEach(() => {
  motion.off = false;
});

afterEach(cleanup);

describe("the comparison block", () => {
  it("joins the block union and reads as one line of text that ends on the pick (AT-16)", () => {
    const block = checked();
    expect(blockText(block)).toBe(comparisonText(block));
    expect(comparisonText(block)).toMatch(/^M\. Golden or K\. Mumpfield, week 10: Projection 12\.9 to 6\.8;/);
    expect(comparisonText(block)).toMatch(/Start K\. Mumpfield\.$/);
  });

  it("shows the personal part of the stream as the block of the card", () => {
    const message: UIMessage = { id: "a", role: "assistant", parts: recordedParts().map((data) => ({ type: "data-block", data }) as UIMessage["parts"][number]) };
    const view = personalViewOf(message);
    expect(view.block?.kind).toBe("comparison");
    expect(view.block && shownBlock(view.block).answerBlock?.kind).toBe("comparison");
  });

  it("draws a pair of bars from the center for each fact, with the side that wins it in red", () => {
    const block = checked();
    render(<ComparisonView block={block} live={false} />);
    const rows = [...document.querySelectorAll<HTMLElement>("[data-fact]")];
    expect(rows.map((row) => row.dataset.fact)).toEqual(block.facts.map((fact) => fact.key));
    const projection = screen.getByRole("img", { name: "Projection: M. Golden 12.9, K. Mumpfield 6.8. M. Golden wins it." });
    const bars = [...projection.querySelectorAll<HTMLElement>("[data-side]")];
    expect(bars.map((bar) => bar.dataset.side)).toEqual(["0", "1"]);
    expect(bars[0].className).toContain("bg-accent");
    expect(bars[0].className).toContain("origin-right");
    expect(bars[1].className).not.toContain("bg-accent");
    expect(bars[1].className).toContain("origin-left");
    // Each fact reds only the side that wins it.
    for (const fact of block.facts) {
      const red = [...document.querySelectorAll<HTMLElement>(`[data-fact="${fact.key}"] [data-side]`)].filter((bar) => bar.className.includes("bg-accent"));
      expect(red.map((bar) => Number(bar.dataset.side))).toEqual(fact.winner === null ? [] : [fact.winner]);
    }
  });

  it("puts a dot on each fact that the checked text cites, and none before the check", () => {
    render(<ComparisonView block={checked()} live={false} />);
    expect([...document.querySelectorAll<HTMLElement>("[data-cited]")].map((dot) => dot.closest<HTMLElement>("[data-fact]")?.dataset.fact)).toEqual(["projection", "defense", "team_points"]);
    cleanup();
    const first = answerBlockOf(recordedParts()[0]);
    if (first?.kind !== "comparison") throw new Error("no comparison block");
    render(<ComparisonView block={first} live={false} />);
    expect(document.querySelectorAll("[data-cited]")).toHaveLength(0);
  });

  it("closes with the pick", () => {
    render(<ComparisonView block={checked()} live={false} />);
    expect(screen.getByText("Start K. Mumpfield.")).toBeTruthy();
  });

  it("shows with no slide, no blur, and no growth under reduced motion", () => {
    motion.off = true;
    const { container } = render(<ComparisonView block={checked()} live />);
    expect(moved(container)).toEqual([]);
  });

  it("grows the bars from the center line with motion on, and shows a kept block at once", () => {
    const { container } = render(<ComparisonView block={checked()} live />);
    expect(moved(container).some((box) => /scaleX\(0\)/.test(box.style.transform))).toBe(true);
    cleanup();
    const kept = render(<ComparisonView block={checked()} live={false} />);
    expect(moved(kept.container)).toEqual([]);
  });
});
