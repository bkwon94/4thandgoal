/**
 * Next.js config for the static export that GitHub Pages serves.
 * Trailing slashes keep the URLs the same as the folder layout in `public/`.
 */
import type { NextConfig } from "next";
import { basePath } from "./src/lib/config";

// The client build writes the route files of each package of the client, so the config gates no route.
const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  basePath,
  images: { unoptimized: true },
  // Each package ships TSX source with no build step, so the site build compiles it.
  transpilePackages: ["@cpc/analyzer", "@cpc/design", "@cpc/league", "@cpc/waiver"],
};

export default nextConfig;
