/**
 * A chapter of the midseason report: a region named by its level 3 heading, the part of the chapter, then its prose.
 * Each act holds its chapters, so the act title is the level 2 heading and each chapter sits one level under it.
 * A part of Quick hits sits one level under Quick hits, so it takes a level 4 heading.
 */
import type { ReactNode } from "react";
import { DURATION, RISE_EASE } from "@cpc/design/lib/motion";
import { Reveal } from "@cpc/design/parts/reveal";
import type { Blurb } from "../schema/midseason-types";
import { ChapterProse } from "./chapter-prose";
import { stableId } from "@cpc/design/lib/stable-id";

export function ReportChapter({
  id,
  title,
  note,
  level = 3,
  blurb = null,
  children,
}: {
  // The id of the chapter, from its key, so a link can jump to it.
  id: string;
  title: string;
  // A short line beside the heading, such as "Weeks 1 to 8".
  note?: string;
  // The level of the heading: 3 for a chapter of an act, 4 for a part of Quick hits.
  level?: 3 | 4;
  blurb?: Blurb | null;
  children?: ReactNode;
}) {
  const heading = `${id}-heading`;
  const Heading = level === 3 ? "h3" : "h4";
  return (
    <section id={id} aria-labelledby={heading}>
      <Reveal duration={DURATION.rise} ease={RISE_EASE} className="flex flex-col gap-sp-3">
        <div className="flex flex-wrap items-baseline justify-between gap-x-sp-3 gap-y-sp-1">
          <Heading
            id={heading}
            className={`m-0 leading-tight font-bold ${level === 3 ? "text-stat" : "text-lead"}`}
            {...stableId("heading", id)}
          >
            {title}
          </Heading>
          {note !== undefined && (
            <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">{note}</span>
          )}
        </div>
        {children}
        <ChapterProse blurb={blurb} />
      </Reveal>
    </section>
  );
}
