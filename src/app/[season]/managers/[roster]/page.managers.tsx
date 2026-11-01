/**
 * The manager page at /<season>/managers/<roster_id>/, one static page per entry in the season managers file.
 * The .managers.tsx name keeps it out of a build with no managers file: next.config adds the extension only when the file exists.
 */
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { Masthead } from "@/components/masthead";
import { ManagerChapters, MANAGER_CHAPTERS } from "@/components/managers/manager-chapters";
import { ManagerHero } from "@/components/managers/manager-hero";
import { PageColumn } from "@/components/page-column";
import { ChapterRail } from "@/components/week/chapter-rail";
import { avatarSrc } from "@/components/week/parts";
import { loadManagers, seasonManagersHref } from "@/lib/data/manager-data";
import { latestAvatars } from "@/lib/data/rankings-data";
import { managerHref } from "@/lib/routes";
import { mastheadProps } from "@/app/masthead-props";

type Params = { season: string; roster: string };
type Props = { params: Promise<Params> };

// The export is static, so a roster with no entry in the managers file at build time has no page.
export const dynamicParams = false;

export function generateStaticParams(): Params[] {
  const managers = loadManagers();
  if (!managers) return [];
  return managers.managers.map((manager) => ({ season: String(managers.season), roster: String(manager.roster_id) }));
}

/* The entry of one roster, or none when the file or the roster is missing. */
function managerOf(roster: string) {
  const managers = loadManagers();
  const manager = managers?.managers.find((entry) => String(entry.roster_id) === roster);
  return managers && manager ? { managers, manager } : null;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { roster } = await params;
  const found = managerOf(roster);
  return { title: `${found?.manager.team.name ?? "Managers"} · Cornerstone Fantasy Football League` };
}

export default async function ManagerPage({ params }: Props) {
  const { season, roster } = await params;
  const found = managerOf(roster);
  if (!found) notFound();
  const { managers, manager } = found;
  return (
    <>
      <Masthead {...mastheadProps()} subtitle="Managers" pageHref={managerHref(season, manager.roster_id)} />
      <PageColumn rail={<ChapterRail chapters={MANAGER_CHAPTERS} />}>
        {/* The hero shows at once. Each chapter below reveals once as it enters the view. */}
        <ManagerHero
          manager={manager}
          avatar={avatarSrc(latestAvatars(managers.season), manager.roster_id)}
          teams={managers.managers.length}
        />
        <ManagerChapters manager={manager} managers={managers.managers} managersHref={seasonManagersHref(season)} />
      </PageColumn>
    </>
  );
}
