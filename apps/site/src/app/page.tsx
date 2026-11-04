/**
 * The home page at /: the tools, the top of the power rankings, and every published week, newest first, read from each week's page.json.
 * It is a server component, so the list is part of the static export. Each section comes from the registry, so an omitted package ships no code.
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
import type { HomeSection } from "@/lib/client-values";
import { homeSections } from "@/generated/registry";
import { mastheadProps } from "@/app/masthead-props";

export const metadata: Metadata = {
  title: "Cornerstone Fantasy Football League",
};

type ToolRow = Extract<HomeSection, { place: "tools" }>;
type HomeChapter = Extract<HomeSection, { chapter: unknown }>;

export default function HomePage() {
  // Each package reads its data at build time. A package with no data gives null, so the page shows no empty section.
  const sections = homeSections.map((section) => section()).filter((section) => section !== null);
  const tools = sections.filter((section): section is ToolRow => section.place === "tools");
  const beside = sections.filter((section): section is HomeChapter => section.place === "beside");
  const below = sections.filter((section): section is HomeChapter => section.place === "below");
  // The top row holds the Tools chapter, when a package gives a tool, and each chapter beside it. Each chapter of the row
  // takes the next stagger step, and the chapters below start one step after the row.
  const toolsChapter = tools.length > 0 ? 1 : 0;
  const topCount = toolsChapter + beside.length;
  return (
    <>
      {/* The heads come first, so the masthead keeps its place in the tree for each client. */}
      {sections.map((section, index) => (
        <Fragment key={index}>{section.head}</Fragment>
      ))}
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
            {tools.length > 0 && (
              <Chapter>
                <Label heading>Tools</Label>
                {tools.map((section, index) => (
                  <Fragment key={index}>{section.row(index === 0)}</Fragment>
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
