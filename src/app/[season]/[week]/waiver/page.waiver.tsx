/**
 * The waiver page at /<season>/week-NN/waiver/, one static page per waiver.json in public/.
 * The .waiver.tsx name keeps it out of most builds: next.config adds the extension only with the flag on
 * and at least one week with a waiver file.
 */
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Masthead, WeekLine } from "@/components/masthead";
import { WarChest } from "@/components/waiver/war-chest";
import { basePath } from "@/lib/config";
import { listWaiverWeeks, loadWaiver } from "@/lib/data/waiver-data";
import { loadWeek, type WeekRef } from "@/lib/data/week-data";
import type { AvatarMap } from "@/lib/week-types";

type Props = { params: Promise<WeekRef> };

// The export is static, so a week with no waiver file at build time has no page.
export const dynamicParams = false;

export function generateStaticParams(): WeekRef[] {
  return listWaiverWeeks();
}

export const metadata: Metadata = {
  title: "Waiver Wire · Cornerstone Fantasy Football League",
};

/* The league plays on US Eastern time, and the static build must not read the time zone of the build machine. */
const BUILT = new Intl.DateTimeFormat("en-US", {
  weekday: "short",
  month: "short",
  day: "numeric",
  hour: "numeric",
  minute: "2-digit",
  timeZone: "America/New_York",
  timeZoneName: "short",
});

/* The week JSON avatar paths are relative to the week folder, but this route sits one folder down, so each path gets the folder in front. */
function weekAvatars(season: string, week: string, avatars: AvatarMap): AvatarMap {
  const folder = `${basePath}/${season}/${week}`;
  return Object.fromEntries(Object.entries(avatars).map(([id, path]) => [id, `${folder}/${path}`]));
}

export default async function WaiverPage({ params }: Props) {
  const { season, week } = await params;
  const board = loadWaiver(season, week);
  if (!board) notFound();
  const page = loadWeek(season, week);
  return (
    <>
      <Masthead subtitle="Waiver Wire" pageHref={`${basePath}/${season}/${week}/waiver/`}>
        <WeekLine label="WEEK" number={board.week} />
        <div className="mt-sp-1 text-meta text-on-dark-2 tabular-nums">{`Built ${BUILT.format(new Date(board.built))}`}</div>
      </Masthead>
      <main className="mx-auto max-w-page bg-wht">
        <WarChest board={board} teams={page.teams} avatars={weekAvatars(season, week, page.avatars)} />
      </main>
    </>
  );
}
