/**
 * The home page at /: the tools, the top of the power rankings, and every published week, newest first, read from each week's page.json.
 * It is a server component, so the list is part of the static export. Each tool and chapter comes from the registry, so an omitted package ships no code.
 */
import type { Metadata } from "next";
import { Fragment } from "react";
import { Masthead, WeekLine } from "@cpc/design/shell/masthead";
import { PageColumn } from "@cpc/design/parts/page-column";
import { Chapter } from "@cpc/design/parts/chapter";
import { Label } from "@cpc/design/parts/label";
import { season } from "@/lib/config";
import { homeHref } from "@/lib/routes";
import { cn } from "@cpc/design/lib/utils";
import { homeSections, homeTools } from "@/generated/registry";
import { mastheadProps } from "@/app/masthead-props";

export const metadata: Metadata = {
  title: "Cornerstone Fantasy Football League",
};

export default function HomePage() {
  // Each package reads its data at build time. A package with no data gives null, so the page shows no empty chapter.
  const sections = homeSections.map((section) => section()).filter((section) => section !== null);
  const beside = sections.filter((section) => section.place === "beside");
  const below = sections.filter((section) => section.place === "below");
  // The top row holds the Tools chapter, when a package gives a tool, and each chapter beside it. Each chapter of the row
  // takes the next stagger step, and the chapters below start one step after the row.
  const toolsChapter = homeTools.length > 0 ? 1 : 0;
  const topCount = toolsChapter + beside.length;
  return (
    <>
      <Masthead {...mastheadProps()} pageHref={homeHref()}>
        <WeekLine label="SEASON" number={season} />
      </Masthead>
      <PageColumn>
        {/* The Tools chapter holds the analyzer row and the managers row, and the Power Rankings chapter holds one tall row,
            so side by side they fill the column.
            The row is one child of the main, so the main's card gap sits above and below it. On a phone the row is a plain
            block, so the chapters stack with the chapter rule. With no rankings file the grid has one column, so the Tools
            chapter takes the full width and the row has no empty half. */}
        {topCount > 0 && (
          <div className={cn("tablet:grid tablet:gap-card-gap", topCount > 1 ? "tablet:grid-cols-2" : "tablet:grid-cols-1")}>
            {/* The masthead and the label show at once. Each row reveals as it enters the view. */}
            {homeTools.length > 0 && (
              <Chapter>
                <Label heading>Tools</Label>
                {/* The registry gives the tool of each package of the client, so an omitted package leaves no code here. */}
                {homeTools.map((Tool, index) => (
                  <Tool key={index} first={index === 0} />
                ))}
              </Chapter>
            )}
            {beside.map((section, index) => (
              <Fragment key={index}>{section.chapter(toolsChapter + index)}</Fragment>
            ))}
          </div>
        )}
        {below.map((section, index) => (
          <Fragment key={index}>{section.chapter(topCount)}</Fragment>
        ))}
      </PageColumn>
    </>
  );
}
