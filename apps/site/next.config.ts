/**
 * Next.js config for the static export that GitHub Pages serves.
 * Trailing slashes keep the URLs the same as the folder layout in `public/`.
 */
import type { NextConfig } from "next";
import { basePath } from "./src/lib/config";
import { managersRouteOn } from "./src/lib/data/manager-data";
import { waiverRouteOn } from "./src/lib/data/waiver-data";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  basePath,
  images: { unoptimized: true },
  // A static export fails on a dynamic route with no params, so a gated route file counts as a page only when its file exists.
  pageExtensions: [
    "tsx",
    "ts",
    "jsx",
    "js",
    ...(waiverRouteOn() ? ["waiver.tsx"] : []),
    ...(managersRouteOn() ? ["managers.tsx"] : []),
  ],
};

export default nextConfig;
