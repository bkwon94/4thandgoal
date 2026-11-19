/**
 * The Sim tile of Your team in the browser: it reads Your team from local storage after the first paint, then shows
 * the tile of that team, or the league fact when the browser keeps no team or a team not in the file.
 */
"use client";

import { useEffect, useState } from "react";
import { SimTile } from "@cpc/sim/tile/sim-tile";
import type { SimTileData } from "@cpc/sim/tile/tile";
import { getYourTeam } from "@/app/front-door/your-team-store";

export function YourSimTile({ data, href }: { data: SimTileData; href: string }) {
  // Undefined until the read of storage after mount, so the static page and the first paint in the browser agree.
  const [you, setYou] = useState<number | null | undefined>(undefined);
  useEffect(() => {
    const kept = getYourTeam();
    setYou(kept !== null && kept in data.teams ? kept : null);
  }, [data]);
  const tile = you === undefined || you === null ? null : data.teams[you];
  return (
    // The tile holds its place before the read and fades in after it, so the fact never flashes before the odds.
    <div data-ready={you !== undefined} className="opacity-0 transition-opacity duration-200 ease-out data-[ready=true]:opacity-100 motion-reduce:transition-none">
      <SimTile tile={tile} fact={data.fact} href={href} />
    </div>
  );
}
