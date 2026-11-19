/**
 * The Sim tile of the week page: one card link to the sim page with the odds of Your team and one line under them,
 * or the league fact of the build when the browser keeps no team, the team is out, or the season is over.
 */
import { ArrowRightIcon } from "lucide-react";
import { cn } from "@cpc/design/lib/utils";
import type { TeamTile } from "./tile";

/* The label of the tile is the label of the tiles of the week page, at the meta size, so it meets the text floor of 11px. */
const TILE_LABEL = "font-mono text-meta leading-tight font-bold tracking-caps uppercase";

/* A plain anchor, so the link skips the router. The whole card is the tap target, as on the tiles of the home page. */
export function SimTile({ tile, fact, href }: { tile: TeamTile | null; fact: string | null; href: string }) {
  return (
    <a
      href={href}
      data-tile={tile === null ? "fact" : "team"}
      className="press group flex min-w-0 flex-col gap-sp-3 rounded-card border border-rule bg-card p-sp-4 text-ink no-underline"
    >
      {tile === null ? (
        <span className="flex flex-col gap-sp-1">
          <span className={cn(TILE_LABEL, "text-mute")}>The league</span>
          <span className="text-lead leading-tight font-bold text-balance">{fact ?? "Pick your team to see your odds."}</span>
        </span>
      ) : (
        <span className="flex flex-col gap-sp-1">
          <span className={cn(TILE_LABEL, "text-mute")}>{tile.label}</span>
          {/* The number is mono, as on the four numbers of the week, so the tiles of the page read as one set. */}
          <span className="font-mono text-stat leading-stat font-bold tabular-nums">{tile.odds}</span>
          <span className="text-body leading-body text-pretty text-ink-2">{tile.line}</span>
        </span>
      )}
      {/* The whole card takes the tap, so this row needs no touch height of its own. */}
      <span className="flex items-center gap-sp-2 self-start text-body leading-tight font-semibold text-accent-ink">
        <span>Open the season sim</span>
        <ArrowRightIcon
          aria-hidden
          className="size-sp-4 transition-transform duration-150 ease-out group-hover:translate-x-sp-0 motion-reduce:transition-none"
          strokeWidth={2.25}
        />
      </span>
    </a>
  );
}
