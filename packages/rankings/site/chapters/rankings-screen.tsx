/**
 * The power rankings page: the top band, the chosen week line, and the table, or a short empty state with no file.
 * The route of the app reads the rankings file and the shell values, and passes them in, so the screen reads no file.
 */
import type { ComponentProps } from "react";
import { TopBand } from "@cpc/design/shell/top-band";
import { PageColumn } from "@cpc/design/parts/page-column";
import { Blurb } from "@cpc/design/parts/blurb";
import { Chapter } from "@cpc/design/parts/chapter";
import { Label } from "@cpc/design/parts/label";
import type { Rankings } from "../schema/rankings-types";
import { PowerRankings } from "./power-rankings";
import { ChosenWeekLine, WeekChoiceProvider } from "./week-choice";

/* The title, the brand, and the menu of the top band, as the app builds them for every page. */
type ShellValues = Pick<ComponentProps<typeof TopBand>, "title" | "brand" | "menu">;

export function RankingsScreen({
  rankings,
  avatars,
  managersHref,
  shell,
  pageHref,
}: {
  // Null when the pipeline has not written the rankings file yet.
  rankings: Rankings | null;
  avatars: Readonly<Record<string, string>>;
  managersHref: string | null;
  shell: ShellValues;
  // The href of this page, with the base path.
  pageHref: string;
}) {
  if (!rankings || rankings.weeks.length === 0) {
    return (
      <>
        <TopBand {...shell} pageHref={pageHref} />
        <PageColumn>
          <Chapter>
            <Label heading>Power Rankings</Label>
            <Blurb>No power rankings are published yet.</Blurb>
          </Chapter>
        </PageColumn>
      </>
    );
  }
  return (
    // The provider holds the chosen week, so the week line and the table read the same week.
    <WeekChoiceProvider weeks={rankings.weeks}>
      <TopBand {...shell} pageHref={pageHref}>
        <ChosenWeekLine />
      </TopBand>
      <PageColumn>
        <PowerRankings weeks={rankings.weeks} avatars={avatars} managersHref={managersHref} />
      </PageColumn>
    </WeekChoiceProvider>
  );
}
