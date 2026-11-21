/**
 * A chapter of the week page in the look: a region named by its level 2 heading, with an optional mono note beside it.
 * The chapter rises in once as it enters the view, so the long scroll feels alive without a wait.
 * Use it when: one topic of a page in the look needs a chapter with a heading that the chapter rail links to.
 * Do not use it when: the section needs the brand black or no heading. Use `Chapter`.
 */
import type { ReactNode } from "react";
import { DURATION, RISE_EASE } from "@cpc/design/lib/motion";
import { Reveal } from "@cpc/design/parts/reveal";
import { stableId } from "@cpc/design/lib/stable-id";

export function WeekChapter({
  id,
  title,
  note,
  children,
}: {
  // The id that the chapter rail links to.
  id: string;
  title: string;
  // A short line beside the heading, such as "Tap for the recap" or "Line 99.6".
  note?: string;
  children: ReactNode;
}) {
  const heading = `${id}-heading`;
  return (
    <section id={id} aria-labelledby={heading}>
      <Reveal duration={DURATION.rise} ease={RISE_EASE} className="gap-sp-3 flex flex-col">
        <div className="gap-x-sp-3 gap-y-sp-1 flex flex-wrap items-baseline justify-between">
          <h2
            id={heading}
            className="text-stat m-0 leading-tight font-bold"
            {...stableId("heading", id)}
          >
            {title}
          </h2>
          {note !== undefined && (
            <span className="text-meta tracking-caps text-mute font-mono leading-tight uppercase">
              {note}
            </span>
          )}
        </div>
        {children}
      </Reveal>
    </section>
  );
}
