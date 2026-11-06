/**
 * The teams row of the Stack: one slot for each side of the trade, with its avatar and its number, and the "+" slot.
 * A tap on a slot opens the team sheet for that side. A tap on "+" opens it for a new side.
 */
"use client";

import { PlusIcon } from "lucide-react";
import { Avatar } from "@cpc/league/avatar";
import { AVATAR_FALLBACK } from "@cpc/league/images";
import type { Team } from "../lib/api";
import { MAX_SIDES } from "../lib/trade";

/* One slot of the row: the title of the side, and its team once picked. */
export type Slot = { id: number; title: string; team: Team | undefined };

type TeamsRowProps = {
  slots: Slot[];
  onPickSlot: (index: number) => void;
  onAdd: () => void;
  // No teams yet, or a grade runs, so no slot takes a tap.
  locked: boolean;
};

/* The round face of a slot: 44px, so the slot is a full tap target. */
const FACE = "relative grid size-touch flex-none place-items-center rounded-full border-2";

export function TeamsRow({ slots, onPickSlot, onAdd, locked }: TeamsRowProps) {
  return (
    <ul aria-label="Teams in the trade" className="m-0 flex list-none flex-wrap items-start gap-sp-4 p-0">
      {slots.map((slot, index) => (
        <li key={slot.id}>
          <button
            type="button"
            disabled={locked}
            onClick={() => onPickSlot(index)}
            aria-label={slot.team ? `${slot.title}: ${slot.team.team}. Change the team` : `Pick ${slot.title}`}
            className="press flex cursor-pointer flex-col items-center gap-sp-1 rounded-card text-ink focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed"
          >
            <span className={`${FACE} ${slot.team ? "border-accent" : "border-dashed border-rule bg-card"}`}>
              {slot.team ? (
                <>
                  <Avatar src={slot.team.avatar ?? AVATAR_FALLBACK} className="size-full rounded-full bg-card object-cover" />
                  <span
                    aria-hidden="true"
                    className="absolute -right-sp-1 -bottom-sp-1 grid size-sp-5 place-items-center rounded-full bg-band font-mono text-meta font-bold text-on-dark"
                  >
                    {index + 1}
                  </span>
                </>
              ) : (
                <span className="font-mono text-meta font-bold text-mute">{index + 1}</span>
              )}
            </span>
            <span className="max-w-[6rem] truncate text-meta leading-tight font-bold">{slot.title}</span>
          </button>
        </li>
      ))}
      {slots.length < MAX_SIDES && (
        <li className="flex flex-col items-center gap-sp-1">
          <button
            type="button"
            disabled={locked}
            onClick={onAdd}
            aria-label="Add a team"
            className={`press ${FACE} cursor-pointer border-dashed border-rule bg-card text-ink hover:border-accent focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed`}
          >
            <PlusIcon aria-hidden="true" className="size-sp-5" />
          </button>
          <span className="font-mono text-meta leading-tight font-bold text-mute">
            {slots.length} of {MAX_SIDES}
          </span>
        </li>
      )}
    </ul>
  );
}
