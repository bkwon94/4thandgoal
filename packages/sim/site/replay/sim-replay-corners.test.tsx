/**
 * Tests for the corners of the sim replay on the real sim file of CPC 2026 week 8: the replay follows the rule of the
 * midseason report, so no element has a full pill or a corner above 8 px. The press shows the table, then the end.
 */
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { sim } from "../fixtures/sim";
import { SimReplay } from "./sim-replay";

afterEach(cleanup);

/* The radius classes of the elements in the container. rounded-report is the 8 px radius of the report. */
const corners = (container: HTMLElement) =>
  new Set([...container.querySelectorAll("[class*='rounded']")].flatMap((e) => e.className.match(/(?<=(?:^|\s))rounded-\S+/g) ?? []));

describe("the corners of the sim replay", () => {
  it("has no full pill and no corner above 8 px before the press", () => {
    const { container } = render(<SimReplay sim={sim} pick={() => 0} />);
    expect([...corners(container)]).toEqual(["rounded-report"]);
  });

  it("has no full pill and no corner above 8 px at the end of a run", () => {
    const { container } = render(<SimReplay sim={sim} pick={() => 0} />);
    fireEvent.click(screen.getByRole("button", { name: "Sim the season" }));
    fireEvent.click(screen.getByRole("button", { name: "Skip to the end" }));
    // The avatar of the champion and the rays are round shapes, not pills, so they are the only other radius.
    const others = [...corners(container)].filter((name) => name !== "rounded-report" && name !== "rounded-full");
    expect(others).toEqual([]);
    expect(corners(container).has("rounded-report")).toBe(true);
  });
});
