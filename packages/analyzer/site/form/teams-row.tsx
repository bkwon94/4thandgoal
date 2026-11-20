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
    <ul
      aria-label="Teams in the trade"
      className="gap-sp-4 m-0 flex list-none flex-wrap items-start p-0"
    >
      {slots.map((slot, index) => (
        <li key={slot.id}>
          <button
            type="button"
            disabled={locked}
            onClick={() => onPickSlot(index)}
            aria-label={
              slot.team ? `${slot.title}: ${slot.team.team}. Change the team` : `Pick ${slot.title}`
            }
            className="press gap-sp-1 rounded-card text-ink focus-visible:outline-accent flex cursor-pointer flex-col items-center focus-visible:outline-2 focus-visible:outline-offset-2 disabled:cursor-not-allowed"
          >
            <span
              className={`${FACE} ${slot.team ? "border-accent" : "border-rule bg-card border-dashed"}`}
            >
              {slot.team ? (
                <>
                  <Avatar
                    src={slot.team.avatar ?? AVATAR_FALLBACK}
                    className="bg-card size-full rounded-full object-cover"
                  />
                  <span
                    aria-hidden="true"
                    className="-right-sp-1 -bottom-sp-1 size-sp-5 bg-band text-meta text-on-dark absolute grid place-items-center rounded-full font-mono font-bold"
                  >
                    {index + 1}
                  </span>
                </>
              ) : (
                <span className="text-meta text-mute font-mono font-bold">{index + 1}</span>
              )}
            </span>
            <span className="text-meta max-w-[6rem] truncate leading-tight font-bold">
              {slot.title}
            </span>
          </button>
        </li>
      ))}
      {slots.length < MAX_SIDES && (
        <li className="gap-sp-1 flex flex-col items-center">
          <button
            type="button"
            disabled={locked}
            onClick={onAdd}
            aria-label="Add a team"
            className={`press ${FACE} border-rule bg-card text-ink hover:border-accent focus-visible:outline-accent cursor-pointer border-dashed focus-visible:outline-2 focus-visible:outline-offset-2 disabled:cursor-not-allowed`}
          >
            <PlusIcon aria-hidden="true" className="size-sp-5" />
          </button>
          <span className="text-meta text-mute font-mono leading-tight font-bold">
            {slots.length} of {MAX_SIDES}
          </span>
        </li>
      )}
    </ul>
  );
}
