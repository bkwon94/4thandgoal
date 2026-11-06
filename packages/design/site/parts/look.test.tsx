/**
 * Tests for the parts of the look: the hero, the card, the tile, the round photo frame, and the rise.
 * They read what a reader sees by role, name, and text, not the class names.
 */
import { cleanup, render, screen, within } from "@testing-library/react";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";
import { Card } from "./card";
import { Hero } from "./hero";
import { PhotoFrame, initialsOf } from "./photo-frame";
import { Rise } from "./rise";
import { Tile } from "./tile";

/* jsdom has no matchMedia, and Framer Motion reads it. The stub matches no query. */
vi.stubGlobal(
  "matchMedia",
  (query: string) =>
    ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }) as unknown as MediaQueryList,
);

afterEach(() => cleanup());
afterAll(() => vi.unstubAllGlobals());

describe("Hero", () => {
  it("shows its content in a region named by its label", () => {
    render(
      <Hero label="Page not found">
        <h1>404</h1>
      </Hero>,
    );
    const hero = screen.getByRole("region", { name: "Page not found" });
    expect(within(hero).getByRole("heading", { level: 1, name: "404" })).toBeTruthy();
  });

  it("draws the grid, the glow, the four brackets, and one scan line, all hidden from a screen reader (AT-7)", () => {
    const { container } = render(<Hero label="Week 8">Text</Hero>);
    const art = container.querySelectorAll("[data-hero-art]");
    expect([...art].map((element) => element.getAttribute("data-hero-art"))).toEqual([
      "texture",
      "scan",
      "bracket",
      "bracket",
      "bracket",
      "bracket",
    ]);
    for (const element of art) expect(element.closest("[aria-hidden=true]")).not.toBeNull();
  });
});

describe("Card", () => {
  it("holds its content", () => {
    render(<Card>Week 8 recap</Card>);
    expect(screen.getByText("Week 8 recap")).toBeTruthy();
  });

  it("renders as the element that the list asks for", () => {
    render(
      <ul>
        <Card as="li">One game</Card>
      </ul>,
    );
    expect(screen.getByRole("listitem").textContent).toBe("One game");
  });
});

describe("Tile", () => {
  it("shows the label, the one number, and the note", () => {
    render(<Tile label="Top score" value="151.32" note="Lil Fridge" />);
    const tile = screen.getByText("151.32").closest("div")!.parentElement!;
    expect(tile.textContent).toBe("Top score151.32Lil Fridge");
  });
});

describe("PhotoFrame", () => {
  it("shows the photo, named by the player", () => {
    render(<PhotoFrame src="/2026/week-08/headshots/4984.png" name="Josh Allen" />);
    expect(screen.getByRole("img", { name: "Josh Allen" }).getAttribute("src")).toBe("/2026/week-08/headshots/4984.png");
  });

  it("shows the initials when no image exists, and keeps the name for a screen reader (AT-33)", () => {
    render(<PhotoFrame src={null} name="Amon-Ra St. Brown" />);
    const frame = screen.getByRole("img", { name: "Amon-Ra St. Brown" });
    expect(frame.textContent).toBe("AS");
    expect(frame.querySelector("img")).toBeNull();
  });

  it("hides a photo from a screen reader when the row already names the player", () => {
    render(<PhotoFrame src="/a.png" name="Josh Allen" decorative />);
    expect(screen.queryByRole("img")).toBeNull();
  });

  it("takes the first letters of the first two words of a name", () => {
    expect(initialsOf("Josh Allen")).toBe("JA");
    expect(initialsOf("London Cooking")).toBe("LC");
    expect(initialsOf("Bills")).toBe("B");
    expect(initialsOf("  ")).toBe("");
  });
});

describe("Rise", () => {
  it("holds its content in a reveal box that shows at rest with no script", () => {
    render(<Rise step={2}>Weekly Reports</Rise>);
    expect(screen.getByText("Weekly Reports").closest("[data-reveal]")).not.toBeNull();
  });
});
