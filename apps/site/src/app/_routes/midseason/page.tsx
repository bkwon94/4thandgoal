/**
 * The midseason report at /midseason/<season>/, one static page per season with a published midseason file.
 * It reads the file, the avatars of the latest week, and the shell values, and the midseason package renders the page.
 * The app mounts the sim replay as the finale of the report, so neither package imports the other.
 */
import type { Metadata } from "next";
import { MidseasonScreen } from "@cpc/midseason/report/midseason-screen";
import { SimReplay } from "@cpc/sim/replay/sim-replay";
import { loadMidseason, midseasonSeasons } from "@/lib/data/midseason-data";
import { latestAvatars } from "@/lib/data/rankings-data";
import { loadSim } from "@/lib/data/sim-data";
import { midseasonHref } from "@/lib/routes";
import { pageTitle, shellProps } from "@/app/shell-props";

type Props = { params: Promise<{ season: string }> };

export function generateStaticParams(): { season: string }[] {
  return midseasonSeasons().map((season) => ({ season }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { season } = await params;
  return { title: pageTitle(undefined, `${season} Midseason Report`) };
}

export default async function MidseasonPage({ params }: Props) {
  const { season } = await params;
  // The route only builds a season with the file, so the loader gives the report here.
  const report = loadMidseason(season)!;
  const sim = loadSim(season);
  return (
    <MidseasonScreen
      report={report}
      shell={shellProps()}
      pageHref={midseasonHref(season)}
      avatars={latestAvatars(Number(season))}
    >
      {sim !== null && <SimReplay sim={sim} />}
    </MidseasonScreen>
  );
}
