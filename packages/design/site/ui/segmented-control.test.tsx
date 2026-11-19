/**
 * Tests for the segmented control wrapper: one choice of a few, its name, the change on a tap, and the lock.
 * Each test reads the screen through the roles of the ui-sdk part.
 */
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { useState } from "react";
import { afterEach, describe, expect, it } from "vitest";
import { SegmentedControl, SegmentedControlIndicator, SegmentedControlItem } from "./segmented-control";

function Modes({ disabled = false }: { disabled?: boolean }) {
  const [value, setValue] = useState<string | null>("grade");
  return (
    <>
      <SegmentedControl aria-label="Mode" value={value} onValueChange={setValue} disabled={disabled}>
        <SegmentedControlIndicator />
        <SegmentedControlItem value="grade">Grade a trade</SegmentedControlItem>
        <SegmentedControlItem value="find">Find a trade</SegmentedControlItem>
      </SegmentedControl>
      <output>{value}</output>
    </>
  );
}

const item = (name: string) => screen.getByRole("radio", { name });

afterEach(cleanup);

describe("SegmentedControl", () => {
  it("is one named group with one checked item", () => {
    render(<Modes />);
    expect(screen.getByRole("radiogroup", { name: "Mode" })).toBeTruthy();
    expect(item("Grade a trade").getAttribute("aria-checked")).toBe("true");
    expect(item("Find a trade").getAttribute("aria-checked")).toBe("false");
  });

  it("checks the tapped item", () => {
    render(<Modes />);
    fireEvent.click(item("Find a trade"));
    expect(item("Find a trade").getAttribute("aria-checked")).toBe("true");
    expect(screen.getByRole("status").textContent).toBe("find");
  });

  it("keeps its value while disabled", () => {
    render(<Modes disabled />);
    fireEvent.click(item("Find a trade"));
    expect(item("Grade a trade").getAttribute("aria-checked")).toBe("true");
    expect(screen.getByRole("status").textContent).toBe("grade");
  });

  it("gives each item an equal share of the width", () => {
    render(<Modes />);
    // jsdom has no layout, so the test reads the classes that split the row. The browser check measures the widths.
    for (const name of ["Grade a trade", "Find a trade"]) {
      expect(item(name).className).toMatch(/\bbasis-0\b/);
      expect(item(name).className).toMatch(/\bflex-1\b/);
    }
  });
});
