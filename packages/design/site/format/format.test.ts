/**
 * Tests for the week page formats. The examples come from the pipeline's fmt filter,
 * so the React page prints the same numbers as the old page.
 */
import { describe, expect, it } from "vitest";
import { count, gap, num, oneDecimal, record, shortName, thousands } from "./format";

describe("num", () => {
  it("drops trailing zeros", () => {
    expect(num(106.8)).toBe("106.8");
    expect(num(21.0)).toBe("21");
    expect(num(114.95)).toBe("114.95");
  });

  it("rounds to two decimals", () => {
    expect(num(20.199999)).toBe("20.2");
    expect(num(-0.85)).toBe("-0.85");
  });
});

describe("gap", () => {
  it("puts a plus on a gain and a true minus on a loss", () => {
    expect(gap(2.79)).toBe("+2.79");
    expect(gap(-2.79)).toBe("−2.79");
    expect(gap(0)).toBe("+0");
  });
});

describe("shortName", () => {
  it("keeps the first initial and the rest", () => {
    expect(shortName("Christian McCaffrey")).toBe("C. McCaffrey");
    expect(shortName("Amon-Ra St. Brown")).toBe("A. St. Brown");
  });

  it("keeps a one-word name whole", () => {
    expect(shortName("Steelers")).toBe("Steelers");
  });
});

describe("thousands", () => {
  it("puts a comma between each group of three digits", () => {
    expect(thousands(48213)).toBe("48,213");
    expect(thousands(1250000)).toBe("1,250,000");
    expect(thousands(640)).toBe("640");
  });
});

describe("record", () => {
  it("joins the wins and the losses with a hyphen", () => {
    expect(record(5, 2)).toBe("5-2");
    expect(record(0, 14)).toBe("0-14");
  });
});

describe("oneDecimal", () => {
  it("keeps one decimal, with a zero when the value is whole", () => {
    expect(oneDecimal(26.3)).toBe("26.3");
    expect(oneDecimal(21)).toBe("21.0");
  });

  it("rounds before toFixed, so 15.85 gives 15.9", () => {
    expect(oneDecimal(15.85)).toBe("15.9");
  });
});

describe("count", () => {
  it("uses the singular form for one", () => {
    expect(count(1, "win", "wins")).toBe("1 win");
  });

  it("uses the plural form for zero and for many", () => {
    expect(count(0, "loss", "losses")).toBe("0 losses");
    expect(count(4, "loss", "losses")).toBe("4 losses");
  });
});
