/**
 * Tests for the count script tag of the head. It renders only when the client sets usage_code.
 * They read the markup that the static export writes, not the props.
 */
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { UsageScript } from "./usage-script";

describe("UsageScript", () => {
  it("loads the count script with the count URL of the code when the client sets usage_code", () => {
    const html = renderToStaticMarkup(<UsageScript code="cpcfantasy" />);
    expect(html).toBe(
      '<script async="" data-goatcounter="https://cpcfantasy.goatcounter.com/count" src="https://gc.zgo.at/count.js"></script>',
    );
  });

  it("loads no count script when the client sets no usage_code", () => {
    expect(renderToStaticMarkup(<UsageScript code={null} />)).toBe("");
  });
});
