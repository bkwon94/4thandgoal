/**
 * One row of a home page chapter: a plain anchor with the press motion and the rule under it.
 * The home section of each package renders its rows with it, so every row of the home page looks the same.
 */
import type { ReactNode } from "react";
import { cn } from "@cpc/design/lib/utils";

/* A plain anchor, like the masthead link. An anchor skips the router, so the caller passes an href with the base path. */
export function HomeRow({ href, first, children }: { href: string; first?: boolean; children: ReactNode }) {
  return (
    <a
      href={href}
      className={cn(
        "press group block border-b border-rule py-sp-3 text-inherit no-underline",
        // The label already gives the first row its top space.
        first && "pt-0",
      )}
    >
      {children}
    </a>
  );
}
