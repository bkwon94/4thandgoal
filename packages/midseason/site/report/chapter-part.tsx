/**
 * The part of each chapter of the report, picked by the key of the chapter.
 * A chapter with no part of its own shows its title and its prose, so each act holds every chapter of the file.
 */
import { Arcs } from "../act-one/arcs";
import { Injuries } from "../act-one/injuries";
import { Luck } from "../act-one/luck";
import { State } from "../act-one/state";
import { Top10 } from "../act-one/top10";
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
    default:
      return <ReportChapter id={chapter.key} title={chapter.title} blurb={chapter.blurb} roast={chapter.roast} />;
  }
}
