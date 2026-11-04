/**
 * Tests for the Avatar part: the src, the empty alt text, a size in pixels, and the swap to the default avatar.
 * Tests for avatarSrc: the map of the week by roster id, and the default avatar at the site root.
 * They read only the attributes of the image, never a class name.
 */
import { cleanup, fireEvent, render } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { AVATAR_FALLBACK, Avatar, avatarSrc } from "./avatar";

function renderAvatar(element: React.ReactElement) {
  const { container } = render(element);
  return container.querySelector("img") as HTMLImageElement;
}

afterEach(cleanup);

describe("Avatar", () => {
  it("renders the src it gets", () => {
    expect(renderAvatar(<Avatar src="avatars/1.png" />).getAttribute("src")).toBe("avatars/1.png");
  });

  it("has an empty alt text, because the team name sits next to it", () => {
    expect(renderAvatar(<Avatar src="avatars/1.png" />).getAttribute("alt")).toBe("");
  });

  it("sets the width and the height from a size in pixels", () => {
    const img = renderAvatar(<Avatar src="avatars/1.png" size={64} />);
    expect(img.style.width).toBe("64px");
    expect(img.style.height).toBe("64px");
  });

  it("sets no inline size for a named size", () => {
    expect(renderAvatar(<Avatar src="avatars/1.png" size="headshot" />).getAttribute("style")).toBeNull();
  });

  it("swaps to the default avatar once after an error", () => {
    const img = renderAvatar(<Avatar src="avatars/1.png" />);
    fireEvent.error(img);
    expect(img.getAttribute("src")).toBe(AVATAR_FALLBACK);
    fireEvent.error(img);
    expect(img.getAttribute("src")).toBe(AVATAR_FALLBACK);
  });
});

describe("avatarSrc", () => {
  it("reads the map by roster id", () => {
    expect(avatarSrc({ "4": "avatars/4.png" }, 4)).toBe("avatars/4.png");
  });

  it("gives the default avatar at the site root for a roster the map lacks", () => {
    expect(avatarSrc({}, 4)).toBe("/images/avatar-default.svg");
    expect(AVATAR_FALLBACK).toBe("/images/avatar-default.svg");
  });
});
