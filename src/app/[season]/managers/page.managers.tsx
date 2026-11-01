/**
 * The managers index at /<season>/managers/, read from the season managers file at build time.
 * The .managers.tsx name keeps it out of a build with no managers file: next.config adds the extension only when the file exists.
 */
import type { Metadata } from "next";
import { Masthead } from "@/components/masthead";
import { ManagersIndex } from "@/components/managers/managers-index";
import { PageColumn } from "@/components/page-column";
import { loadManagers } from "@/lib/data/manager-data";
import { latestAvatars } from "@/lib/data/rankings-data";
import { managersHref } from "@/lib/routes";
import { mastheadProps } from "@/app/masthead-props";

type Props = { params: Promise<{ season: string }> };

// The export is static, so a season with no managers file at build time has no page.
export const dynamicParams = false;

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
        <ManagersIndex managers={managers} avatars={latestAvatars(managers.season)} />
      </PageColumn>
    </>
  );
}
