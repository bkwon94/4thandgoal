/**
 * The page of the front door: at / with the flag front_door on, else at the hidden /ask/. It asks for Your team, then
 * shows the empty Thread with the ask box. A server component that reads the latest week, so the sheet ships in the export.
 */
import { TopBand } from "@cpc/design/shell/top-band";
import { clientValues } from "@/generated/client-values";
import { homeBanners } from "@/generated/registry";
import { loadFrontDoor } from "@/lib/data/front-door-data";
import { askTarget } from "@/lib/config";
import { homeHref } from "@/lib/routes";
import { shellProps } from "@/app/shell-props";
import { FrontDoor } from "@/app/front-door/front-door";
import { PassphraseRow } from "@/app/front-door/passphrase-row";

/* `pageHref` is the path of the page. The front door is Home, so the hidden /ask/ passes the Home path too, and the Home row shows the check. */
export default function FrontDoorPage({ pageHref = homeHref() }: { pageHref?: string }) {
  const door = loadFrontDoor();
  return (
    <>
      {/* The front door has its own foot, the Suggestions and the ask box, so the pages sit in the header sheet in place of
          the dock, and the week chip leaves: the Answers are about the live week (decision 10). */}
      {/* The header sheet holds a row that changes the league passphrase, which the front door asks for in a modal. */}
      <TopBand {...shellProps()} pageHref={pageHref} nav="sheet" sheetRows={door ? <PassphraseRow /> : undefined} />
      {/* The strip of each package under the top band, edge to edge, such as the egg banner after an egg drop. */}
      {homeBanners.map((Banner, index) => (
        <Banner key={index} />
      ))}
      {/* The page color fills the width under the band in both themes. A client with no published week has no teams to
          pick from, so it shows the name of the league alone. */}
      <main className="bg-page">
        {door ? (
          <FrontDoor siteName={clientValues.copy.siteName} week={door.week} teams={door.teams} answers={door.answers} personalHrefs={door.personalHrefs} askTarget={askTarget} />
        ) : (
          <h1 className="m-0 px-gutter py-sp-6 text-score leading-tight font-bold">{clientValues.copy.siteName}</h1>
        )}
      </main>
    </>
  );
}
