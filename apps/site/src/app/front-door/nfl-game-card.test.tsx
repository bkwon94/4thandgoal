/**
 * Tests for the NFL game card of a free answer: the tug bar of the expected margin, the strip of the 32 defenses with
 * the opponent lit, and the two pass-share bars, from the Bears stream and the Packers block that the API recorded.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

/* The test sets the reduced-motion switch for each case. */
const motion = vi.hoisted(() => ({ off: false }));
vi.mock("@cpc/design/hooks/use-motion-off", () => ({ useMotionOff: () => motion.off }));

const { NflGameView, nflGameText } = await import("./nfl-game-card");
const { answerBlockOf, blockText } = await import("./answer-block");

const FIXTURES = join(__dirname, "..", "..", "fixtures", "free-answer");

/* The block of the `data-block` part of the recorded stream of "How does the Bears game look?". */
function bearsGame() {
  const part = readFileSync(join(FIXTURES, "nfl-game-bears-week-11.sse"), "utf8")
    .split("\n")
    .filter((line) => line.startsWith("data: {"))
    .map((line) => JSON.parse(line.slice("data: ".length)))
    .find((chunk) => chunk.type === "data-block");
  const block = answerBlockOf(part.data);
  if (block?.kind !== "nfl_game") throw new Error("the recorded stream holds no NFL game card");
  return block;
}

function packersGame() {
  const block = answerBlockOf(JSON.parse(readFileSync(join(FIXTURES, "nfl-game-packers-week-10.json"), "utf8")));
  if (block?.kind !== "nfl_game") throw new Error("the recorded block is no NFL game card");
  return block;
}

/* The style of each box of the card that moves, blurs, or scales as it enters. */
function moved(root: HTMLElement) {
  return [root, ...root.querySelectorAll<HTMLElement>("*")].filter((box) => /blur\((?!0)|translate|scale/.test(`${box.style.filter} ${box.style.transform}`));
}

beforeEach(() => {
  motion.off = false;
});

afterEach(cleanup);

describe("the NFL game card", () => {
  it("joins the block union and reads as one line of text with the margin (AT-19)", () => {
    const block = packersGame();
    expect(blockText(block)).toBe(nflGameText(block));
    expect(nflGameText(block)).toContain("Packers 22.5, Vikings 19.5: Packers by 3");
    expect(nflGameText(bearsGame())).toContain("Bears 22.8, Saints 22.8: even");
  });

  it("pulls the tug bar toward the favorite in red, by the margin", () => {
    render(<NflGameView block={packersGame()} live={false} />);
    expect(screen.getByRole("img", { name: "Expected margin: Packers by 3" })).toBeTruthy();
    const pull = document.querySelector<HTMLElement>("[data-tug]");
    expect(pull?.dataset.tug).toBe("left");
    expect(pull?.className).toContain("bg-accent");
  });

  it("shows an even game with no pull", () => {
    render(<NflGameView block={bearsGame()} live={false} />);
    expect(screen.getByRole("img", { name: "Expected margin: even game" })).toBeTruthy();
    expect(document.querySelector("[data-tug]")).toBeNull();
  });

  it("shows the 32 defenses against the position with only the opponent lit", () => {
    render(<NflGameView block={bearsGame()} live={false} />);
    const strip = screen.getByRole("img", { name: /Saints defense allows 29\.8 WR points a game, 14th fewest of 32/ });
    const ticks = [...strip.querySelectorAll<HTMLElement>("[data-defense]")];
    expect(ticks).toHaveLength(32);
    expect(ticks.filter((tick) => tick.className.includes("bg-accent")).map((tick) => tick.dataset.defense)).toEqual(["NO"]);
  });

  it("sets each pass-share bar against the league mark", () => {
    render(<NflGameView block={bearsGame()} live={false} />);
    expect(screen.getByRole("img", { name: "Bears pass 50% of plays, against 55% for the league" })).toBeTruthy();
    expect(screen.getByRole("img", { name: "Saints pass 62% of plays, against 55% for the league" })).toBeTruthy();
    expect(document.querySelectorAll("[data-league-mark]")).toHaveLength(2);
  });

  it("shows with no slide, no blur, and no growth under reduced motion", () => {
    motion.off = true;
    const { container } = render(<NflGameView block={packersGame()} live />);
    expect(moved(container)).toEqual([]);
  });

  it("grows the bars and rises each part from a blur with motion on, and shows a kept card at once", () => {
    const { container } = render(<NflGameView block={packersGame()} live />);
    expect(moved(container).some((box) => /scaleX\(0\)/.test(box.style.transform))).toBe(true);
    expect(moved(container).some((box) => /blur/.test(box.style.filter))).toBe(true);
    cleanup();
    const kept = render(<NflGameView block={packersGame()} live={false} />);
    expect(moved(kept.container)).toEqual([]);
  });
});
