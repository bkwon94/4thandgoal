/**
 * The manager page at /<season>/managers/<roster_id>/, one static page per entry in the season managers file.
 * The client build writes its route file only when the client takes managers and the latest season has a managers file.
 */
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { TopBand } from "@cpc/design/shell/top-band";
import { ManagerChapters, MANAGER_CHAPTERS } from "@cpc/managers/page/manager-chapters";
import { ManagerHero } from "@cpc/managers/page/manager-hero";
import { PageColumn } from "@cpc/design/parts/page-column";
import { ChapterRail } from "@cpc/design/parts/chapter-rail";
import { avatarSrc } from "@cpc/league/images";
import { loadManagers, seasonManagersHref } from "@/lib/data/manager-data";
import { latestAvatars } from "@/lib/data/rankings-data";
import { managerHref, managersHref } from "@/lib/routes";
import { shellProps, pageTitle } from "@/app/shell-props";

type Params = { season: string; roster: string };
type Props = { params: Promise<Params> };

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
  return { title: pageTitle(undefined, found?.manager.team.name ?? "Managers") };
}

export default async function ManagerPage({ params }: Props) {
  const { season, roster } = await params;
  const found = managerOf(roster);
  if (!found) notFound();
  const { managers, manager } = found;
  return (
    <>
      <TopBand {...shellProps()} pageHref={managerHref(season, manager.roster_id)} />
      <PageColumn rail={<ChapterRail chapters={MANAGER_CHAPTERS} />}>
        {/* The back link comes first, so a reader moves to the next team in one tap. It is a full tap target. */}
        <div className="px-gutter pt-sp-4 tablet:px-0">
          <a href={managersHref(season)} className="inline-flex min-h-touch items-center text-body font-bold text-accent-ink no-underline">
            ← All Managers
          </a>
        </div>
        {/* The hero rises in on load. Each chapter below reveals once as it enters the view. */}
        <div className="px-gutter tablet:px-0">
          <ManagerHero
            manager={manager}
            avatar={avatarSrc(latestAvatars(managers.season), manager.roster_id)}
            teams={managers.managers.length}
          />
        </div>
        <ManagerChapters manager={manager} managers={managers.managers} managersHref={seasonManagersHref(season)} />
      </PageColumn>
    </>
  );
}
