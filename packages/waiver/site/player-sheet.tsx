/**
 * The sheet of the waiver page: the open player's name, his facts, his research claims, the bid to win, and the last like him.
 * A drop names the roster that holds him in place of a price. A line says when the research step found no experts this week.
 * With a team pick, a box counts the managers that can outbid the viewer.
 */
"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { Blurb } from "@cpc/design/parts/blurb";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { DURATION, rise } from "@cpc/design/lib/motion";
import { cn } from "@cpc/design/lib/utils";
import type { TeamNames, WaiverPlayer } from "./types";
import { beatenLine, holderLine, STANCE, teamName, trendingLine, waiverMetaLine } from "./format";

/* One box of the bid row: a small caps name, a big number, and the line that explains it. The hot box is the bid to win. */
function BidBox({ name, value, hot, children }: { name: string; value: string; hot?: boolean; children: ReactNode }) {
  return (
    <div className={cn("flex-1 rounded-card px-sp-3 py-sp-2", hot ? "bg-accent" : "bg-chip-dark")}>
      <div className="text-label leading-tight tracking-caps text-on-dark-muted uppercase">{name}</div>
      <div className="text-stat leading-stat font-extrabold tabular-nums">{value}</div>
      <div className="mt-sp-0 text-meta leading-tight text-on-dark-2">{children}</div>
    </div>
  );
}

export function PlayerSheet({
  player,
  teams,
  expertsMissing,
  viewerBudget,
}: {
  player: WaiverPlayer | null;
  teams: TeamNames;
  expertsMissing: boolean;
  // The budget left of the picked team, or null with no pick.
  viewerBudget: number | null;
}) {
  const off = useMotionOff();
  const facts = player?.facts ?? [];
  const research = player?.research ?? [];
  const drop = player?.drop ?? null;
  const trending = player ? trendingLine(player) : null;
  const price = player?.price ?? null;
  const last = price?.last_like ?? null;
  // The pipeline keys the map by budget level as a string. It already leaves the viewer out of the count, so the site only looks it up.
  const outbid = price && viewerBudget !== null ? price.outbid[String(viewerBudget)] : undefined;
  // The engine counts the managers over the lower of the bid and the viewer's budget, so the line names that amount.
  const outbidOver = price && viewerBudget !== null ? Math.min(price.bid, viewerBudget) : null;
  // The sheet is a black card. The dark theme turns ink into a text color, so ink would paint it white.
  return (
    <section aria-label="Player sheet" className="mt-sp-3 rounded-card border border-rule-dark bg-card-band px-sp-4 py-sp-3">
      {/* A screen reader reads this one short line after a tap, and not the whole sheet. */}
      <p aria-live="polite" className="sr-only">
        {player ? `Sheet: ${player.name}` : ""}
      </p>
      {player && (
        // The key changes with the player, so a new player rises in once. The old one leaves at once, so a fast tap never waits.
        <motion.div key={player.player_id} data-reveal {...rise(off, { duration: DURATION.page })}>
          <h2 className="m-0 text-lead leading-tight font-extrabold tracking-snug">{player.name}</h2>
          <div className="mt-sp-0 text-meta text-on-dark-muted tabular-nums">{waiverMetaLine(player)}</div>
          {drop && (
            <>
              <div className="mt-sp-1 text-meta font-bold text-accent-text">{holderLine(drop)}</div>
              <div className="mt-sp-1 text-meta text-on-dark-2 tabular-nums">{beatenLine(drop)}</div>
            </>
          )}
          {trending && <div className="mt-sp-1 text-meta text-on-dark-2 tabular-nums">{trending}</div>}
          {facts.length > 0 && (
            <ul aria-label="Facts" className="m-0 mt-sp-2 list-none space-y-sp-1 p-0">
              {facts.map((fact) => (
                <li key={fact.id}>
                  <Blurb dark className="text-meta leading-body">
                    {fact.text}
                  </Blurb>
                </li>
              ))}
            </ul>
          )}
          {research.length > 0 && (
            <ul aria-label="Claims" className="m-0 mt-sp-3 list-none space-y-sp-2 border-t border-rule-dark p-0 pt-sp-2">
              {research.map((claim) => (
                <li key={claim.url} className="text-meta leading-body">
                  {/* A claim opens its source in a new tab, so the reader keeps the page and the open player. */}
                  <a href={claim.url} target="_blank" rel="noopener noreferrer" className="text-on-dark underline decoration-mute underline-offset-2">
                    {claim.text}
                  </a>
                  <div className="text-label tracking-caps text-on-dark-muted uppercase">{`${claim.source} · ${STANCE[claim.stance]}`}</div>
                </li>
              ))}
            </ul>
          )}
          {price && (
            <div className="mt-sp-3 flex items-stretch gap-sp-2">
              <BidBox name="Bid to win" value={`$${price.bid}`} hot>
                {price.fact.text}
              </BidBox>
              {last && (
                <BidBox name={`Last ${player.position} won`} value={`$${last.bid}`}>
                  {`${last.name}, week ${last.week}, ${teamName(teams, last.roster_id)}`}
                </BidBox>
              )}
              {outbid !== undefined && (
                <BidBox name="Can outbid you" value={String(outbid)}>
                  {`Managers over $${outbidOver}`}
                </BidBox>
              )}
            </div>
          )}
        </motion.div>
      )}
      {expertsMissing && <p className="m-0 mt-sp-3 text-meta text-on-dark-muted italic">The experts are out this week.</p>}
    </section>
  );
}
