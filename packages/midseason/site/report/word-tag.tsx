/**
 * The tag of the report: a small mono caps word with no box and no fill, so a tag never takes over its row.
 * It is muted, or in the accent color for a bad sign, such as "Just bad" (decision ticket 15).
 */
import type { ReactNode } from "react";
import { cn } from "@cpc/design/lib/utils";

export type TagTone = "mute" | "accent";

/* data-tag holds the tone, so a test finds each tag of the report and reads its tone. */
export function WordTag({ children, tone = "mute", className }: { children: ReactNode; tone?: TagTone; className?: string }) {
  return (
    <span
      data-tag={tone}
      className={cn(
        "ml-sp-2 inline-block align-baseline font-mono text-label font-bold tracking-caps whitespace-nowrap uppercase",
        tone === "accent" ? "text-accent-ink" : "text-mute",
        className,
      )}
    >
      {children}
    </span>
  );
}
