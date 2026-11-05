/**
 * The chapter rail: the list of the weekly report's chapters beside the page column from the rail tier.
 * It is the client island of the week page. It links each chapter by its id and marks the chapter in view.
 */
"use client";

import { useEffect, useRef, useState } from "react";
import { cn } from "../lib/utils";

export type RailChapter = { id: string; label: string };

/* The band that counts as the top of the viewport, as a share of the viewport height from its top edge.
   A chapter in the band is in view. The first such chapter in the report's order is the one nearest the top. */
const BAND = 0.3;

/* The band starts this far under the top band. A chapter that only touches its lower edge after a jump stays out. */
const BAND_INSET = 8;

/* The observer margin for the band: the top band at the top, the rest of the viewport under the band at the bottom.
   The height of the top band comes from the scroll padding on html, so the rail and the top band share one value. */
function bandMargin(): string {
  const bar = Number.parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 0;
  return `-${bar + BAND_INSET}px 0px -${(1 - BAND) * 100}% 0px`;
}

export function ChapterRail({ chapters }: { chapters: RailChapter[] }) {
  const [current, setCurrent] = useState<string | null>(null);
  // The ids of the chapters in the band now. A ref, because only the first of them is state the reader sees.
  const inBand = useRef(new Set<string>());

  useEffect(() => {
    if (typeof IntersectionObserver === "undefined") return;
    const band = inBand.current;
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) band.add(entry.target.id);
          else band.delete(entry.target.id);
        }
        // With no chapter in the band, such as at the masthead, the last mark stays, so the rail never goes blank.
        const first = chapters.find(({ id }) => band.has(id));
        if (first) setCurrent(first.id);
      },
      { rootMargin: bandMargin() },
    );
    for (const { id } of chapters) {
      const chapter = document.getElementById(id);
      if (chapter) observer.observe(chapter);
    }
    return () => {
      observer.disconnect();
      band.clear();
    };
  }, [chapters]);

  return (
    // The rail renders at every tier, so the static HTML is the same for each. The rail variant shows it once the margin holds it.
    // It sits at the end of the left margin track with the gap before the column. The rail is sticky under the top band, so it stays in view as the reader scrolls.
    // From the rail tier the top band is one row: a 44px row, 8px above and below, and its 1px rule at the bottom.
    <nav
      aria-label="Chapters"
      className="sticky top-[calc(var(--spacing-touch)+2*var(--spacing-sp-2)+1px)] col-start-1 row-start-1 mr-rail-gap hidden w-rail self-start justify-self-end py-sp-5 rail:block"
    >
      <ul className="m-0 list-none p-0">
        {chapters.map(({ id, label }) => (
          <li key={id}>
            {/* A plain fragment anchor jumps with scripts off. The scroll padding on html keeps the chapter clear of the top band.
                No smooth scroll is set, so the jump is instant with motion on or off.
                The mark is "location", the ARIA value for the reader's place in the page. "page" is for a link to the page in view.
                Each link is 44px tall, the tap floor of the readability check, because the links stack with no space between them. */}
            <a
              href={`#${id}`}
              aria-current={current === id ? "location" : undefined}
              className={cn(
                "flex min-h-touch items-center py-sp-1 text-label leading-tight font-bold tracking-wide uppercase transition-colors",
                current === id ? "text-accent-ink" : "text-mute hover-fine:text-ink",
              )}
            >
              {label}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
