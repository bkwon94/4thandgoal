/**
 * The sim page of Your team in the browser: it reads Your team from local storage after the first paint, then renders
 * the sim page of that team, or the pick of a team when the browser keeps none.
 */
"use client";

import { useEffect, useState } from "react";
import { SimPage, type Avatars } from "@cpc/sim/page/sim-page";
import { TeamPick } from "@cpc/sim/page/team-pick";
import type { WeekSim } from "@cpc/sim/schema/sim-types";
import { getYourTeam, setYourTeam } from "@/app/front-door/your-team-store";

export function YourSimPage({ sim, avatars }: { sim: WeekSim; avatars: Avatars }) {
  // Undefined until the read of storage after mount, so the static page and the first paint in the browser agree.
  const [you, setYou] = useState<number | null | undefined>(undefined);
  useEffect(() => {
    const kept = getYourTeam();
    setYou(kept !== null && kept in sim.pages ? kept : null);
  }, [sim]);

  // The space of the page stays, so the footer does not jump when the page fills in.
  if (you === undefined) return <div aria-busy="true" className="min-h-dvh" />;
  if (you === null) {
    return (
      <TeamPick
        sim={sim}
        onPick={(id) => {
          setYourTeam(id);
          setYou(id);
        }}
      />
    );
  }
  return <SimPage sim={sim} you={you} avatars={avatars} />;
}
