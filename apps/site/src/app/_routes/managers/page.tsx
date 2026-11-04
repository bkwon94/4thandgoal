/**
 * The managers index at /<season>/managers/, read from the season managers file at build time.
 * The client build writes its route file only when the client takes managers and the latest season has a managers file.
 */
import type { Metadata } from "next";
import { Masthead } from "@/components/shell/masthead";
import { ManagersIndex } from "@/components/managers/managers-index";
import { PageColumn } from "@/components/parts/page-column";
import { loadManagers } from "@/lib/data/manager-data";
import { latestAvatars } from "@/lib/data/rankings-data";
import { managersHref } from "@/lib/routes";
import { mastheadProps } from "@/app/masthead-props";

type Props = { params: Promise<{ season: string }> };

export function generateStaticParams(): { season: string }[] {
  const managers = loadManagers();
  return managers ? [{ season: String(managers.season) }] : [];
}

export const metadata: Metadata = {
  title: "Managers · Cornerstone Fantasy Football League",
};

export default async function ManagersPage({ params }: Props) {
  const { season } = await params;
  // The route only builds with the file, so the loader gives the managers here.
  const managers = loadManagers()!;
  return (
    <>
      <Masthead {...mastheadProps()} subtitle="Managers" pageHref={managersHref(season)} />
      <PageColumn>
        <ManagersIndex managers={managers} avatars={latestAvatars(managers.season)} managersHref={managersHref(season)} />
      </PageColumn>
    </>
  );
}
