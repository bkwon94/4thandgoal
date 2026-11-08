/**
 * Tests for the Grade dial. They render the grade of the first fixture entry, and a set of ranks at both ends.
 * They read the accessible name of each arc, the rank text in it, and the count of lit blades.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { managers as fixture } from "../fixtures/managers";
import { GradeDial } from "./grade-dial";

afterEach(cleanup);

/* The first fixture entry ranks 1st, 4th, 7th, and 10th of 12 on the four parts. */
const parts = fixture.managers[0].grade!.parts;

/* The four arcs, in the order the dial draws them. */
function arcs() {
  return within(screen.getByRole("list", { name: "Grade Dial" })).getAllByRole("img");
}

/* The count of lit blades of one arc. */
function lit(arc: HTMLElement) {
  return arc.querySelectorAll('[data-blade][data-on="true"]').length;
}

describe("GradeDial", () => {
  it("names each arc with its part, its rank, and its weight", () => {
    render(<GradeDial parts={parts} teams={12} />);
    expect(arcs().map((arc) => arc.getAttribute("aria-label"))).toEqual([
      "Projection Ahead: 1st of 12, 45% of the grade",
      "Season Production: 4th of 12, 30% of the grade",
      "Trade Value: 7th of 12, 10% of the grade",
      "Depth And Holes: 10th of 12, 15% of the grade",
    ]);
  });

  it("draws 12 blades per arc and lights the count of teams plus one minus the rank", () => {
    render(<GradeDial parts={parts} teams={12} />);
    for (const arc of arcs()) expect(arc.querySelectorAll("[data-blade]")).toHaveLength(12);
    expect(arcs().map(lit)).toEqual([12, 9, 6, 3]);
  });

  it("lights every blade for rank 1 and one blade for the last rank", () => {
    const ends = [
      { key: "projection" as const, rank: 1 },
      { key: "production" as const, rank: 12 },
      { key: "trade_value" as const, rank: 2 },
      { key: "depth" as const, rank: 11 },
    ];
    render(<GradeDial parts={ends} teams={12} />);
    expect(arcs().map(lit)).toEqual([12, 1, 11, 2]);
  });

  it("shows the rank in the arc and the part name and weight under it as text", () => {
    render(<GradeDial parts={parts} teams={12} />);
    const first = arcs()[0];
    expect(first.textContent).toContain("1st");
    expect(first.textContent).toContain("of 12");
    expect(first.textContent).toContain("Projection Ahead");
    expect(first.textContent).toContain("45% of the grade");
  });

  it("drops the count of teams under the rank in the small size", () => {
    render(<GradeDial parts={parts} teams={12} size="small" />);
    const first = arcs()[0];
    expect(first.textContent).toContain("1st");
    expect(first.textContent).not.toContain("of 12");
    expect(first.textContent).toContain("45%");
    expect(first.getAttribute("aria-label")).toBe("Projection Ahead: 1st of 12, 45% of the grade");
  });
});
