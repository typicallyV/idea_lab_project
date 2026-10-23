import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Vercel's Next.js 16.3 adapter conflicts with standalone output tracing
  // during onBuildComplete. Keep standalone output for our Docker image only.
  output: process.env.VERCEL ? undefined : "standalone",
};

export default nextConfig;
