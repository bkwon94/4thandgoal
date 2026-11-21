/**
 * The Trade block strip of Find mode: one row of the asker's QB, RB, WR, and TE, where a tap puts a player on the
 * block or takes him off, up to 3. The picks lead the strip in the order of the taps. The finder holds the picks.
 */
"use client";

import { motion } from "framer-motion";
import { CheckIcon, CircleAlertIcon } from "lucide-react";
import { useRef, useState } from "react";
import { Headshot } from "@cpc/league/headshot";
import { HEADSHOT_FALLBACK } from "@cpc/league/images";
import { ScrollArea, ScrollAreaContent, ScrollAreaViewport } from "@cpc/design/ui/scroll-area";
import { Toggle, ToggleGroup } from "@cpc/design/ui/toggle-group";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { cn } from "@cpc/design/lib/utils";
import type { TeamPlayer } from "../lib/api";

/* The find route takes at most 3 block players. */
export const BLOCK_MAX = 3;

// The reason line of a 4th tap. It names the rule and the way out, in plain words.
const BLOCK_FULL = "Your block holds 3 players. Take one off to add another.";
// The line of an empty block. The empty block sets no rule, so the search may send any player.
const BLOCK_EMPTY = "No one on the block. The search can offer any of your players.";

// The chart lists only these positions, so no trade can send a kicker or a defense, and the strip never lists one.
const POSITIONS = ["QB", "RB", "WR", "TE"];

// A critically damped spring, as apple-design advises for a move that no flick started: it settles with no bounce.
const PIN_SPRING = { type: "spring", duration: 0.4, bounce: 0 } as const;

/* The players the strip lists: the QB, RB, WR, and TE of the roster, in that position order, then by name. */
export function blockRoster(players: TeamPlayer[]): TeamPlayer[] {
  return players
    .filter((player) => POSITIONS.includes(player.position))
    .sort((a, b) => POSITIONS.indexOf(a.position) - POSITIONS.indexOf(b.position) || a.name.localeCompare(b.name));
}

/* The last name of a player, so a headshot of 64 px holds his name below it. */
function lastName(name: string): string {
  const parts = name.split(" ");
  return parts.length > 1 ? parts.slice(1).join(" ") : name;
}

