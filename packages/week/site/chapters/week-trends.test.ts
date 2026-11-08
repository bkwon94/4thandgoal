/**
 * Tests for the two week series of the Trend tiles: the top score and the median of each week, from week 1 to the page week.
 * They read the real managers files of CPC, which has a published median, and of NorCal, which has none.
 */
import { describe, expect, it } from "vitest";
import cpcJson from "../../../../clients/cpc/published/2026/managers.json";
import norcalJson from "../../../../clients/norcal/published/2026/managers.json";
import norcalWeek8Json from "../../../../clients/norcal/published/2026/week-08/page.json";
import { weekPageSchema } from "../schema/week";
import { medianOf, trendText, weekTrends } from "./week-trends";

const cpcWeeks = cpcJson.managers.map((manager) => manager.weeks);
const norcalWeeks = norcalJson.managers.map((manager) => manager.weeks);
const values = (series: { value: number }[]) => series.map((point) => point.value);

describe("weekTrends", () => {
  it("gives the top score of each week from week 1 to the page week", () => {
    const trends = weekTrends(cpcWeeks, 8);
    expect(values(trends.top)).toEqual([156.92, 156.52, 140.6, 145.63, 158.96, 126.79, 148.13, 134.1]);
    expect(trends.top.map((point) => point.week)).toEqual([1, 2, 3, 4, 5, 6, 7, 8]);
  });

  it("stops each series at the page week, so an older week shows no later week", () => {
    const trends = weekTrends(cpcWeeks, 6);
    expect(values(trends.top)).toEqual([156.92, 156.52, 140.6, 145.63, 158.96, 126.79]);
    expect(trends.median).toHaveLength(6);
  });

  it("takes the published median of each week when the league has a median game", () => {
    const trends = weekTrends(cpcWeeks, 8);
    expect(values(trends.median)).toEqual([111.36, 96.34, 107.14, 104.58, 107.35, 106.83, 103.87, 99.6]);
  });

  it("takes the median of the points of every team when the league has no median game", () => {
    const trends = weekTrends(norcalWeeks, 8);
    const week8 = weekPageSchema.parse(norcalWeek8Json);
    const scores = week8.matchups.flatMap((matchup) => matchup.sides.map((side) => side.score));
    // The trend of the page week equals the number on the Median tile, which the week page takes from the scores.
    expect(trends.median.at(-1)?.value).toBe(medianOf(scores));
    expect(trends.median).toHaveLength(8);
  });
});

describe("medianOf", () => {
  it("rounds the middle pair of an even count in whole cents", () => {
    expect(medianOf([100.31, 98.88, 50, 150])).toBe(99.6);
  });
});

describe("trendText", () => {
  const top = weekTrends(cpcWeeks, 8).top;

  it("compares the page week to the week before it", () => {
    expect(trendText(top, 8)).toBe("Down from 148.13 in week 7.");
    expect(trendText(top, 7)).toBe("Up from 126.79 in week 6.");
  });

  it("names the high and the low of the season so far", () => {
    expect(trendText(top, 5)).toBe("The highest of the season so far.");
    expect(trendText(top, 6)).toBe("The lowest of the season so far.");
  });

  it("names the first week of the season", () => {
    expect(trendText(top, 1)).toBe("The first week of the season.");
  });
});
