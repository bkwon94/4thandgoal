/**
 * The pick of Your team on the sim page, for a visitor with no team kept: one button per team, by name.
 * The app keeps the pick in the browser, the same team as the home page.
 */
"use client";

import { cn } from "@cpc/design/lib/utils";
import type { WeekSim } from "../schema/sim-types";
import { CARD, PRESS, nameOf } from "./format";

export function TeamPick({ sim, onPick }: { sim: WeekSim; onPick: (id: number) => void }) {
  // The teams in the order of their names, so a manager finds a team as in a list of contacts.
  const ids = Object.keys(sim.pages)
    .map(Number)
    .sort((a, b) => nameOf(sim, a).localeCompare(nameOf(sim, b)));
  return (
    <div className="px-gutter pt-sp-4 pb-sp-6 tablet:px-0">
      <section className={cn(CARD, "w-full")} aria-labelledby="sim-pick-title">
        <h1 id="sim-pick-title" className="m-0 text-stat leading-tight font-bold text-balance">
          Pick your team
        </h1>
        {/* A sub line of the heading, so it is other text of the floor at 11px or more, not prose (ADR 0025). */}
        <div className="text-meta text-pretty text-mute">See what your team needs to make the playoffs.</div>
        <ul aria-label="Teams" className="m-0 grid list-none grid-cols-1 gap-x-sp-3 p-0 tablet:grid-cols-2">
          {ids.map((id) => (
            <li key={id} className="border-t border-rule">
              <button
                type="button"
                onClick={() => onPick(id)}
                className={cn(PRESS, "flex min-h-touch w-full items-center text-left text-body font-bold hover-fine:text-accent-ink")}
              >
                {nameOf(sim, id)}
              </button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
