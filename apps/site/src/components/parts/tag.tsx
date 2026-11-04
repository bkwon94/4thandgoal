/**
 * The small red tag that follows a label. It ports the .tag rule of the source stylesheet.
 * It sits to the right of the label or on its own line.
 */
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/* A tag after a label sits to its right. A tag on its own line passes ml-0 and its own top margin. */
export function Tag({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <span
      className={cn(
        "ml-sp-2 inline-block rounded-sm bg-accent px-sp-2 py-sp-0 align-middle text-label font-bold tracking-caps text-on-dark uppercase",
        className,
      )}
    >
      {children}
    </span>
  );
}
