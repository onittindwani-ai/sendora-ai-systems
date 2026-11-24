import type { NextConfig } from "next";

const config: NextConfig = {
  transpilePackages: ["@sendora/ui-kit"],
  reactStrictMode: true,
};

export default config;
