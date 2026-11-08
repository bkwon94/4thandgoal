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
import type { HeroScene } from "./scene-math";
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

/* A small scene of two lights, as a page passes it to its first hero. */
const SCENE: HeroScene = {
  lights: [
    { x: 0, y: 98.88, label: "London Cooking · 98.88", tone: "flare" },
    { x: 1, y: 100.31, label: "The Blue Tent · 100.31", tone: "flare" },
  ],
  guides: [],
  margin: { from: 1, to: 0, text: "+1.43" },
  restIndex: 1,
  mode: "settle",
};
afterAll(() => vi.unstubAllGlobals());

describe("Hero", () => {
  it("takes no free content, and renders a hero with only a title in a region named by its label (AT-14)", () => {
    // The typecheck proves the rule: if Hero took children, this directive would be unused and tsc would fail.
    // @ts-expect-error Hero takes the six slots and no children.
    void (<Hero label="Page not found">404</Hero>);
    render(<Hero label="Page not found" title="Page not found" />);
    const hero = screen.getByRole("region", { name: "Page not found" });
    expect(within(hero).getByRole("heading", { level: 1, name: "Page not found" })).toBeTruthy();
  });

  it("draws the grid, the glow, and the four brackets, all hidden from a screen reader, and no scan line (AT-7, AT-39)", () => {
    const { container } = render(<Hero label="Week 8" title="Week 8" />);
    const art = container.querySelectorAll("[data-hero-art]");
    expect([...art].map((element) => element.getAttribute("data-hero-art"))).toEqual([
      "texture",
      "bracket",
      "bracket",
      "bracket",
      "bracket",
    ]);
    for (const element of art) expect(element.closest("[aria-hidden=true]")).not.toBeNull();
  });
});

/* The hero slots that a hero renders, in the order of the markup. */
function slotsOf(container: HTMLElement): (string | null)[] {
  return [...container.querySelectorAll("[data-hero-slot]")].map((element) => element.getAttribute("data-hero-slot"));
}

describe("Hero slots", () => {
  it("renders the six slots in the slot order, whatever the order of the props", () => {
    const { container } = render(
      <Hero
        label="To Infinity and Bijan"
        action={<a href="/week-08/">Week 8</a>}
        stats={<span>Playoff 41%</span>}
        feature={<span>Week chips</span>}
        meta="bjpicard96"
        title="To Infinity and Bijan"
        eyebrow="7-9 · 9th of 12"
      />,
    );
    expect(slotsOf(container)).toEqual(["eyebrow", "title", "meta", "feature", "stats", "action"]);
    const hero = screen.getByRole("region", { name: "To Infinity and Bijan" });
    expect(hero.textContent).toBe("7-9 · 9th of 12To Infinity and Bijanbjpicard96Week chipsPlayoff 41%Week 8");
  });

  it("renders no element for an absent slot, and no hairline with no stats", () => {
    const { container } = render(<Hero label="Rank 1" title="Lil Fridge" />);
    expect(slotsOf(container)).toEqual(["title"]);
    expect(container.querySelector("[data-hero-rule]")).toBeNull();
  });

  it("draws one hairline, hidden from a screen reader, directly before the stats", () => {
    const { container } = render(<Hero label="Rank 1" title="Lil Fridge" stats={<span>Playoff 99%</span>} />);
    const rule = container.querySelector("[data-hero-rule]")!;
    expect(rule.getAttribute("aria-hidden")).toBe("true");
    expect(rule.nextElementSibling?.getAttribute("data-hero-slot")).toBe("stats");
  });

  it("renders the title as an h1 by default and as an h2 with level 2", () => {
    render(<Hero label="Week 8" title="The Blue Tent by 1.43" />);
    const h1 = screen.getByRole("heading", { level: 1, name: "The Blue Tent by 1.43" });
    cleanup();
    render(<Hero label="Week 8" title="The Blue Tent by 1.43" level={2} />);
    const h2 = screen.getByRole("heading", { level: 2, name: "The Blue Tent by 1.43" });
    expect(screen.queryByRole("heading", { level: 1 })).toBeNull();
    // The level changes the element, not the look.
    expect(h2.className).toBe(h1.className);
  });
  it("draws no scene with no scene, so the hero keeps the static grid", () => {
    const { container } = render(<Hero label="Rank 1" title="Lil Fridge" />);
    expect(container.querySelector("canvas")).toBeNull();
  });

  it("draws one scene canvas, hidden from a screen reader, and keeps the text of the slots as it is", () => {
    const { container } = render(
      <Hero label="Matchup of the Week" eyebrow="Week 08" title="The Blue Tent by 1.43" scene={SCENE} />,
    );
    const canvases = container.querySelectorAll("canvas");
    expect(canvases).toHaveLength(1);
    expect(canvases[0].closest("[aria-hidden='true']")).not.toBeNull();
    expect(slotsOf(container)).toEqual(["eyebrow", "title"]);
    expect(screen.getByRole("region", { name: "Matchup of the Week" }).textContent).toBe("Week 08The Blue Tent by 1.43");
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
