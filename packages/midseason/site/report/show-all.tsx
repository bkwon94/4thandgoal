/**
 * A long list of the report: its first 5 rows, then a "Show all" control that opens the rest (PRD, "Long lists").
 * It is a client component, because the open list is state. A list of 5 rows or fewer shows no control.
 */
"use client";

import { Button } from "@cpc/design/ui/button";
import { useState, type ReactNode } from "react";
import { cn } from "@cpc/design/lib/utils";
import { openId } from "@cpc/design/lib/stable-id";

/* The rows that a long list shows before the reader opens it. */
export const FIRST_ROWS = 5;

export function ShowAll({
  label,
  rows,
  className,
}: {
  label: string;
  rows: ReactNode[];
  className?: string;
}) {
  const [open, setOpen] = useState(false);
  const long = rows.length > FIRST_ROWS;
  return (
    <div className="gap-sp-2 flex flex-col">
      <ol aria-label={label} className={cn("m-0 list-none p-0", className)}>
        {open || !long ? rows : rows.slice(0, FIRST_ROWS)}
      </ol>
      {/* A mono text control with a chevron and no border (decision ticket 15). The chevron turns by a CSS transition,
          so the reduced-motion rule of globals.css stops the turn. */}
      {long && (
        <Button
          variant="plain"
          type="button"
          aria-expanded={open}
          onClick={() => setOpen(!open)}
          {...openId("show-all", label)}
          className="press min-h-touch gap-sp-2 text-meta tracking-caps text-accent-ink flex cursor-pointer items-center self-start bg-transparent p-0 font-mono font-bold"
        >
          {open ? `Show top ${FIRST_ROWS}` : `Show all ${rows.length}`}
          <svg
            aria-hidden="true"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={2.5}
            className={cn(
              "size-sp-4 ease-rise transition-transform duration-300",
              open && "rotate-180",
            )}
          >
            <path d="M6 9l6 6 6-6" />
          </svg>
        </Button>
      )}
    </div>
  );
}
