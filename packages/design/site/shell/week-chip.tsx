/**
 * The week chip of the top band, "WK 08", and the strip of the weeks of the season that a tap on it opens.
 * The chip week has the brand edge, and a tap on a week opens its page.
 */
"use client";

import { ChevronDownIcon } from "lucide-react";
import { useEffect, useRef } from "react";
import { weekChipLabel, type WeekLink } from "./nav";

type WeekChipProps = {
  // The published weeks, newest first.
  weeks: WeekLink[];
  // The week the chip names: the week of the open page, else the latest week.
  week: WeekLink;
  // The href of the open page.
  pageHref?: string;
};

/* A details element holds the strip, so the chip opens and closes with scripts off too.
   The script only adds a close on Escape and on a tap outside, as a reader expects of a panel. */
export function WeekChip({ weeks, week, pageHref }: WeekChipProps) {
  const ref = useRef<HTMLDetailsElement>(null);

  useEffect(() => {
    const close = (focus: boolean) => {
      const details = ref.current;
      if (!details?.open) return;
      details.open = false;
      if (focus) details.querySelector("summary")?.focus();
    };
    const onPointer = (event: PointerEvent) => {
      if (event.target instanceof Node && !ref.current?.contains(event.target)) close(false);
    };
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") close(true);
    };
    document.addEventListener("pointerdown", onPointer);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onPointer);
      document.removeEventListener("keydown", onKey);
    };
  }, []);

  // The strip reads left to right in time, so the oldest week comes first and the latest week sits at the right end.
  const strip = [...weeks].reverse();
  return (
    <details ref={ref} className="group">
      <summary className="press flex min-h-touch cursor-pointer list-none items-center gap-sp-1 rounded-pill border border-rule bg-card px-sp-4 font-mono text-meta font-bold tracking-caps text-ink [&::-webkit-details-marker]:hidden">
        {weekChipLabel(week.number)}
        <ChevronDownIcon aria-hidden className="size-sp-4 group-open:rotate-180" />
      </summary>
      {/* The strip hangs from the bottom of the top band, across its full width. The top band is sticky, so it is the box of the strip. */}
      <div className="absolute inset-x-0 top-full border-b border-rule bg-page">
        <nav aria-label="Weeks of the season" className="mx-auto flex max-w-band gap-sp-2 overflow-x-auto px-gutter py-sp-3">
          {strip.map((link) => {
            const marked = link.href === week.href;
            return (
              // The brand edge marks the chip week. The open page takes "page", and the chip week on another page takes "true".
              <a
                key={link.href}
                href={link.href}
                aria-current={link.href === pageHref ? "page" : marked ? "true" : undefined}
                className={`press flex min-h-touch min-w-touch flex-none items-center justify-center rounded-pill border-2 bg-card px-sp-4 font-mono text-meta font-bold tracking-caps text-ink no-underline ${marked ? "border-accent" : "border-rule"}`}
              >
                {weekChipLabel(link.number)}
              </a>
            );
          })}
        </nav>
      </div>
    </details>
  );
}
