/**
 * The page column: the shared shell that centers every page's content and spaces its chapters.
 * It renders the three-track grid from the tablet tier, an optional rail in the left track, and the main.
 */
import type { ReactNode } from "react";

/* One shell serves every page, because four copies of the same grid and main classes drift apart.
   From the tablet tier a three-track grid keeps the page column in the middle track, so it lines up with the masthead
   and the compact bar. The rail sits in the left margin track. On a phone the column fills the width, so no grid.
   From the tablet tier up the main turns clear and spaces the chapters, so each chapter reads as a card on the grey body.
   The main sets its full width. A grid item with auto margins shrinks to its content, and a short page would get a thin column. */
export function PageColumn({ rail, children }: { rail?: ReactNode; children: ReactNode }) {
  return (
    <div className="tablet:grid tablet:grid-cols-[minmax(0,1fr)_var(--container-page)_minmax(0,1fr)]">
      {rail}
      <main className="mx-auto w-full max-w-page bg-wht tablet:col-start-2 tablet:flex tablet:flex-col tablet:gap-card-gap tablet:bg-transparent">
        {children}
      </main>
    </div>
  );
}
