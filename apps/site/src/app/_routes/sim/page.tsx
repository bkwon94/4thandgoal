/**
 * The sim page at /sim/<season>/, one static page per season with a week sim file. It reads the newest week sim file,
 * the avatars of the latest week, and the shell values. The browser picks the page block of Your team.
 */
import type { Metadata } from "next";
import { PageColumn } from "@cpc/design/parts/page-column";
import { TopBand } from "@cpc/design/shell/top-band";
import { latestAvatars } from "@/lib/data/rankings-data";
import { latestWeekSim, weekSimSeasons } from "@/lib/data/sim-data";
import { simHref } from "@/lib/routes";
import { pageTitle, shellProps } from "@/app/shell-props";
import { YourSimPage } from "./your-sim-page";

type Props = { params: Promise<{ season: string }> };

export function generateStaticParams(): { season: string }[] {
  return weekSimSeasons().map((season) => ({ season }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { season } = await params;
  return { title: pageTitle(undefined, `The Race ${season}`) };
}

export default async function SimRoute({ params }: Props) {
  const { season } = await params;
  // The route only builds a season with a week sim file, so the loader gives the file here.
  const sim = latestWeekSim(season)!;
  return (
    <>
      <TopBand {...shellProps()} pageHref={simHref(season)} />
      <div className="bg-page">
        <PageColumn>
          <YourSimPage sim={sim} avatars={latestAvatars(Number(season))} />
        </PageColumn>
      </div>
    </>
  );
}
