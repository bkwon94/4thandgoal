/**
 * The red uppercase label that opens a chapter or a card. It ports the .lbl rule of the source stylesheet.
 * It is a level 2 heading when it opens a chapter.
 */
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/* The red uppercase label that opens a chapter or a card. A label inside a card passes mb-sp-1 to sit close to its content.
   A chapter's own label passes heading, so it is a level 2 heading and a screen reader can jump from chapter to chapter.
   The base styles reset a heading's size, weight, and margin, so the heading looks the same as the plain label. */
export function Label({
  children,
  dark,
  heading,
  className,
}: {
  children: ReactNode;
  dark?: boolean;
  heading?: boolean;
  className?: string;
}) {
  const Element = heading ? "h2" : "div";
  return (
    <Element
      className={cn(
        "text-label leading-tight font-bold tracking-wide uppercase",
        "mb-sp-3",
        dark ? "text-red-lt" : "text-red-ink",
        className,
      )}
    >
      {children}
    </Element>
  );
}
