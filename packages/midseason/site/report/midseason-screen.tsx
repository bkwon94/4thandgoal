/**
 * The midseason report page: the top band, the chapter rail, the opener, then the three acts on one scroll.
 * The route of the app reads the midseason file and the shell values, and passes them in, so the screen reads no file.
 */
import type { ComponentProps, ReactNode } from "react";
import { PageColumn } from "@cpc/design/parts/page-column";
import { TopBand } from "@cpc/design/shell/top-band";
import type { Midseason } from "../schema/midseason-types";
import { ActRail } from "./act-rail";
import { ActSection } from "./act-section";
import { Opener } from "./opener";

/* The title, the brand, and the menu of the top band, as the app builds them for every page. */
type ShellValues = Pick<ComponentProps<typeof TopBand>, "title" | "brand" | "menu">;

export function MidseasonScreen({
  report,
  shell,
  pageHref,
  children,
}: {
  report: Midseason;
  shell: ShellValues;
  // The href of this page.
  pageHref: string;
  // The finale at the end of the last act. The app mounts the sim replay here, so the report imports no sim.
  children?: ReactNode;
}) {
  const last = report.acts.length - 1;
  return (
    <>
      <TopBand {...shell} pageHref={pageHref} />
      <div className="bg-page">
        <ActRail acts={report.acts} />
        <PageColumn>
          <div className="flex flex-col gap-sp-6 px-gutter pt-sp-4 pb-sp-6 tablet:px-0">
            <Opener opener={report.opener} season={report.season} week={report.week} />
            {report.acts.map((act, index) => (
              <ActSection key={act.key} act={act} index={index} finale={index === last ? children : undefined} />
            ))}
          </div>
        </PageColumn>
      </div>
    </>
  );
}
