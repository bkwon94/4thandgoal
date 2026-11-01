/**
 * The blurb: a short paragraph of prose under a chapter label or a grid of cards.
 * Its measure caps the line, so prose stays readable on a wide column.
 */
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/* A blurb under a grid of cards passes mt-sp-3 for the space above it. The measure caps the line, so prose stays readable on a wide column. */
export function Blurb({ children, dark, className }: { children: ReactNode; dark?: boolean; className?: string }) {
  return <p className={cn("m-0 max-w-measure text-body", dark ? "text-on-dark-2" : "text-ink-2", className)}>{children}</p>;
}
