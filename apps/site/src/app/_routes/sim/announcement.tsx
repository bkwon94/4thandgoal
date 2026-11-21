/**
 * The Announcement of the season sim on the home page: the general Announcement with the art of the sim. It reads Your
 * team from local storage at load and at the load beat, and opens only for a team of the week sim file kept at load.
 */
"use client";

import { useEffect, useRef, useState } from "react";
import { Announcement } from "@cpc/design/parts/announcement";
import type { PreviewData } from "@cpc/sim/announcement/preview";
import { SimPreview } from "@cpc/sim/announcement/sim-preview";
import { getYourTeam } from "@/app/front-door/your-team-store";
import { useAnnouncement } from "@/app/use-announcement";

/* The release is the merge day of the spec, Thursday 2026-11-19, as Brian set. The Announcement stops 1 week later,
   from the start of 2026-11-26 in the time of the manager. */
export const SIM_ANNOUNCEMENT = {
  id: "season-sim-2026",
  release: "2026-11-19",
  stops: "2026-11-26",
} as const;

const COPY = {
  eyebrow: "New: Season sim",
  title: "See your path to the playoffs",
  line: "Pick this week's results and watch your playoff odds move.",
  follow: "Open the sim",
  dismiss: "Not now",
};

export function SimAnnouncement({
  data,
  siteName,
  href,
}: {
  data: PreviewData;
  siteName: string;
  href: string;
}) {
  // The team kept when the page loads. A load with no team opens the team picker, so the Announcement skips that load
  // even when the pick comes before the load beat. The note then shows on the next load (story 51).
  const keptAtLoad = useRef<number | null>(null);
  useEffect(() => {
    keptAtLoad.current = getYourTeam();
  }, []);
  const {
    open,
    data: you,
    dismiss,
    follow,
  } = useAnnouncement({
    id: SIM_ANNOUNCEMENT.id,
    href,
    stops: SIM_ANNOUNCEMENT.stops,
    read: () => {
      if (keptAtLoad.current === null) return null;
      const kept = getYourTeam();
      return kept !== null && data.table.some((row) => row.id === kept) ? kept : null;
    },
  });
  // The art starts its automatic What-if once the sheet stops.
  const [settled, setSettled] = useState(false);

  if (you === null) return null;
  return (
    <Announcement
      open={open}
      siteName={siteName}
      href={href}
      copy={COPY}
      art={<SimPreview data={data} you={you} settled={settled} />}
      onDismiss={dismiss}
      onFollow={follow}
      onSettled={() => setSettled(true)}
    />
  );
}
