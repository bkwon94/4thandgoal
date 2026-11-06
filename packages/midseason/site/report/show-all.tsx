/**
 * A long list of the report: its first 5 rows, then a "Show all" button that opens the rest (PRD, "Long lists").
 * It is a client component, because the open list is state. A list of 5 rows or fewer shows no button.
 */
"use client";

import { useState, type ReactNode } from "react";
import { cn } from "@cpc/design/lib/utils";

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
      {long && (
        <button
          type="button"
          aria-expanded={open}
          onClick={() => setOpen(!open)}
          className="press min-h-touch cursor-pointer self-start rounded-pill border border-rule bg-transparent px-sp-4 font-mono text-meta font-bold text-ink-2"
        >
          {open ? "Show fewer" : `Show all ${rows.length}`}
        </button>
      )}
    </div>
  );
}
