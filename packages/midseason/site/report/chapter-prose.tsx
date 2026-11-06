/**
 * The prose of a chapter or of the opener: the blurb of the writer, then the roast under its own tag.
 * Each blurb is one paragraph of its sentences. A chapter with no blurb and no roast shows no prose.
 */
import { Blurb as BlurbText } from "@cpc/design/parts/blurb";
import type { Blurb } from "../schema/midseason-types";

/* The sentences of a blurb as one paragraph. */
export const blurbText = (blurb: Blurb) => blurb.sentences.map((sentence) => sentence.text).join(" ");

export function ChapterProse({ blurb, roast, dark }: { blurb: Blurb | null; roast: Blurb | null; dark?: boolean }) {
  if (blurb === null && roast === null) return null;
  return (
    <div className="flex flex-col gap-sp-3">
      {blurb !== null && <BlurbText dark={dark}>{blurbText(blurb)}</BlurbText>}
      {roast !== null && (
        <div className="flex flex-col gap-sp-1">
          <span className={`font-mono text-meta leading-tight font-bold tracking-caps uppercase ${dark ? "text-accent-text" : "text-accent-ink"}`}>
            The roast
          </span>
          <BlurbText dark={dark}>{blurbText(roast)}</BlurbText>
        </div>
      )}
    </div>
  );
}
