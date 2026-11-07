/**
 * Tests for the stable id of an element: it derives from the data that the element renders, and two renders of the
 * same data give the same id.
 */
import { describe, expect, it } from "vitest";
import { stableId, textId } from "./stable-id";

describe("stableId", () => {
  it("joins the parts of the data in lower case with a dash", () => {
    expect(stableId("luck", 3)).toEqual({ "data-stable-id": "luck-3" });
    expect(stableId("week", 8, "award", "Top Score")).toEqual({ "data-stable-id": "week-8-award-top-score" });
  });

  it("drops each mark that is not a letter or a digit, so an id has only letters, digits, and dashes", () => {
    expect(stableId("heading", "What Comes Next?")["data-stable-id"]).toBe("heading-what-comes-next");
    expect(stableId("row", "D/ST", 10)["data-stable-id"]).toBe("row-d-st-10");
  });
});

describe("textId", () => {
  it("derives one short id from the text, so two renders of one blurb give one id and two blurbs give two", () => {
    const one = textId("blurb", "Lil Fridge got lucky.");
    expect(one).toEqual(textId("blurb", "Lil Fridge got lucky."));
    expect(one["data-stable-id"]).toMatch(/^blurb-[a-z0-9]{1,7}$/);
    expect(one).not.toEqual(textId("blurb", "Teehee got lucky."));
  });
});
