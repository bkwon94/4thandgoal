/**
 * The Live names part that the layout mounts on every page. It turns the part off on the midseason report, because the
 * report keeps its published names as a record of its week (decision 07).
 */
"use client";

import { usePathname } from "next/navigation";
import { LiveNames, type PublishedTeam } from "@cpc/league/live-names";

const MIDSEASON = "/midseason/";

export function LiveNamesPart({
  leagueId,
  teams,
}: {
  leagueId: string | null;
  teams: PublishedTeam[];
}) {
  // Outside the router, such as in a test, usePathname gives null, so the part reads the address of the window.
  const path = usePathname() ?? (typeof window === "undefined" ? "" : window.location.pathname);
  if (leagueId === null) return null;
  return <LiveNames leagueId={leagueId} teams={teams} on={!path.startsWith(MIDSEASON)} />;
}
