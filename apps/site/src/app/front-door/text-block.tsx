/**
 * The text block: the text of every Answer, with a small set of markdown marks (decision 09). Bold, italic, bullet
 * lists, numbered lists, and paragraphs render as marks. Every other mark shows as plain text.
 */
import { Fragment, type ReactNode } from "react";

/* One run of words inside a paragraph or a list item, with its mark. */
export type TextRun = { mark: "plain" | "bold" | "italic"; text: string };

/* One part of the text: a paragraph, or a list whose items are runs. A numbered list keeps the number of its first item. */
export type TextPart =
  | { kind: "paragraph"; runs: TextRun[] }
  | { kind: "bullets"; items: TextRun[][] }
  | { kind: "numbers"; start: number; items: TextRun[][] };

const BULLET = /^\s*[-*+]\s+(.*)$/;
const NUMBER = /^\s*(\d+)[.)]\s+(.*)$/;
/* Bold is `**x**` or `__x__`, italic is `*x*` or `_x_`. An underscore inside a word, as in a snake_case name, is no mark.
   A mark never starts or ends on a space, so "5 * 3 * 2" stays plain. */
const INLINE = /\*\*(?=\S)(.+?)(?<=\S)\*\*|__(?=\S)(.+?)(?<=\S)__|\*(?=\S)(.+?)(?<=\S)\*|(?<!\w)_(?=\S)(.+?)(?<=\S)_(?!\w)/g;

/* The runs of one line or one list item. */
function runsOf(line: string): TextRun[] {
  const runs: TextRun[] = [];
  let at = 0;
  for (const match of line.matchAll(INLINE)) {
    if (match.index > at) runs.push({ mark: "plain", text: line.slice(at, match.index) });
    const bold = match[1] ?? match[2];
    runs.push(bold !== undefined ? { mark: "bold", text: bold } : { mark: "italic", text: (match[3] ?? match[4])! });
    at = match.index + match[0].length;
  }
  if (at < line.length) runs.push({ mark: "plain", text: line.slice(at) });
  return runs;
}

/* The parts of a text. A blank line ends a paragraph. The lines of one paragraph join with a space, as HTML shows them.
   A link, an image, a heading, raw HTML, or a table has no part of its own, so it stays in its paragraph as plain text. */
export function textParts(text: string): TextPart[] {
  const parts: TextPart[] = [];
  let lines: string[] = [];
  const endParagraph = () => {
    if (lines.length > 0) parts.push({ kind: "paragraph", runs: runsOf(lines.join(" ")) });
    lines = [];
  };
  for (const line of text.split("\n")) {
    const bullet = BULLET.exec(line);
    const number = bullet ? null : NUMBER.exec(line);
    if (bullet || number) endParagraph();
    // The part before this line, once a paragraph that it ends is in.
    const last = parts.at(-1);
    if (bullet) {
      if (last?.kind === "bullets") last.items.push(runsOf(bullet[1]));
      else parts.push({ kind: "bullets", items: [runsOf(bullet[1])] });
    } else if (number) {
      if (last?.kind === "numbers") last.items.push(runsOf(number[2]));
      else parts.push({ kind: "numbers", start: Number(number[1]), items: [runsOf(number[2])] });
    } else if (line.trim() === "") {
      endParagraph();
      // A blank line also ends a list, so the next list starts fresh.
      parts.push({ kind: "paragraph", runs: [] });
    } else {
      lines.push(line.trim());
    }
  }
  endParagraph();
  return parts.filter((part) => part.kind !== "paragraph" || part.runs.length > 0);
}

/* The words of a run, each with the space after it, and the space before the first word on its own. */
const tokensOf = (text: string) => text.match(/^\s+|\S+\s*/g) ?? [];

/* The count of words of a text as the text block shows it, so a caller can give each word its own delay. */
export function textWords(text: string): number {
  return textParts(text)
    .flatMap((part) => (part.kind === "paragraph" ? [part.runs] : part.items))
    .flat()
    .reduce((count, run) => count + tokensOf(run.text).filter((token) => token.trim()).length, 0);
}

/* The text block. Each word goes through `word` with its index in the whole text, so a live Answer can sweep its words
   in one by one. With no `word`, each run shows as it is. Only p, ul, ol, li, strong, em, and the spans of `word` reach
   the page. React escapes every text, so raw HTML in the text shows as its letters. */
export function TextBlock({ text, className = "", word }: { text: string; className?: string; word?: (word: string, index: number) => ReactNode }) {
  let index = 0;
  const show = (run: TextRun, key: number) => {
    const body = word
      ? tokensOf(run.text).map((token, at) => (token.trim() ? <Fragment key={at}>{word(token, index++)}</Fragment> : token))
      : run.text;
    if (run.mark === "bold") return <strong key={key} className="font-semibold text-ink">{body}</strong>;
    if (run.mark === "italic") return <em key={key}>{body}</em>;
    return <span key={key}>{body}</span>;
  };
  const line = (runs: TextRun[]) => runs.map(show);
  return (
    <div data-text-block="" className={`flex flex-col gap-sp-3 text-body leading-body ${className}`}>
      {textParts(text).map((part, key) => {
        if (part.kind === "paragraph") return <p key={key} className="m-0">{line(part.runs)}</p>;
        const items = part.items.map((runs, at) => (
          <li key={at} className="pl-sp-1">
            {line(runs)}
          </li>
        ));
        // The markers sit in the mute ink, so the words of each item lead.
        return part.kind === "bullets" ? (
          <ul key={key} className="m-0 flex list-disc flex-col gap-sp-1 pl-sp-5 marker:text-mute">
            {items}
          </ul>
        ) : (
          <ol key={key} start={part.start === 1 ? undefined : part.start} className="m-0 flex list-decimal flex-col gap-sp-1 pl-sp-5 marker:text-mute marker:tabular-nums">
            {items}
          </ol>
        );
      })}
    </div>
  );
}
