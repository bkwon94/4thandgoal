/**
 * Tests for the name of a personal Topic in the Thread: the typed question, else the Topic name, with the team after
 * it when it is not Your team.
 */
import { describe, expect, it } from "vitest";
import { personalName } from "./thread";

describe("personalName", () => {
  it("gives a typed question as is, and a tapped Topic its name with the team after it when it is not Your team", () => {
    expect(personalName({ key: "weak_spots", question: null }, "Bo Girds")).toBe("Weak spots: Bo Girds");
    expect(personalName({ key: "weak_spots", question: null }, undefined)).toBe("Weak spots");
    expect(personalName({ key: "weak_spots", question: "where am I weak" }, "Bo Girds")).toBe("where am I weak");
  });
});
