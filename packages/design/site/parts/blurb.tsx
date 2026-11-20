/**
 * The blurb: a short paragraph of prose under a chapter label or a grid of cards. It ports the .blurb rule of the source stylesheet.
 * Its measure caps the line, so prose stays readable on a wide column.
 * Use it when: a short paragraph sits under a chapter label or a grid of cards.
 * Do not use it when: the text needs a surface of its own. Use `Card`.
 */
import type { ReactNode } from "react";
import { cn } from "../lib/utils";
import { textId } from "../lib/stable-id";

/* A blurb under a grid of cards passes mt-sp-3 for the space above it. The measure caps the line, so prose stays readable on a wide column.
   A blurb is prose, so it takes the lead size: 16px or more at each tier.
   A blurb of plain text carries a stable id from its text, so the egg hunt can name a word in it. */
export function Blurb({
  children,
  dark,
  className,
}: {
  children: ReactNode;
  dark?: boolean;
  className?: string;
}) {
  const id = typeof children === "string" ? textId("blurb", children) : {};
  return (
    <p
      className={cn(
        "max-w-measure text-lead m-0",
        dark ? "text-on-dark-2" : "text-ink-2",
        className,
      )}
      {...id}
    >
      {children}
    </p>
  );
}
