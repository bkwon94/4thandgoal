/**
 * The power rankings page: the masthead with the chosen week line and the table, or a short empty state with no file.
 * The route of the app reads the rankings file and the masthead values, and passes them in, so the screen reads no file.
 */
import type { ComponentProps } from "react";
import { Masthead } from "@cpc/design/shell/masthead";
import { PageColumn } from "@cpc/design/parts/page-column";
import { Blurb } from "@cpc/design/parts/blurb";
import { Chapter } from "@cpc/design/parts/chapter";
import { Label } from "@cpc/design/parts/label";
import type { Rankings } from "../schema/rankings-types";
import { PowerRankings } from "./power-rankings";
import { ChosenWeekLine, WeekChoiceProvider } from "./week-choice";

/* The title, the brand, and the menu of the masthead, as the app builds them for every page. */
type MastheadValues = Pick<ComponentProps<typeof Masthead>, "title" | "brand" | "menu">;

export function RankingsScreen({
  rankings,
  avatars,
  managersHref,
  masthead,
  pageHref,
}: {
  // Null when the pipeline has not written the rankings file yet.
  rankings: Rankings | null;
  avatars: Readonly<Record<string, string>>;
  managersHref: string | null;
  masthead: MastheadValues;
  // The href of this page, with the base path.
  pageHref: string;
}) {
  if (!rankings || rankings.weeks.length === 0) {
    return (
      <>
        <Masthead {...masthead} subtitle="Power Rankings" pageHref={pageHref} />
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
    // The provider holds the chosen week, so the masthead week line and the table read the same week.
    <WeekChoiceProvider weeks={rankings.weeks}>
      <Masthead {...masthead} subtitle="Power Rankings" pageHref={pageHref}>
        <ChosenWeekLine />
      </Masthead>
      <PageColumn>
        <PowerRankings weeks={rankings.weeks} avatars={avatars} managersHref={managersHref} />
      </PageColumn>
    </WeekChoiceProvider>
  );
}
