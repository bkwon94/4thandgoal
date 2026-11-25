/**
 * The page of the front door: at / with the flag front_door on, else at the hidden /ask/. It asks for Your team, then
 * shows the empty Thread with the ask box. A server component that reads the latest week, so the sheet ships in the export.
 */
import { TopBand } from "@cpc/design/shell/top-band";
import { clientValues } from "@/generated/client-values";
import { homeBanners, menuLinks } from "@/generated/registry";
import { loadFrontDoor } from "@/lib/data/front-door-data";
import { askTarget } from "@/lib/config";
import { homeHref } from "@/lib/routes";
import { shellProps } from "@/app/shell-props";
import { clientSitePages } from "@/app/site-pages";
import { FrontDoor } from "@/app/front-door/front-door";
import { TourButton, TourRow } from "@/app/front-door/tour-replay";
import { SimLinkProvider } from "@/app/front-door/sim-link";

/* `pageHref` is the path of the page. The front door is Home, so the hidden /ask/ passes the Home path too, and the Home row shows the check. */
export default function FrontDoorPage({ pageHref = homeHref() }: { pageHref?: string }) {
  const door = loadFrontDoor();
  const shell = shellProps();
  return (
    <>
      {/* Only the front door has a Tour, so only it passes the replay controls into the shell. The "?" sits last, beside
          the theme button. */}
      <TopBand
        {...shell}
        pageHref={pageHref}
        actions={
          door ? (
            <>
              {shell.actions}
              <TourButton />
            </>
          ) : (
            shell.actions
          )
        }
        menuFoot={door ? <TourRow /> : undefined}
      />
      {/* The strip of each package under the top band, edge to edge, such as the egg banner after an egg drop. */}
      {homeBanners.map((Banner, index) => (
        <Banner key={index} />
      ))}
      {/* The page color fills the width under the band in both themes. A client with no published week has no teams to
          pick from, so it shows the name of the league alone. */}
      <main className="bg-page">
        {door ? (
          // The Menu link of the sim gives the link of the standings ladder, so it opens the same page as the Menu.
          <SimLinkProvider href={menuLinks.sim?.()?.href ?? null}>
            <FrontDoor
              siteName={clientValues.copy.siteName}
              week={door.week}
              teams={door.teams}
              answers={door.answers}
              personalHrefs={door.personalHrefs}
              pages={clientSitePages()}
              askTarget={askTarget}
              tradesClosed={clientValues.tradesClosed}
            />
          </SimLinkProvider>
        ) : (
          <h1 className="px-gutter py-sp-6 text-score m-0 leading-tight font-bold">
            {clientValues.copy.siteName}
          </h1>
        )}
      </main>
    </>
  );
}
