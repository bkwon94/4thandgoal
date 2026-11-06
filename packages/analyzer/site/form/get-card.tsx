/**
 * The card of one side of the Stack: "<side> gets", the players the side gets, each with a "from <team>" tag, and the add button.
 * The form owns the trade, so this part only reads its side and reports each change.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { PlusIcon, XIcon } from "lucide-react";
import { useId } from "react";
import { Card } from "@cpc/design/parts/card";
import { Headshot } from "@cpc/league/headshot";
import { HEADSHOT_FALLBACK } from "@cpc/league/images";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { enterExit } from "@cpc/design/lib/motion";
import type { Team, TeamPlayer } from "../lib/api";

/* A player the side gets, with the team that gives him. */
export type GotRow = { player: TeamPlayer; from: Team };

type GetCardProps = {
  // The heading of the side, such as "Your Team".
  title: string;
  team: Team | undefined;
  rows: GotRow[];
  // False until this side and another side each have a team, so the picker has a team to show.
  canAdd: boolean;
  onAdd: () => void;
  onRemovePlayer: (playerId: string) => void;
  // Set only for the third and fourth sides. The card then shows a remove control.
  onRemove?: () => void;
  // A grade runs, so no control may change the trade that the grade reads.
  locked: boolean;
};

/* A small control of the card: a touch target with a muted icon. */
const ICON_BUTTON =
  "press grid size-touch flex-none cursor-pointer place-items-center rounded-pill text-mute hover:text-ink focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-40";

export function GetCard({ title, team, rows, canAdd, onAdd, onRemovePlayer, onRemove, locked }: GetCardProps) {
  const headingId = useId();
  const off = useMotionOff();
  return (
    <section aria-labelledby={headingId} className="min-w-0">
      <Card className="flex min-w-0 flex-col gap-sp-3">
        <div className="flex min-h-touch items-center justify-between gap-sp-2">
          <div className="min-w-0">
            <h3 id={headingId} className="m-0 text-stat leading-stat font-bold">
              {title} gets
            </h3>
            <span className="block truncate text-meta text-mute">{team ? team.team : "No team yet"}</span>
          </div>
          {onRemove && (
            <button type="button" aria-label={`Remove ${title}`} disabled={locked} onClick={onRemove} className={`${ICON_BUTTON} -mr-sp-2`}>
              <XIcon aria-hidden="true" className="size-sp-5" />
            </button>
          )}
        </div>
        {/* The list stays in the page, so the last row can animate out. empty:hidden drops the empty list from the layout. */}
        <ul aria-label={`Players ${title} gets`} className="relative m-0 flex list-none flex-col gap-sp-1 p-0 empty:hidden">
          <AnimatePresence initial={false} mode="popLayout">
            {rows.map(({ player, from }) => (
              <motion.li
                key={player.player_id}
                layout={!off}
                {...enterExit(off)}
                className="flex min-h-touch items-center gap-sp-3 rounded-tile bg-raised py-sp-1 pl-sp-3 text-ink"
              >
                <Headshot src={player.headshot || HEADSHOT_FALLBACK} size="avatar" lazy className="flex-none rounded-full bg-card object-cover object-top" />
                <span className="flex min-w-0 flex-1 flex-col">
                  <b className="truncate text-row leading-tight font-bold">{player.name}</b>
                  <span className="truncate text-meta text-mute">
                    {player.position} {player.nfl_team} · <span className="font-bold text-ink">from {from.team}</span>
                  </span>
                </span>
                <button
                  type="button"
                  aria-label={`Remove ${player.name}`}
                  disabled={locked}
                  onClick={() => onRemovePlayer(player.player_id)}
                  className={ICON_BUTTON}
                >
                  <XIcon aria-hidden="true" className="size-sp-4" />
                </button>
              </motion.li>
            ))}
          </AnimatePresence>
        </ul>
        <button
          type="button"
          disabled={!canAdd || locked}
          onClick={onAdd}
          className="press flex min-h-touch w-full cursor-pointer items-center justify-center gap-sp-2 rounded-pill border border-dashed border-rule px-sp-4 text-meta font-bold text-ink hover:border-accent focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:text-mute"
        >
          <PlusIcon aria-hidden="true" className="size-sp-4" />
          Add a player {title} gets
        </button>
      </Card>
    </section>
  );
}
