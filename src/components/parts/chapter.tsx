/**
 * A chapter of a page: the section that holds one topic, on the brand black or on white.
 * It ports the .chap rule of the source stylesheet. It can fade in once as a unit when it enters the view.
 */
import type { ReactNode } from "react";
import { Reveal } from "@/components/parts/reveal";
import { cn } from "@/lib/utils";

/* A dark chapter sits on the brand black. Its label and blurb take the dark prop for their on-dark colors.
   A chapter with reveal fades and rises in once as a unit, when it enters the view. A chapter with its own
   card stagger or hero motion leaves reveal off, so no element sits inside two reveals.
   On every page, from the tablet tier up, a chapter is a card on the grey body.
   The page column's main sets the gap, so the chapter drops its rule and takes the white of the page itself.
   The edge stays square, as the print is. */
export function Chapter({
  dark,
  id,
  reveal,
  children,
}: {
  dark?: boolean;
  id?: string;
  reveal?: boolean;
  children: ReactNode;
}) {
  const section = (
    <section
      id={id}
      className={cn(
        "border-b-(length:--chap-rule) border-gry px-gutter py-sp-5 tablet:border-b-0",
        dark ? "bg-card-blk text-on-dark" : "tablet:bg-wht",
      )}
    >
      {children}
    </section>
  );
  return reveal ? <Reveal>{section}</Reveal> : section;
}
