/**
 * The home tool of the analyzer package: the Trade Analyzer row of the Tools chapter, and the teams prefetch.
 * The registry of the client build imports it only when the client takes analyzer.
 */
import { Reveal } from "@cpc/design/parts/reveal";
import { stagger } from "@cpc/design/lib/motion";
import { TeamsPrefetch } from "@cpc/analyzer/form/teams-prefetch";
import { HomeRow } from "@/app/home-row";
import { apiTarget } from "@/lib/config";
import { analyzeHref } from "@/lib/routes";

export function HomeTool({ first }: { first: boolean }) {
  return (
    <>
      {/* A reader who opens the analyzer next sees the pickers at once, because the teams are already in session storage. */}
      <TeamsPrefetch target={apiTarget} />
      {/* The row reveals first, so a new week never pushes it down or delays it. */}
      <Reveal delay={stagger(0)}>
        <HomeRow href={analyzeHref()} first={first}>
          <b className="mb-sp-1 block text-lead leading-tight group-hover:text-accent-ink">Trade Analyzer</b>
          <span className="block text-meta text-mute">Grade a trade offer before you send it.</span>
          <span className="block text-meta text-mute">League passphrase needed.</span>
        </HomeRow>
      </Reveal>
    </>
  );
}
