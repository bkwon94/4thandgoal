/**
 * The part of each chapter of the report, picked by the key of the chapter.
 * A chapter with no part of its own shows its title and its prose, so each act holds every chapter of the file.
 */
import { Arcs } from "../act-one/arcs";
import { Injuries } from "../act-one/injuries";
import { Luck } from "../act-one/luck";
import { State } from "../act-one/state";
import { Top10 } from "../act-one/top10";
import { LookAhead } from "../act-three/look-ahead";
import { Watch } from "../act-three/watch";
import { Draft } from "../act-two/draft";
import { Lineup } from "../act-two/lineup";
import { Records } from "../act-two/records";
import { Trades } from "../act-two/trades";
import { Waivers } from "../act-two/waivers";
import type { MidseasonChapter } from "../schema/midseason-types";
import { ReportChapter } from "./report-chapter";

export function ChapterPart({ chapter }: { chapter: MidseasonChapter }) {
  switch (chapter.key) {
    case "state":
      return <State chapter={chapter} />;
    case "arcs":
      return <Arcs chapter={chapter} />;
    case "luck":
      return <Luck chapter={chapter} />;
    case "injuries":
      return <Injuries chapter={chapter} />;
    case "top10":
      return <Top10 chapter={chapter} />;
    case "draft":
      return <Draft chapter={chapter} />;
    case "waivers":
      return <Waivers chapter={chapter} />;
    case "trades":
      return <Trades chapter={chapter} />;
    case "lineup":
      return <Lineup chapter={chapter} />;
    case "records":
      return <Records chapter={chapter} />;
    case "look-ahead":
      return <LookAhead chapter={chapter} />;
    case "watch":
      return <Watch chapter={chapter} />;
    default: {
      // Each key of the schema has a part now, so TypeScript narrows this branch to never. A chapter that a later
      // schema adds still shows its title and its prose here until it gets a part.
      const other = chapter as MidseasonChapter;
      return <ReportChapter id={other.key} title={other.title} blurb={other.blurb} roast={other.roast} />;
    }
  }
}
