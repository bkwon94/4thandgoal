/**
 * One chapter of the home page: a region named by its level 2 heading, with an optional mono note beside the heading.
 * The home part of each package renders its chapter with it, so every chapter of the home page looks the same.
 */
import type { ReactNode } from "react";
import { DURATION, RISE_EASE } from "@cpc/design/lib/motion";
import { Reveal } from "@cpc/design/parts/reveal";

export function HomeChapter({
  id,
  title,
  note,
  children,
}: {
  // The id of the region. The heading id comes from it.
  id: string;
  title: string;
  // A short line beside the heading, such as "Playoff odds" or "3 weeks".
  note?: string;
  children: ReactNode;
}) {
  const heading = `${id}-heading`;
  return (
    <section id={id} aria-labelledby={heading}>
      {/* The chapter rises in once as it enters the view, as a chapter of the week page does. */}
      <Reveal duration={DURATION.rise} ease={RISE_EASE} className="gap-sp-3 flex flex-col">
        <div className="gap-x-sp-3 gap-y-sp-1 flex flex-wrap items-baseline justify-between">
          <h2 id={heading} className="text-stat m-0 leading-tight font-bold">
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
