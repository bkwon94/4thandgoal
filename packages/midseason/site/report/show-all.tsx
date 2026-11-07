/**
 * A long list of the report: its first 5 rows, then a "Show all" control that opens the rest (PRD, "Long lists").
 * It is a client component, because the open list is state. A list of 5 rows or fewer shows no control.
 */
"use client";

import { useState, type ReactNode } from "react";
import { cn } from "@cpc/design/lib/utils";
import { openId } from "@cpc/design/lib/stable-id";

/* The rows that a long list shows before the reader opens it. */
export const FIRST_ROWS = 5;

export function ShowAll({ label, rows, className }: { label: string; rows: ReactNode[]; className?: string }) {
  const [open, setOpen] = useState(false);
  const long = rows.length > FIRST_ROWS;
  return (
    <div className="flex flex-col gap-sp-2">
      <ol aria-label={label} className={cn("m-0 list-none p-0", className)}>
        {open || !long ? rows : rows.slice(0, FIRST_ROWS)}
      </ol>
      {/* A mono text control with a chevron and no border (decision ticket 15). The chevron turns by a CSS transition,
          so the reduced-motion rule of globals.css stops the turn. */}
      {long && (
        <button
          type="button"
          aria-expanded={open}
          onClick={() => setOpen(!open)}
          {...openId("show-all", label)}
          className="press flex min-h-touch cursor-pointer items-center gap-sp-2 self-start bg-transparent p-0 font-mono text-meta font-bold tracking-caps text-accent-ink"
        >
          {open ? `Show top ${FIRST_ROWS}` : `Show all ${rows.length}`}
          <svg
            aria-hidden="true"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={2.5}
            className={cn("size-sp-4 transition-transform duration-300 ease-rise", open && "rotate-180")}
          >
            <path d="M6 9l6 6 6-6" />
          </svg>
        </button>
      )}
    </div>
  );
}
