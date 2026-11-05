/**
 * Tests of the root layout: the first paint that the static export ships. It renders the layout to the server markup,
 * as the export writes it, and reads the class on <html> and the boot script in the head.
 */
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { BOOT_SCRIPT } from "@cpc/design/lib/theme";
import RootLayout from "./layout";

const markup = renderToStaticMarkup(
  <RootLayout>
    <main>page</main>
  </RootLayout>,
);

describe("the root layout", () => {
  it("ships the dark class on <html>, so no choice and scripts off both paint dark (AT-1, AT-2)", () => {
    const classes = markup.match(/^<html[^>]*\sclass="([^"]*)"/)?.[1].split(" ");
    expect(classes).toContain("dark");
  });

  it("puts the boot script inline in the head, so a stored light choice applies before the body paints (AT-3)", () => {
    const head = markup.slice(markup.indexOf("<head>"), markup.indexOf("</head>"));
    expect(head).toContain(`<script>${BOOT_SCRIPT}</script>`);
  });
});
