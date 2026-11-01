/**
 * The week 6 page JSON as a typed fixture for the section tests.
 * The tests read the real published file, so a change to the JSON shape breaks them.
 * Blurb tests read their text from the fixture, never as a literal, since the pipeline rewrites blurbs.
 */
import json from "../../public/2026/week-06/page.json";
import { weekPageSchema } from "@/lib/schemas/week";

export const week6 = weekPageSchema.parse(json);

/* The first sentence of a blurb, for a test that finds the blurb on the page with a substring match. */
export function firstSentence(text: string | null | undefined): string {
  if (!text) throw new Error("The fixture has no text for this blurb.");
  return text.split(". ")[0];
}
