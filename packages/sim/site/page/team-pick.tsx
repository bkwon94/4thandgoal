/**
 * The pick of Your team on the sim page, for a visitor with no team kept: one button per team, by name.
 * The app keeps the pick in the browser, the same team as the home page.
 */
"use client";

import { Button } from "@cpc/design/ui/button";
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
        <h1 id="sim-pick-title" className="text-stat m-0 leading-tight font-bold text-balance">
          Pick your team
        </h1>
        {/* A sub line of the heading, so it is other text of the floor at 11px or more, not prose (ADR 0025). */}
        <div className="text-meta text-mute text-pretty">
          See what your team needs to make the playoffs.
        </div>
        <ul
          aria-label="Teams"
          className="gap-x-sp-3 tablet:grid-cols-2 m-0 grid list-none grid-cols-1 p-0"
        >
          {ids.map((id) => (
            <li key={id} className="border-rule border-t">
              <Button
                variant="plain"
                type="button"
                onClick={() => onPick(id)}
                className={cn(
                  PRESS,
                  "min-h-touch text-body hover-fine:text-accent-ink flex w-full items-center text-left font-bold",
                )}
              >
                {nameOf(sim, id)}
              </Button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
