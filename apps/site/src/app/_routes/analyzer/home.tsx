/**
 * The home tool of the analyzer package: the Trade Analyzer tile of the Tools chapter, and the teams prefetch.
 * The registry of the client build imports it only when the client takes analyzer.
 */
import { ArrowLeftRightIcon } from "lucide-react";
import { TeamsPrefetch } from "@cpc/analyzer/form/teams-prefetch";
import { HomeTile } from "@/app/home-tile";
import { apiTarget } from "@/lib/config";
import { analyzeHref } from "@/lib/routes";

export function HomeTool() {
  return (
    <>
      {/* A reader who opens the analyzer next sees the pickers at once, because the teams are already in session storage. */}
      <TeamsPrefetch target={apiTarget} />
      {/* The dock shows the same icon for the analyzer, so the tile and the dock item read as one place. */}
      <HomeTile
        href={analyzeHref()}
        icon={ArrowLeftRightIcon}
        name="Trade Analyzer"
        line="Grade a trade offer before you send it."
      />
    </>
  );
}
