/**
 * The midseason report page: the top band, the chapter rail, the opener, then the three acts on one scroll.
 * The route of the app reads the midseason file and the shell values, and passes them in, so the screen reads no file.
 */
import type { ComponentProps, ReactNode } from "react";
import { PageColumn } from "@cpc/design/parts/page-column";
import { TopBand } from "@cpc/design/shell/top-band";
import type { Midseason } from "../schema/midseason-types";
import type { Avatars } from "./chapter-part";
import { ActRail } from "./act-rail";
import { ActSection } from "./act-section";
import { midseasonScene } from "./midseason-scene";
import { Opener } from "./opener";

/* The title, the brand, and the menu of the top band, as the app builds them for every page. */
type ShellValues = Pick<ComponentProps<typeof TopBand>, "title" | "brand" | "menu">;

/* The id of the finale at the end of the last act, where the app mounts the sim. */
const FINALE_ID = "sim";

export function MidseasonScreen({
  report,
  shell,
  pageHref,
  avatars = {},
  children,
}: {
  report: Midseason;
  shell: ShellValues;
  // The href of this page.
  pageHref: string;
  // The avatar of each team by roster id, with the base path, from the latest week. A team with none gets the default.
  avatars?: Avatars;
  // The finale at the end of the last act. The app mounts the sim replay here, so the report imports no sim.
  children?: ReactNode;
}) {
  const last = report.acts.length - 1;
  // The frame of the finale holds the id that "See the sim" in the opener jumps to. The rail sits under the top band,
  // so the jump leaves the height of the rail free above the sim, as a jump to an act does.
  const finale = children ? (
    <div id={FINALE_ID} className="scroll-mt-[calc(var(--spacing-touch)+1px)]">
      {children}
    </div>
  ) : undefined;
  return (
    <>
      <TopBand {...shell} pageHref={pageHref} />
      <div className="bg-page">
        <ActRail acts={report.acts} />
        <PageColumn>
          <div className="flex flex-col gap-sp-6 px-gutter pt-sp-4 pb-sp-6 tablet:px-0">
            <Opener
              opener={report.opener}
              season={report.season}
              week={report.week}
              scene={midseasonScene(report)}
              finaleHref={finale === undefined ? undefined : `#${FINALE_ID}`}
            />
            {report.acts.map((act, index) => (
              <ActSection
                key={act.key}
                act={act}
                index={index}
                avatars={avatars}
                finale={index === last ? finale : undefined}
              />
            ))}
          </div>
        </PageColumn>
      </div>
    </>
  );
}
