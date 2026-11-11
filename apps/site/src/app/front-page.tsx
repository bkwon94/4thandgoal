/**
 * The Front page of decision 08 at / while the front door is off: the intro, then the parts that each package gives.
 * It is a server component, so every part is in the static export. The registry lists only the packages of the client.
 */
import { Fragment } from "react";
import { TopBand } from "@cpc/design/shell/top-band";
import { PageColumn } from "@cpc/design/parts/page-column";
import { Rise } from "@cpc/design/parts/rise";
import { clientValues } from "@/generated/client-values";
import { homeBanners, homeSections, homeTools } from "@/generated/registry";
import type { HomePlace } from "@/lib/client-values";
import { season } from "@/lib/config";
import { homeHref } from "@/lib/routes";
import { shellProps } from "@/app/shell-props";
import { HomeChapter } from "@/app/home-chapter";

export default function FrontPage() {
  // Each package reads its data at build time. A package with no data gives no part, so the page shows no empty chapter.
  const sections = homeSections.flatMap((section) => section());
  const partsAt = (place: HomePlace) =>
    sections
      .filter((section) => section.place === place)
      .map((section, index) => <Fragment key={`${place}-${index}`}>{section.part}</Fragment>);
  const takeover = partsAt("takeover");
  return (
    <>
      {/* The intro names the season, so the top band holds no week line. */}
      <TopBand {...shellProps()} pageHref={homeHref()} />
      {/* The strip of each package under the top band, edge to edge, such as the egg banner after an egg drop. */}
      {homeBanners.map((Banner, index) => (
        <Banner key={index} />
      ))}
      {/* The page color fills the width under the band, so the cards sit on the page in both themes. */}
      <div className="bg-page">
        <PageColumn>
          {/* One scroll in the order of decision 08: the intro, the hero and its four numbers, Power Rankings, Tools,
              and Weekly Reports. The intro and the hero rise in on load. Each chapter below rises in as it enters the view. */}
          <div className="flex flex-col gap-sp-6 px-gutter pt-sp-4 pb-sp-6 tablet:px-0">
            <Rise step={0} className="flex flex-col gap-sp-1">
              <span className="font-mono text-meta leading-tight tracking-caps text-mute uppercase">
                {`${season} // ${clientValues.copy.tagline}`}
              </span>
              <h1 className="m-0 text-score leading-tight font-bold">{clientValues.copy.siteName}</h1>
            </Rise>
            {/* A takeover part, such as the midseason report, shows in place of the usual top. */}
            {takeover.length > 0 ? takeover : partsAt("top")}
            {partsAt("middle")}
            {homeTools.length > 0 && (
              <HomeChapter id="tools" title="Tools">
                {/* Two tiles per row, so the analyzer and the managers sit side by side on a phone too. */}
                <div className="grid grid-cols-2 gap-sp-2">
                  {/* The registry gives the tool of each package of the client, so an omitted package leaves no code here. */}
                  {homeTools.map((Tool, index) => (
                    <Tool key={index} />
                  ))}
                </div>
              </HomeChapter>
            )}
            {partsAt("bottom")}
          </div>
        </PageColumn>
      </div>
    </>
  );
}
