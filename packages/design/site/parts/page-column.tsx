/**
 * The page column: the shared shell that centers every page's content and spaces its chapters.
 * It renders the three-track grid from the tablet tier, an optional rail in the left track, and the main.
 */
import type { ReactNode } from "react";
import { cn } from "../lib/utils";

/* One shell serves every page, because four copies of the same grid and main classes drift apart.
   From the tablet tier a three-track grid keeps the page column in the middle track, so it lines up under the top band. The rail sits in the left margin track. On a phone the column fills the width, so no grid.
   From the tablet tier up the main turns clear and spaces the chapters, so each chapter reads as a card on the grey body.
   The main sets its full width. A grid item with auto margins shrinks to its content, and a short page would get a thin column. */
/* A wide page, such as the managers index with its stage, takes the width of the top band from the desktop tier, less a
   gutter on each side, so two columns fit side by side. The grid track sets the width, so the main drops its cap there. */
export function PageColumn({ rail, wide = false, children }: { rail?: ReactNode; wide?: boolean; children: ReactNode }) {
  return (
    <div
      className={cn(
        "tablet:grid tablet:grid-cols-[minmax(0,1fr)_var(--container-page)_minmax(0,1fr)]",
        wide && "desktop:[--container-page:min(var(--container-band),100%_-_2*var(--spacing-gutter))]",
      )}
    >
      {rail}
      <main
        className={cn(
          "mx-auto w-full max-w-page bg-page tablet:col-start-2 tablet:flex tablet:flex-col tablet:gap-card-gap tablet:bg-transparent",
          wide && "desktop:max-w-none",
        )}
      >
        {children}
      </main>
    </div>
  );
}
