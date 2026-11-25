/**
 * Tests for the bar chart part: one named group with one tab stop, the arrow keys between its bars, and the press of a bar.
 * Each test reads the screen through the roles of the part.
 */
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { useState } from "react";
import { afterEach, describe, expect, it } from "bun:test";
import { BarChart, BarChartBar } from "./bar-chart";

function Board() {
  const [picked, setPicked] = useState<string | null>(null);
  return (
    <>
      <BarChart aria-label="Odds" value={picked} onValueChange={setPicked}>
        {["Lil Fridge", "Bo Girds", "Teez Nuts"].map((name) => (
          <BarChartBar key={name} value={name}>
            {name}
          </BarChartBar>
        ))}
      </BarChart>
      <output>{picked ?? "none"}</output>
    </>
  );
}

const bar = (name: string) => screen.getByRole("button", { name });

afterEach(cleanup);

describe("BarChart", () => {
  it("is one named group whose bars hold one tab stop", () => {
    render(<Board />);
    expect(screen.getByRole("group", { name: "Odds" })).toBeTruthy();
    const stops = screen.getAllByRole("button").filter((el) => el.tabIndex === 0);
    expect(stops).toHaveLength(1);
  });

  it("moves the focus to the next bar and back with the arrow keys", () => {
    render(<Board />);
    bar("Lil Fridge").focus();
    fireEvent.keyDown(bar("Lil Fridge"), { key: "ArrowDown" });
    expect(document.activeElement).toBe(bar("Bo Girds"));
    fireEvent.keyDown(bar("Bo Girds"), { key: "ArrowUp" });
    expect(document.activeElement).toBe(bar("Lil Fridge"));
  });

  it("picks the pressed bar", () => {
    render(<Board />);
    fireEvent.click(bar("Teez Nuts"));
    expect(screen.getByRole("status").textContent).toBe("Teez Nuts");
    expect(bar("Teez Nuts").hasAttribute("data-selected")).toBe(true);
  });
});
