/**
 * Tests for the race group of a team, the group of the chips of the Index list.
 * They cover a clinched team, an eliminated team, the 75% edge of In, the 25% edge of Bubble, and a team with no odds.
 */
import { describe, expect, it } from "vitest";
import { raceGroup } from "./race-group";

describe("raceGroup", () => {
  it("puts a clinched team in In, whatever its odds", () => {
    expect(raceGroup({ playoff: 40, status: "in" })).toBe("in");
  });

  it("puts an eliminated team in Out, whatever its odds", () => {
    expect(raceGroup({ playoff: 60, status: "out" })).toBe("out");
  });

  it("puts odds of 75% in In, and odds of 74% in Bubble", () => {
    expect(raceGroup({ playoff: 75, status: "open" })).toBe("in");
    expect(raceGroup({ playoff: 74, status: "open" })).toBe("bubble");
  });

  it("puts odds of 25% in Bubble, and odds of 24% in Out", () => {
    expect(raceGroup({ playoff: 25, status: "open" })).toBe("bubble");
    expect(raceGroup({ playoff: 24, status: "open" })).toBe("out");
  });

  it("puts a team with no odds in no group", () => {
    expect(raceGroup(null)).toBeNull();
  });
});
