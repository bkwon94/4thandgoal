/**
 * The Announcement of The Race on the home page: the general Announcement with the League board as art. It reads Your
 * team from local storage at load and at the load beat, and opens only for a team of the week sim file kept at load.
 */
"use client";

import { useEffect, useRef } from "react";
import { Announcement } from "@cpc/design/parts/announcement";
import type { PreviewData } from "@cpc/sim/announcement/preview";
import { SimPreview } from "@cpc/sim/announcement/sim-preview";
import { getYourTeam } from "@/app/front-door/your-team-store";
import { useAnnouncement } from "@/app/use-announcement";

/* The release is the build day of the playoff-paths spec, Tuesday 2026-11-24, so the Announcement shows from the merge.
   It stops 1 week later, from the start of 2026-12-01 in the time of the manager. A new id shows it also in a browser
   that saw the season sim Announcement. */
export const SIM_ANNOUNCEMENT = {
  id: "the-race-2026",
  release: "2026-11-24",
  stops: "2026-12-01",
} as const;

/* The line is a call the spec records for review (PRD of playoff-paths, Further Notes, call 3). */
const COPY = {
  eyebrow: "New: The Race",
  title: "The Race is on",
  line: "See what you need each week, and who to root for.",
  follow: "Open The Race",
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
      return kept !== null && data.rows.some((row) => row.id === kept) ? kept : null;
    },
  });
  if (you === null) return null;
  return (
    <Announcement
      open={open}
      siteName={siteName}
      href={href}
      copy={COPY}
      art={<SimPreview data={data} you={you} />}
      onDismiss={dismiss}
      onFollow={follow}
    />
  );
}
