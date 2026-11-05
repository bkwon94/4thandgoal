/**
 * The picker "Gets": the sheet that adds the players one side gets, with a tab for each other team, a search, and the position chips.
 * A tap on a row toggles a check at once, so each way out of the sheet keeps the picks.
 */
"use client";

import { CheckIcon } from "lucide-react";
import { useState } from "react";
import { Headshot } from "@cpc/league/headshot";
import { HEADSHOT_FALLBACK } from "@cpc/league/images";
import type { Team } from "../lib/api";
import type { Get } from "../lib/trade";
import { cn } from "@cpc/design/lib/utils";
import { Sheet } from "./sheet";

/* The chips of the picker. All shows every player, so a kicker still shows under All. */
export const POSITIONS = ["All", "QB", "RB", "WR", "TE", "DEF"] as const;
type Position = (typeof POSITIONS)[number];

/* Another side of the trade that this side can get a player from: its id and its team. */
export type Source = { sideId: number; team: Team };

type PlayerSheetProps = {
  open: boolean;
  // The heading of the side that gets the players, such as "Your Team".
  title: string;
  sources: Source[];
  // The players this side gets now.
  gets: Get[];
  // The player ids that another side already gets, each with the name of that team. A player goes to one team only.
  elsewhere: Map<string, string>;
  onToggle: (get: Get) => void;
  onClose: () => void;
};

/* The pill of a tab or a chip: a touch target, with the brand fill when it is on. */
const PILL =
  "press min-h-touch min-w-touch flex-none cursor-pointer rounded-pill border px-sp-4 text-meta font-bold focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent";
const PILL_ON = "border-accent bg-accent text-on-dark";
const PILL_OFF = "border-rule bg-card text-ink hover:bg-raised";

export function PlayerSheet({ open, title, sources, gets, elsewhere, onToggle, onClose }: PlayerSheetProps) {
  const [tab, setTab] = useState(0);
  const [query, setQuery] = useState("");
  const [position, setPosition] = useState<Position>("All");
  // A side can leave while the sheet is closed, so the tab falls back to the first source.
  const source = sources[tab] ?? sources[0];
  const needle = query.trim().toLowerCase();
  const players = (source?.team.players ?? []).filter(
    (p) => (position === "All" || p.position === position) && (needle === "" || p.name.toLowerCase().includes(needle)),
  );
  const checked = (playerId: string) => gets.some((get) => get.playerId === playerId && get.fromSide === source?.sideId);

  return (
    <Sheet
      open={open}
      title={`${title} gets`}
      onClose={onClose}
      footer={
        <button
          type="button"
          onClick={onClose}
          className="press min-h-touch w-full cursor-pointer rounded-pill bg-accent px-sp-4 text-lead font-bold text-on-dark focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        >
          Done{gets.length > 0 ? ` · ${gets.length}` : ""}
        </button>
      }
    >
      <div role="tablist" aria-label="From team" className="flex gap-sp-2 overflow-x-auto">
        {sources.map((s, index) => (
          <button
            key={s.sideId}
            type="button"
            role="tab"
            aria-selected={s === source}
            onClick={() => setTab(index)}
            className={cn(PILL, "max-w-full truncate", s === source ? PILL_ON : PILL_OFF)}
          >
            {s.team.team}
          </button>
        ))}
      </div>
      <input
        type="search"
        aria-label="Search players"
        placeholder="Search players"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        className="min-h-touch w-full rounded-card border border-rule bg-card px-sp-3 text-lead text-ink placeholder:text-mute focus-visible:outline-2 focus-visible:outline-accent"
      />
      <div role="group" aria-label="Position" className="flex flex-wrap gap-sp-2">
        {POSITIONS.map((p) => (
          <button
            key={p}
            type="button"
            aria-pressed={p === position}
            onClick={() => setPosition(p)}
            className={cn(PILL, p === position ? PILL_ON : PILL_OFF)}
          >
            {p}
          </button>
        ))}
      </div>
      <ul aria-label={source ? `Players of ${source.team.team}` : "Players"} className="m-0 flex list-none flex-col gap-sp-1 p-0">
        {players.map((player) => {
          const on = checked(player.player_id);
          const goesTo = elsewhere.get(player.player_id);
          return (
            <li key={player.player_id}>
              <button
                type="button"
                role="checkbox"
                aria-checked={on}
                disabled={goesTo !== undefined}
                onClick={() => source && onToggle({ playerId: player.player_id, fromSide: source.sideId })}
                className={cn(
                  "press flex min-h-touch w-full cursor-pointer items-center gap-sp-3 rounded-card border px-sp-3 py-sp-1 text-left text-ink focus-visible:outline-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-40",
                  on ? "border-accent bg-card" : "border-transparent hover:bg-card",
                )}
              >
                <Headshot src={player.headshot || HEADSHOT_FALLBACK} size="avatar" lazy className="flex-none rounded-full bg-raised object-cover object-top" />
                <span className="flex min-w-0 flex-1 flex-col">
                  <b className="truncate text-row leading-tight font-bold">{player.name}</b>
                  <span className="text-meta text-mute">
                    {player.position} {player.nfl_team}
                    {goesTo !== undefined && ` · to ${goesTo}`}
                  </span>
                </span>
                <span
                  aria-hidden="true"
                  className={cn(
                    "grid size-sp-6 flex-none place-items-center rounded-full border",
                    on ? "border-accent bg-accent text-on-dark" : "border-rule",
                  )}
                >
                  {on && <CheckIcon className="size-sp-4" />}
                </span>
              </button>
            </li>
          );
        })}
      </ul>
      {players.length === 0 && <p className="m-0 text-lead text-mute">No player matches.</p>}
    </Sheet>
  );
}
