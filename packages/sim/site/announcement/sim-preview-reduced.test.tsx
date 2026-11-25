/**
 * Tests for the art of The Race Announcement with the reduced-motion media query on: the rows, the bars, and the odds show
 * at rest on the first frame. matchMedia is a stub that must exist before Framer Motion first reads it.
 */
import { render, screen, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, spyOn } from "bun:test";
import { weekElevenSim } from "../fixtures/sim";
import { previewOf } from "./preview";
import { SimPreview } from "./sim-preview";

const matchMediaStub = (query: string) =>
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
  }) as MediaQueryList;

beforeEach(() => {
  spyOn(globalThis, "matchMedia").mockImplementation(matchMediaStub);
});
const BO_GIRDS = 6;

describe("the art of The Race Announcement with reduced motion", () => {
  it("shows each row and the odds at rest on the first frame, with no count", () => {
    render(<SimPreview data={previewOf(weekElevenSim)} you={BO_GIRDS} />);
    const list = screen.getByRole("list", { name: "League board near your team" });
    expect(within(list).getAllByRole("listitem")[1].textContent).toContain("48%");
    expect(screen.getByText("Your team").parentElement?.parentElement?.textContent).toContain(
      "48%",
    );
    for (const element of list.querySelectorAll<HTMLElement>("*")) {
      expect(element.style.opacity === "" || element.style.opacity === "1").toBe(true);
      expect(element.style.transform ?? "").not.toMatch(/translate/);
    }
  });
});
