/**
 * The part of each chapter of the report, picked by the key of the chapter.
 * A chapter with no part of its own shows its title and its prose, so each act holds every chapter of the file.
 */
import { Arcs } from "../act-one/arcs";
import { Luck } from "../act-one/luck";
import { State } from "../act-one/state";
import { Top10 } from "../act-one/top10";
import { LookAhead } from "../act-three/look-ahead";
import { Draft } from "../act-two/draft";
import { QuickHits } from "../act-two/quick-hits";
import { Records } from "../act-two/records";
import { Trades } from "../act-two/trades";
import { Waivers } from "../act-two/waivers";
import type { MidseasonChapter } from "../schema/midseason-types";
import { ReportChapter } from "./report-chapter";

/* The avatar of each team by roster id, with the base path. The route of the app reads it from the latest week. */
export type Avatars = Readonly<Record<string, string>>;

export function ChapterPart({ chapter, avatars }: { chapter: MidseasonChapter; avatars: Avatars }) {
  switch (chapter.key) {
    case "state":
      return <State chapter={chapter} />;
    case "arcs":
      return <Arcs chapter={chapter} />;
    case "luck":
      return <Luck chapter={chapter} />;
    case "top10":
      return <Top10 chapter={chapter} />;
    case "draft":
      return <Draft chapter={chapter} />;
    case "waivers":
      return <Waivers chapter={chapter} />;
    case "trades":
      return <Trades chapter={chapter} />;
    case "records":
      return <Records chapter={chapter} avatars={avatars} />;
    case "quick-hits":
      return <QuickHits chapter={chapter} />;
    case "look-ahead":
      return <LookAhead chapter={chapter} />;
    default: {
      // Each key of the schema has a part now, so TypeScript narrows this branch to never. A chapter that a later
      // schema adds still shows its title and its prose here until it gets a part.
      const other = chapter as Exclude<MidseasonChapter, { key: "quick-hits" }>;
      return <ReportChapter id={other.key} title={other.title} blurb={other.blurb} />;
    }
  }
}
