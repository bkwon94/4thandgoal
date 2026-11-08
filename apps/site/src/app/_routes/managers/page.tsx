/**
 * The managers index at /<season>/managers/, read from the season managers file at build time.
 * The client build writes its route file only when the client takes managers and the latest season has a managers file.
 */
import type { Metadata } from "next";
import { TopBand } from "@cpc/design/shell/top-band";
import { ManagersIndex } from "@cpc/managers/page/managers-index";
import { PageColumn } from "@cpc/design/parts/page-column";
import { loadManagers } from "@/lib/data/manager-data";
import { latestAvatars } from "@/lib/data/rankings-data";
import { managersHref } from "@/lib/routes";
import { shellProps, pageTitle } from "@/app/shell-props";

type Props = { params: Promise<{ season: string }> };

export function generateStaticParams(): { season: string }[] {
  const managers = loadManagers();
  return managers ? [{ season: String(managers.season) }] : [];
}

export const metadata: Metadata = {
  title: pageTitle(undefined, "Managers"),
};

export default async function ManagersPage({ params }: Props) {
  const { season } = await params;
  // The route only builds with the file, so the loader gives the managers here.
  const managers = loadManagers()!;
  return (
    <>
      <TopBand {...shellProps()} pageHref={managersHref(season)} />
      {/* The page is wide from the desktop tier, so the stage of the Index list sits beside the ledger. */}
      <PageColumn wide>
        <ManagersIndex managers={managers} avatars={latestAvatars(managers.season)} managersHref={managersHref(season)} />
      </PageColumn>
    </>
  );
}
