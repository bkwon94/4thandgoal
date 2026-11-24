/**
 * The sim page of Your team in the browser: it reads Your team from local storage after the first paint, then renders
 * the sim page of that team, or the pick of a team when the browser keeps none. A tap on a result calls the What-if of the API.
 */
"use client";

import { useEffect, useState } from "react";
import { whatIfApi } from "@cpc/sim/lib/what-if-api";
import { SimPage, type Avatars } from "@cpc/sim/page/sim-page";
import { TeamPick } from "@cpc/sim/page/team-pick";
import type { WeekSim } from "@cpc/sim/schema/sim-types";
import { getYourTeam, setYourTeam } from "@/app/front-door/your-team-store";
import { simTarget } from "@/lib/config";

/* The one client of the What-if route of the build, for each page that opens. */
const whatIf = whatIfApi(simTarget);

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
  return (
    <SimPage
      sim={sim}
      you={you}
      avatars={avatars}
      whatIf={whatIf}
      onYou={(id) => {
        setYourTeam(id);
        setYou(id);
      }}
    />
  );
}
