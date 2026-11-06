/**
 * The team sheet of the Stack: every team of the league as one row, with the teams of the trade dimmed.
 * A tap on a free team picks it and closes the sheet. The form decides which side the team goes to.
 */
"use client";

import { Avatar } from "@cpc/league/avatar";
import { AVATAR_FALLBACK } from "@cpc/league/images";
import type { Team } from "../lib/api";
import { Sheet } from "./sheet";

type TeamSheetProps = {
  open: boolean;
  // The title names the slot, such as "Pick Team Three".
  title: string;
  teams: Team[];
  // The roster ids that a side of the trade holds. Their rows show dimmed and take no tap.
  taken: number[];
  onPick: (rosterId: number) => void;
  onClose: () => void;
};

export function TeamSheet({ open, title, teams, taken, onPick, onClose }: TeamSheetProps) {
  return (
    <Sheet open={open} title={title} onClose={onClose}>
      <ul aria-label="Teams" className="m-0 flex list-none flex-col gap-sp-1 p-0">
        {teams.map((team) => {
          const inTrade = taken.includes(team.roster_id);
          return (
            <li key={team.roster_id}>
              <button
                type="button"
                disabled={inTrade}
                onClick={() => onPick(team.roster_id)}
                className="press flex min-h-touch w-full cursor-pointer items-center gap-sp-3 rounded-card px-sp-3 py-sp-1 text-left text-ink hover:bg-card focus-visible:outline-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-40"
              >
                <Avatar src={team.avatar ?? AVATAR_FALLBACK} />
                <span className="flex min-w-0 flex-col">
                  <b className="truncate text-row leading-tight font-bold">{team.team}</b>
                  <span className="text-meta text-mute">{inTrade ? "In the trade" : team.manager}</span>
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    </Sheet>
  );
}
