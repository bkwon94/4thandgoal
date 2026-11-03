/**
 * Tests for the cn helper. They check that the custom scale names, colors, and breakpoint sort into the right groups.
 */
import { describe, expect, it } from "vitest";
import { cn } from "./utils";

describe("cn", () => {
  it("keeps a size token next to a color", () => {
    expect(cn("text-label", "text-red")).toBe("text-label text-red");
  });

  it("keeps only the last of two size tokens", () => {
    expect(cn("text-label", "text-meta")).toBe("text-meta");
  });

  it("keeps only the last of two margin tokens", () => {
    expect(cn("mb-sp-3", "mb-sp-1")).toBe("mb-sp-1");
  });

  it("keeps only the last of two padding tokens", () => {
    expect(cn("p-sp-4", "p-sp-2")).toBe("p-sp-2");
  });

  it("keeps a movement color next to a size token", () => {
    expect(cn("text-row", "text-move-up")).toBe("text-row text-move-up");
  });

  it("keeps only the last of two movement colors", () => {
    expect(cn("text-move-up", "text-move-down")).toBe("text-move-down");
  });

  it("keeps only the last of two rankings column widths", () => {
    expect(cn("w-rankings-col", "w-sp-4")).toBe("w-sp-4");
  });

  it("keeps only the last of two page grid columns", () => {
    expect(cn("page:grid-cols-2", "page:grid-cols-4")).toBe("page:grid-cols-4");
  });
});