export function TradeBlock({
  players,
  picks,
  onPicks,
  disabled,
}: {
  // The whole roster of the asker. The strip lists only its QB, RB, WR, and TE.
  players: TeamPlayer[];
  // The player ids on the block, in the order of the taps.
  picks: string[];
  onPicks: (picks: string[]) => void;
  disabled: boolean;
}) {
  const off = useMotionOff();
  const viewport = useRef<HTMLDivElement>(null);
  // A 4th tap sets the reason. Any change of the block clears it, so the line names only the tap the reader just made.
  const [refused, setRefused] = useState(false);
  const roster = blockRoster(players);
  const full = picks.length >= BLOCK_MAX;
  const picked = picks.flatMap((id) => roster.filter((player) => player.player_id === id));
  // The picks lead in the order of the taps, then the rest of the roster in its own order.
  const order = [...picked, ...roster.filter((player) => !picks.includes(player.player_id))];

  function change(next: string[]) {
    const added = next.find((id) => !picks.includes(id));
    if (added === undefined) {
      setRefused(false);
      onPicks(picks.filter((id) => next.includes(id)));
      return;
    }
    // A pick lands at the front, and a refused 4th tap shows the 3 picks it names, so both scroll the strip back to
    // its start. The viewport scrolls smoothly unless motion is off, through its class.
    if (viewport.current) viewport.current.scrollLeft = 0;
    if (full) {
      setRefused(true);
      return;
    }
    setRefused(false);
    onPicks([...picks, added]);
  }

  return (
    <div className="flex flex-col gap-sp-2">
      <div className="flex items-baseline justify-between gap-sp-3 px-sp-1">
        <span className="text-label font-bold tracking-caps text-on-dark-muted uppercase">
          {full ? "Trade block · tap a pick to take it off" : "Trade block · tap to add"}
        </span>
        <span
          className={cn(
            "flex-none rounded-pill px-sp-2 py-sp-0 text-meta font-bold tabular-nums transition-[background-color,color] duration-150 ease-out",
            full ? "bg-chip-dark text-on-dark" : "text-on-dark-muted",
          )}
        >
          {picks.length} of {BLOCK_MAX}
        </span>
      </div>
      {/* The strip runs to the edges of the hero. The mask fades both ends, so a cut headshot says "scroll for more".
          The viewport of the ScrollArea is the native scroller, and it hides the scrollbar itself. */}
      <ScrollArea className="-mx-sp-4">
        <ScrollAreaViewport
          ref={viewport}
          className="overscroll-x-contain motion-safe:scroll-smooth [mask-image:linear-gradient(to_right,transparent,black_var(--spacing-sp-4),black_calc(100%-var(--spacing-sp-6)*2),transparent)] [&::-webkit-scrollbar]:hidden"
        >
          <ScrollAreaContent className="w-max">
            <ToggleGroup multiple aria-label="Trade block" value={picks} onValueChange={change} disabled={disabled} className="flex gap-sp-2 px-sp-4 py-sp-1">
              {order.map((player) => {
                const on = picks.includes(player.player_id);
                return (
                  <motion.div key={player.player_id} layout={off ? false : "position"} transition={PIN_SPRING} className="flex-none">
                    <Toggle
                      value={player.player_id}
                      aria-label={`${player.name}, ${player.position}`}
                      className="press flex w-[64px] cursor-pointer flex-col items-center gap-sp-1 rounded-card py-sp-1 outline-none focus-visible:outline-2 focus-visible:outline-accent aria-disabled:cursor-not-allowed aria-disabled:opacity-60"
                    >
                      {/* A player past the cap dims only his headshot, so his name keeps full contrast. */}
                      <span className={cn("relative transition-opacity duration-150 ease-out", full && !on && "opacity-40")}>
                        <Headshot
                          src={player.headshot || HEADSHOT_FALLBACK}
                          size={52}
                          className={cn(
                            "rounded-full bg-chip-dark object-cover object-top ring-2 ring-offset-2 ring-offset-band transition-[box-shadow] duration-150 ease-out",
                            on ? "ring-accent" : "ring-transparent",
                          )}
                        />
                        <span
                          aria-hidden="true"
                          data-check={on}
                          className={cn(
                            "absolute -right-sp-0 -bottom-sp-0 grid size-sp-5 place-items-center rounded-full bg-accent text-on-dark ring-2 ring-band transition-[opacity,scale] duration-150 ease-out",
                            on ? "scale-100 opacity-100" : "scale-50 opacity-0",
                          )}
                        >
                          <CheckIcon className="size-sp-3" strokeWidth={3} />
                        </span>
                      </span>
                      <span className={cn("w-full truncate text-center text-label leading-tight font-bold", on ? "text-on-dark" : "text-on-dark-2")}>
                        {lastName(player.name)}
                      </span>
                      <span className="text-label leading-none text-on-dark-muted">{player.position}</span>
                    </Toggle>
                  </motion.div>
                );
              })}
            </ToggleGroup>
          </ScrollAreaContent>
        </ScrollAreaViewport>
      </ScrollArea>
      <div aria-live="polite" className="px-sp-1">
        {refused && full && (
          <p className="m-0 flex items-start gap-sp-2 text-meta leading-tight font-bold text-pretty text-on-dark">
            <CircleAlertIcon aria-hidden="true" className="mt-px size-sp-4 flex-none text-accent-text" />
            {BLOCK_FULL}
          </p>
        )}
        {picks.length === 0 && <p className="m-0 text-meta leading-tight text-pretty text-on-dark-2">{BLOCK_EMPTY}</p>}
      </div>
    </div>
  );
}
