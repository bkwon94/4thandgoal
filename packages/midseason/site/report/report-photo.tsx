/**
 * The photo of the midseason report: the photo frame of the shared look, a headshot or a team avatar, with the 8px
 * corners of the report in place of the round frame, so the report has no full round corner (decision ticket 15).
 */
import type { ComponentProps } from "react";
import { cn } from "@cpc/design/lib/utils";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";

/* The frame has a fixed size and lazy loads its image, so a photo never moves the layout. */
export function ReportPhoto({ className, ...props }: ComponentProps<typeof PhotoFrame>) {
  return <PhotoFrame {...props} className={cn("rounded-report", className)} />;
}
