/**
 * The Announcement of the season sim on the home page: the general Announcement with the art of the sim. It reads Your
 * team from local storage at the load beat, and opens only for a team of the week sim file.
 */
"use client";

import { useState } from "react";
import { Announcement } from "@cpc/design/parts/announcement";
import type { PreviewData } from "@cpc/sim/announcement/preview";
import { SimPreview } from "@cpc/sim/announcement/sim-preview";
import { getYourTeam } from "@/app/front-door/your-team-store";
import { useAnnouncement } from "@/app/use-announcement";

/* The spec sets no release date, so the release is the first weekly publish after the merge of the spec: week 11, on
   Tuesday 2026-11-24. The Announcement stops 1 week later, from the start of 2026-12-01 in the time of the manager. */
export const SIM_ANNOUNCEMENT = { id: "season-sim-2026", release: "2026-11-24", stops: "2026-12-01" } as const;

const COPY = {
  eyebrow: "New: Season sim",
  title: "See your path to the playoffs",
  line: "Pick this week's results and watch your playoff odds move.",
  follow: "Open the sim",
  dismiss: "Not now",
};

export function SimAnnouncement({ data, siteName, href }: { data: PreviewData; siteName: string; href: string }) {
  const { open, data: you, dismiss, follow } = useAnnouncement({
    id: SIM_ANNOUNCEMENT.id,
    href,
    stops: SIM_ANNOUNCEMENT.stops,
    read: () => {
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
