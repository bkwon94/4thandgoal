/**
 * Tests for the reveal component.
 * After hydration the page must turn off the CSS safety rule, so Framer Motion owns the reveal.
 */
import { cleanup, render } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { Reveal } from "./reveal";

afterEach(() => {
  cleanup();
  document.documentElement.removeAttribute("data-hydrated");
});

describe("Reveal", () => {
  it("sets data-hydrated on the html element after render", () => {
    expect(document.documentElement.hasAttribute("data-hydrated")).toBe(false);
    render(<Reveal>Week 6</Reveal>);
    expect(document.documentElement.hasAttribute("data-hydrated")).toBe(true);
  });
});
