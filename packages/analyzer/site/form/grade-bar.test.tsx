/**
 * Tests for the grade bar: the label and the style of its button while a grade runs and after it settles.
 * The grading prop drives the state, because a grade that the finder starts has no press of the button.
 */
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "bun:test";
import { GradeBar } from "./grade-bar";

afterEach(cleanup);

const grade = () => Promise.resolve();
const classes = (button: HTMLElement) => button.className.split(/\s+/);

/* The plain classes of the muted style of the off bar, and of the accent style of the on bar. */
const MUTED = ["border-rule", "bg-raised", "text-mute"];
const ACCENT = ["bg-accent", "text-on-dark"];

describe("the grade bar", () => {
  it("shows Grading… in the muted style while grading is true, and Grade the Trade in the accent style after", () => {
    const { rerender } = render(<GradeBar ready grading level={1} onGrade={grade} />);
    const busy = screen.getByRole("button");
    expect(busy.textContent).toBe("Grading…");
    expect(classes(busy)).toEqual(expect.arrayContaining(MUTED));
    expect(classes(busy)).not.toEqual(expect.arrayContaining(ACCENT));
    // The button stays in the tab order while grading, so it is not natively disabled.
    expect((busy as HTMLButtonElement).disabled).toBe(false);

    rerender(<GradeBar ready grading={false} level={1} onGrade={grade} />);
    const idle = screen.getByRole("button");
    expect(idle.textContent).toBe("Grade the Trade");
    expect(classes(idle)).toEqual(expect.arrayContaining(ACCENT));
    for (const name of MUTED) expect(classes(idle)).not.toContain(name);
  });
});
