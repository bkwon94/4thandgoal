/**
 * Checks that the text block renders the marks of each sample text of the shared fixture text-marks.json.
 * The API test test_text_marks.py reads the same file, so a drift between the two parsers fails a test.
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { cleanup, render } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { TextBlock } from "./text-block";

type Case = {
  name: string;
  text: string;
  blocks: { tag: string; text: string }[];
  strong: string[];
  em: string[];
  li: string[];
};

// The path comes from this file and not from the working folder, because other tests point the working folder at a fixed copy.
const CASES: Case[] = JSON.parse(readFileSync(join(__dirname, "..", "..", "..", "..", "api", "tests", "fixtures", "text-marks.json"), "utf8"));

afterEach(cleanup);

describe("the text block over the shared text marks", () => {
  it.each(CASES)("$name", ({ text, blocks, strong, em, li }) => {
    const { container } = render(<TextBlock text={text} />);
    const root = container.querySelector("[data-text-block]")!;
    const texts = (selector: string) => [...root.querySelectorAll(selector)].map((node) => node.textContent);
    expect([...root.children].map((node) => ({ tag: node.tagName.toLowerCase(), text: node.textContent }))).toEqual(blocks);
    expect(texts("strong")).toEqual(strong);
    expect(texts("em")).toEqual(em);
    expect(texts("li")).toEqual(li);
    // Raw HTML and links stay as letters: no element beyond the marks reaches the page.
    expect(root.querySelectorAll("a, img, h1, h2, h3, table, script, b, i").length).toBe(0);
  });
});
