/**
 * Tests for the transaction feed under reduced motion and with motion on. The feed is the block of a free answer that
 * the API recorded in a live run of week 6, with its trades, its waiver claims, and its free agent moves.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

/* The test sets the reduced-motion switch for each case. */
const motion = vi.hoisted(() => ({ off: false }));
vi.mock("@cpc/design/hooks/use-motion-off", () => ({ useMotionOff: () => motion.off }));

const { FeedView, feedBlockSchema } = await import("./feed-block");

/* The feed of the `data-block` part of the recorded week 6 stream. */
function recordedFeed() {
  const stream = readFileSync(join(__dirname, "..", "..", "fixtures", "free-answer", "moves-feed-week-6.sse"), "utf8");
  const part = stream
    .split("\n")
    .filter((line) => line.startsWith("data: {"))
    .map((line) => JSON.parse(line.slice("data: ".length)))
    .find((chunk) => chunk.type === "data-block");
  return feedBlockSchema.parse(part.data);
}

beforeEach(() => {
  motion.off = false;
});

afterEach(cleanup);

/* The style of each box of the feed that moves, blurs, or scales as it enters. */
function moved(root: HTMLElement) {
  return [root, ...root.querySelectorAll<HTMLElement>("*")].filter((box) => /blur\((?!0)|translate|scale/.test(`${box.style.filter} ${box.style.transform}`));
}

describe("the transaction feed", () => {
  it("shows with no slide, no blur, and no growth of a bar under reduced motion", () => {
    motion.off = true;
    const { container } = render(<FeedView block={recordedFeed()} live />);
    expect(moved(container)).toEqual([]);
    expect(screen.getAllByRole("listitem").length).toBeGreaterThan(20);
  });

  it("grows each bar of the strip from its base and rises each row from a blur with motion on", () => {
    const { container } = render(<FeedView block={recordedFeed()} live />);
    const bars = [...screen.getByRole("img").querySelectorAll<HTMLElement>(".origin-bottom")];
    expect(bars).toHaveLength(8);
    expect(bars.every((bar) => /scaleY\(0\)/.test(bar.style.transform))).toBe(true);
    expect(moved(container).some((box) => /blur/.test(box.style.filter))).toBe(true);
  });

  it("shows a kept feed at once, with no move", () => {
    const { container } = render(<FeedView block={recordedFeed()} live={false} />);
    expect(moved(container)).toEqual([]);
  });
});
