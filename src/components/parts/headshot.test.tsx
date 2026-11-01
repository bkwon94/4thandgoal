/**
 * Tests for the Headshot part: the src, the empty alt text, a size in pixels, and the swap to the default headshot.
 * They read only the attributes of the image, never a class name.
 */
import { cleanup, fireEvent, render } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { HEADSHOT_FALLBACK, headshotSrc } from "@/lib/headshot";
import { Headshot } from "./headshot";

function renderHeadshot(element: React.ReactElement) {
  const { container } = render(element);
  return container.querySelector("img") as HTMLImageElement;
}

afterEach(cleanup);

describe("Headshot", () => {
  it("renders the src it gets", () => {
    expect(renderHeadshot(<Headshot src="headshots/4046.png" />).getAttribute("src")).toBe("headshots/4046.png");
  });

  it("has an empty alt text, because the player name sits next to it", () => {
    expect(renderHeadshot(<Headshot src="headshots/4046.png" />).getAttribute("alt")).toBe("");
  });

  it("sets the width and the height from a size in pixels", () => {
    const img = renderHeadshot(<Headshot src="headshots/4046.png" size={88} />);
    expect(img.style.width).toBe("88px");
    expect(img.style.height).toBe("88px");
  });

  it("sets no inline size for a named size", () => {
    expect(renderHeadshot(<Headshot src="headshots/4046.png" size="avatar" />).getAttribute("style")).toBeNull();
  });

  it("loads lazy only when asked", () => {
    expect(renderHeadshot(<Headshot src="a.png" lazy />).getAttribute("loading")).toBe("lazy");
    cleanup();
    expect(renderHeadshot(<Headshot src="a.png" />).getAttribute("loading")).toBeNull();
  });

  it("swaps to the default headshot once after an error", () => {
    const img = renderHeadshot(<Headshot src="https://cdn.test/DEF.jpg" />);
    fireEvent.error(img);
    expect(img.getAttribute("src")).toBe(HEADSHOT_FALLBACK);
    fireEvent.error(img);
    expect(img.getAttribute("src")).toBe(HEADSHOT_FALLBACK);
  });
});

describe("headshotSrc", () => {
  it("reads the map by player id", () => {
    expect(headshotSrc({ "4046": "headshots/4046.png" }, "4046")).toBe("headshots/4046.png");
  });

  it("gives the default headshot for a player the map lacks", () => {
    expect(headshotSrc({}, "4046")).toBe(HEADSHOT_FALLBACK);
  });
});
