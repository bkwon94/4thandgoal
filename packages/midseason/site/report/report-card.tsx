/**
 * The card of the midseason report: the card of the shared look with the 8px corners of the report.
 * Each chapter takes its card from here, so no card of the report keeps the 20px radius (decision ticket 15).
 */
import type { ComponentProps } from "react";
import { cn } from "@cpc/design/lib/utils";
import { Card as LookCard } from "@cpc/design/parts/card";

export function ReportCard({ className, ...props }: ComponentProps<typeof LookCard>) {
  return <LookCard {...props} className={cn("rounded-report", className)} />;
}
