/**
 * Next.js config for the static export that the Cloudflare Worker of each client serves.
 * Trailing slashes keep the URLs the same as the folder layout in `public/`.
 */
import type { NextConfig } from "next";

// The client build writes the route files of each package of the client, so the config gates no route.
const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  // Each package ships TSX source with no build step, so the site build compiles it.
  transpilePackages: ["@cpc/analyzer", "@cpc/design", "@cpc/league", "@cpc/managers", "@cpc/midseason", "@cpc/rankings", "@cpc/waiver", "@cpc/week"],
};

export default nextConfig;
