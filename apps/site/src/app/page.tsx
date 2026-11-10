/**
 * The home page at /: the front door. It asks for Your team, then shows the empty Thread with the ask box at its center.
 * It is a server component that reads the teams of the latest week, so the sheet ships in the static export.
 */
import type { Metadata } from "next";
import { TopBand } from "@cpc/design/shell/top-band";
import { clientValues } from "@/generated/client-values";
import { homeBanners } from "@/generated/registry";
import { loadFrontDoor } from "@/lib/data/front-door-data";
import { homeHref } from "@/lib/routes";
import { shellProps, pageTitle } from "@/app/shell-props";
import { FrontDoor } from "@/app/front-door/front-door";

export const metadata: Metadata = {
  title: pageTitle(),
};

export default function HomePage() {
  const door = loadFrontDoor();
  return (
    <>
      <TopBand {...shellProps()} pageHref={homeHref()} />
      {/* The strip of each package under the top band, edge to edge, such as the egg banner after an egg drop. */}
      {homeBanners.map((Banner, index) => (
        <Banner key={index} />
      ))}
      {/* The page color fills the width under the band in both themes. A client with no published week has no teams to
          pick from, so it shows the name of the league alone. */}
      <main className="bg-page">
        {door ? (
          <FrontDoor siteName={clientValues.copy.siteName} week={door.week} teams={door.teams} answers={door.answers} />
        ) : (
          <h1 className="m-0 px-gutter py-sp-6 text-score leading-tight font-bold">{clientValues.copy.siteName}</h1>
        )}
      </main>
    </>
  );
}
