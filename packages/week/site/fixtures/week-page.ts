/**
 * The week 6 and week 8 page JSON of CPC as typed fixtures for the section tests.
 * The tests read the real published file, so a change to the JSON shape breaks them.
 * Blurb tests read their text from the fixture, never as a literal, since the pipeline rewrites blurbs.
 */
import json from "../../../../clients/cpc/published/2026/week-06/page.json";
import week8Json from "../../../../clients/cpc/published/2026/week-08/page.json";
import { weekPageSchema } from "../schema/week";

/* The parse runs at import, so a stale fixture fails at once. */
export const week6 = weekPageSchema.parse(json);
/* Week 8 is the week of the acceptance tests of the redesign, such as the recap of The Blue Tent and London Cooking. */
export const week8 = weekPageSchema.parse(week8Json);

/* The first sentence of a blurb, for a test that finds the blurb on the page with a substring match. */
export function firstSentence(text: string | null | undefined): string {
  if (!text) throw new Error("The fixture has no text for this blurb.");
  return text.split(". ")[0];
}
