/**
 * The Sim tile of the week page: one card link to The Race with the odds of Your team and one line under them,
 * or the league fact of the build when the browser keeps no team, the team is out, or the season is over.
 */
import { ArrowRightIcon } from "lucide-react";
import { cn } from "@cpc/design/lib/utils";
import type { TeamTile } from "./tile";

/* The label of the tile is the label of the tiles of the week page, at the meta size, so it meets the text floor of 11px. */
const TILE_LABEL = "font-mono text-meta leading-tight font-bold tracking-caps uppercase";

/* A plain anchor, so the link skips the router. The whole card is the tap target, as on the tiles of the home page. */
export function SimTile({
  tile,
  fact,
  href,
}: {
  tile: TeamTile | null;
  fact: string | null;
  href: string;
}) {
  return (
    <a
      href={href}
      data-tile={tile === null ? "fact" : "team"}
      className="press group gap-sp-3 rounded-card border-rule bg-card p-sp-4 text-ink flex min-w-0 flex-col border no-underline"
    >
      {tile === null ? (
        <span className="gap-sp-1 flex flex-col">
          <span className={cn(TILE_LABEL, "text-mute")}>The league</span>
          <span className="text-lead leading-tight font-bold text-balance">
            {fact ?? "Pick your team to see your odds."}
          </span>
        </span>
      ) : (
        <span className="gap-sp-1 flex flex-col">
          <span className={cn(TILE_LABEL, "text-mute")}>{tile.label}</span>
          {/* The number is mono, as on the four numbers of the week, so the tiles of the page read as one set. */}
          <span className="text-stat leading-stat font-mono font-bold tabular-nums">
            {tile.odds}
          </span>
          <span className="text-body leading-body text-ink-2 text-pretty">{tile.line}</span>
        </span>
      )}
      {/* The whole card takes the tap, so this row needs no touch height of its own. */}
      <span className="gap-sp-2 text-body text-accent-ink flex items-center self-start leading-tight font-semibold">
        <span>Open The Race</span>
        <ArrowRightIcon
          aria-hidden
          className="size-sp-4 group-hover:translate-x-sp-0 transition-transform duration-150 ease-out motion-reduce:transition-none"
          strokeWidth={2.25}
        />
      </span>
    </a>
  );
}
