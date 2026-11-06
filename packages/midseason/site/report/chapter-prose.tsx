/**
 * The prose of a chapter: the blurb of the writer as one paragraph, in the voice of the roast setting of the client.
 * A chapter with no blurb shows no prose.
 */
import { Blurb as BlurbText } from "@cpc/design/parts/blurb";
import type { Blurb } from "../schema/midseason-types";

/* The sentences of a blurb as one paragraph. */
export const blurbText = (blurb: Blurb) => blurb.sentences.map((sentence) => sentence.text).join(" ");

export function ChapterProse({ blurb, dark }: { blurb: Blurb | null; dark?: boolean }) {
  if (blurb === null) return null;
  return <BlurbText dark={dark}>{blurbText(blurb)}</BlurbText>;
}
